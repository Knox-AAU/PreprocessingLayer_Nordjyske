import configparser
import string
from datetime import datetime, timezone
from os import environ
from xml.dom import minidom
import re

from alto_segment_lib.segment import SegmentType
from crawler.file import File
from knox_source_data_io.models.publication import Article
from pytesseract import pytesseract
from alto_segment_lib.segment_module import SegmentModule
from ocr.tesseract import TesseractModule
environ["OPENCV_IO_ENABLE_JASPER"] = "true"
import cv2


class OCRRunner:

    def run_ocr(self, file: File, language='dan', tesseract_path=None):
        """
        Runs everything that's needed to do OCR. It does the following: segmentation, creating articles, and
        turning articles into publications
        @param file: given file to perform OCR on
        @param language: optional parameter to change the language used by Tesseract
        @param tesseract_path: optional parameter to specify Tesseract installation if its not found in PATH
        @return: publication with the articles in the file
        """
        image = cv2.imread(file.path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        segments = SegmentModule.run_segmentation(file.path)

        tessdata = "dan"

        file_date = self.__find_year(file.name)

        # 19280517 = 1928-05-17
        if int(file_date) < 19280517:
            tessdata = "gothic_fine_tune"

        article = Article()
        articles = []
        for segment in segments:
            # If there is over 300 segments then we can safely say that it contains adverts or stock markets
            if len(segments) > 300:
                break

            if segment.y1 <= segment.y2 and segment.x1 <= segment.x2:
                # Crops the image based on the segment
                cropped_image = image[segment.y1:segment.y2+1, segment.x1:segment.x2+1]
            else:
                continue

            if segment.type == SegmentType.heading:
                # When there is a headline we know that its the start of a new article
                # So we save the old article and create a new one
                articles.append(article)
                article = Article()
                article.page = self.__find_page_number(file.path)
                headline = TesseractModule.from_file(cropped_image, tessdata).to_paragraphs()
                if len(headline) > 0:
                    article.headline = headline[0].value

            if segment.type == SegmentType.paragraph:
                # If the segment is a paragraph we will extract text with tesseract, remove adverts
                # and add file path to the article
                paragraphs = TesseractModule.from_file(cropped_image, tessdata).to_paragraphs()
                paragraphs = self.__remove_advertisement_and_junk(paragraphs)
                if len(paragraphs) > 0:
                    [article.add_paragraph(p) for p in paragraphs]
                    article.add_extracted_from(file.path)

            if segment.type == "subhead":
                # If the segment is a subheader then add it to the subeheader attribute in the article
                subhead = TesseractModule.from_file(cropped_image, tessdata).to_paragraphs()
                if len(subhead) > 0:
                    article.subhead = subhead[0].value

            if segment.type == "lead":
                # If the segment is a lead then add it to the lead attribute in the article
                lead = TesseractModule.from_file(cropped_image, tessdata).to_paragraphs()
                if len(lead) > 0:
                    article.lead = lead[0].value
        # Finds the page number if not already found
        if article.page == 0:
            article.page = self.__find_page_number(file.path)

        articles.append(article)

        # Takes all articles found and converts them into a single publication
        publication = self.__convert_articles_into_publication(articles, file)

        return publication

    def __convert_articles_into_publication(self, articles, file):
        """
        Converts articles into publications and finds the following for the publication:
        publication (name), publisher, published_at, and removes empty paragraphs
        @param articles: list of articles to turn into publication
        @param file: file object of the file that has been ran through OCR
        @return: publication with all articles
        """
        # Reads the name of publisher from config file
        config = configparser.ConfigParser()
        config.read('publication_default.ini')

        publication = TesseractModule.from_articles_to_publication(articles)
        publication.publication = self.__find_publication(file.name)
        publication.publisher = config['publisher']['name']
        publication.published_at = self.__find_published_at(file.path)
        publication = self.__remove_empty_paragraphs(publication)

        return publication

    @staticmethod
    def __find_publication(file_name):
        """
        Finds publisher name from file name
        @param file_name: name of file
        @return: publisher name
        """
        # todo bliver ikke sat mellemrum men ved ikke om det er vigtigt
        return file_name.split("-")[0].title()

    @staticmethod
    def __find_page_number(file_path):
        """
        Finds page number from alto.xml file
        @param file_path: name of file
        @return: page number
        """
        page_elements = minidom.parse(file_path.split('.')[0] + ".alto.xml").getElementsByTagName("Page")

        return int(page_elements[0].attributes['PHYSICAL_IMG_NR'].value)

    @staticmethod
    def __find_published_at(file_path):
        """
        Find when the newspaper was published
        @param file_path: path to the file
        @return: datetime object of when paper was published
        """
        # Opens the corresponding alto.xml file to find the published_at date
        published_at = minidom.parse(file_path.split('.')[0] + ".alto.xml").\
            getElementsByTagName("fileName")[0].firstChild.data

        # Uses regular expression to find the data in the file name
        pattern = re.compile("\\d\\d\\d\\d-\\d\\d-\\d\\d")
        result = pattern.search(published_at)
        result = result.group(0)

        # Makes datetime object from the date found with RE
        if re.match(pattern, result):
            return datetime(year=int(result[0:4]), month=int(result[5:7]), day=int(result[8:10]), tzinfo=timezone.utc)\
                .isoformat()

    @staticmethod
    def __remove_advertisement_and_junk(paragraphs):
        """
        Finds articles where the text is either half full with numbers or a quarter full with special characters
        and removes the article to avoid junk in the output
        @param paragraphs: paragraphs to search through
        @return: paragraphs that does not contain junk
        """
        # If text contains a lot of numbers it might be a TV guide or "aktier"
        ok_paragraphs = []
        special_chars = set(string.punctuation.replace("_", ""))

        # Loops through all paragraphs and checks if they have more than half numbers, or a third special
        # characters/numbers or contains a quarter of special characters
        for paragraph in paragraphs:
            num_counter = 0
            special_char_counter = 0
            total_char_count = 0

            total_char_count += len(paragraph.value.strip())
            words = paragraph.value.split(" ")
            # Counts all the characters in the words and sees if they are numbers or special characters
            for word in words:
                num_counter += sum(char.isdigit() for char in word)
                special_char_counter += sum(char in special_chars for char in word)

            if not (special_char_counter > total_char_count/4 or num_counter > total_char_count/2
                    or special_char_counter + num_counter > total_char_count/3):
                ok_paragraphs.append(paragraph)

        return ok_paragraphs

    @staticmethod
    def __remove_empty_paragraphs(publication):
        """
        Removes all articles in a publication that does not contain text
        @param publication: publication with articles to check
        @return: publication without empty paragraphs
        """
        correct_paragraphs = []
        for article in publication.articles:
            paragraphs = article.paragraphs

            for paragraph in paragraphs:
                if len(paragraph.value) > 0:
                    correct_paragraphs.append(paragraph)

            article.paragraphs = correct_paragraphs

        return publication

    def __find_year(self, file_name):
        """
        Finds the year of the file with regular expression
        @param file_name: name of file
        @return: file date in format: YYYYMMDD
        """
        pattern = re.compile("\\d\\d\\d\\d-\\d\\d-\\d\\d")
        result = pattern.search(file_name)
        file_date = result.group(0)
        file_date = file_date.replace("-", "")
        return file_date
