import re
from datetime import datetime, timezone
import pytesseract
from knox_source_data_io.models.publication import Publication, Article, Paragraph


class TesseractModule:
    """
    Used to handle all Tesseract related tasks.
    """

                                              # CHANGE THIS (PATH) BELOW
    def __init__(self, image, language='dan', tesseract_path='C:\Program Files\Tesseract-OCR\\tesseract.exe'):
        """
        Instantiates an instance of the class and extracts the text from the provided image using Tesseract.

        @param image: the image to extract the text from.
        @param language: the language model to use for the text extraction.
        @param tesseract_path: path to Tesseract (only necessary in case of incorrect setup).
        """

        if tesseract_path is not None:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        try:
            self.data = pytesseract.image_to_data(image, lang=language, output_type='dict', config="--psm 4")
        except Exception as e:
            print("[ERROR] Tesseract has run into a problem: " + str(e))
            # ToDo: handle the exception


    @classmethod
    def from_file(cls, image, tessdata: str):
        """
        Instantiates the class from a file and uses Tesseract to retrieve the text from it.

        @param image: the image to instantiate the class from.
        @param tessdata: the language model to use for the text extraction.
        @return: the instantiated class.
        """

        tm = cls(image, tessdata)
        return tm

    @staticmethod
    def from_articles_to_publication(articles):
        """
        Converts list of articles to publication.

        @param articles: the list of articles to convert.
        @return: the resulting Publication.
        """
        pub = Publication()
        pub.publication = ""
        pub.published_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
        [pub.add_article(article) for article in articles]

        return pub

    def to_publication(self):
        """
        Converts the data retrieved using Tesseract to a publication.

        @return: the resulting Publication.
        """
        pub = Publication()
        pub.publication = ""
        pub.published_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
        pub.add_article(self.to_article())

        return pub

    def to_article(self):
        """
        Converts the data retrieved using Tesseract to an Article.

        @return: the resulting Article.
        """
        # todo find byline, confidence
        article = Article()
        [article.add_paragraph(p) for p in self.to_paragraphs()]
        return article

    def to_text(self):
        """
        Converts the data retrieved using Tesseract to a string.

        @return: the resulting string.
        """
        b_str = ""
        for t in self.data['text']:
            b_str += f"{t} "
        return b_str.strip()

    def to_paragraphs(self):
        """
        Converts the data retrieved using Tesseract to a list of paragraphs.

        @return: the resulting list of paragraphs.
        """
        text = self.data['text']

        paragraphs = []
        b_str = ""
        for t in text:
            if t == "":
                if len(b_str) > 1 and (b_str[-1] == "\n" or b_str[-1] == "\r"):
                    # If last char was new line as well, then split into paragraph
                    paragraphs.append(b_str.strip())
                    b_str = ""
                else:
                    # Empty string = new line
                    b_str += "\n\r"
            else:
                b_str += f"{t} "
        if b_str != "":
            paragraphs.append(b_str)

        # Remove empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p != '']

        # Remove new lines and hyphens across them.
        paragraphs = [self.remove_hyphens_and_nl_cr(p) for p in paragraphs]

        paragraphs = [self.str_to_paragraph(p) for p in paragraphs]

        return paragraphs

    @staticmethod
    def str_to_paragraph(p):
        """
        Creates paragraph from string.

        @param p: the string to create the paragraph from.
        @return: the created paragraph.
        """
        paragraph = Paragraph()
        paragraph.kind = "paragraph"
        paragraph.value = p
        return paragraph

    @staticmethod
    def remove_hyphens_and_nl_cr(p):
        """
        Removes hyphens and newline characters and dashes placed right before them.

        @param p: the string to clean.
        @return: the cleaned string.
        """

        p = p.replace("- \n", "")
        p = p.replace("- \r", "")
        p = p.replace("\n", "")
        p = p.replace("\r", "")
        return p

    def text_conf_matches_from_tesseract_data(self):
        """
        Generates a list of tuples of text and its associated confidence score.

        @return: list of text, confidence tuples.
        """
        return [[text, conf] for text, conf in zip(self.data['text'], self.data['conf']) if conf != "-1"]

    def get_average_conf(self):
        """
        Gets the average of the confidence score.

        @return: A float with the average confidence score.
        """
        confidences = [int(x) for x in self.data['conf'] if 0 <= int(x) <= 100]

        # Avoid divide by zero
        if len(confidences) == 0:
            return 0
        return sum(confidences) / len(confidences)
