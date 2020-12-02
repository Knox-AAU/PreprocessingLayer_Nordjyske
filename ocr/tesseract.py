import re
from datetime import datetime
import cv2
import pytesseract
from knox_source_data_io.models.publication import Publication, Article, Paragraph
from crawler.file import File


class TesseractModule:

    def __init__(self, image, language='dan', tesseract_path=None):
        if tesseract_path is not None:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        self.data = pytesseract.image_to_data(image, lang=language, output_type='dict', config="")

    @classmethod
    def from_file(cls, file: File):
        # todo do preprocessing methods instead of loading file
        img = cv2.imread(file.path)
        tm = cls(img)

        return tm

    def to_publication(self):
        #todo find publication, published, publisher, and page count.
        pub = Publication()
        pub.publication = ""
        pub.published_at = datetime.now().isoformat()
        pub.add_article(self.to_article())

        return pub

    def to_article(self):
        # todo find byline, confidence, extracted_from, headline, lead, publication
        article = Article()
        [article.add_paragraph(p) for p in self.to_paragraphs()]
        return article

    def to_paragraphs(self):
        text = self.data['text']

        paragraphs = []
        b_str = ""
        for t in text:
            if t == "":
                if len(b_str) > 1 and (b_str[-1] == "\n" or b_str[-1] == "\r"):
                    # if last char was new line as well, then split into paragraph
                    paragraphs.append(b_str.strip())
                    b_str = ""
                else:
                    # empty string = new line
                    b_str += "\n\r"
            else:
                b_str += f"{t} "
        if b_str != "":
            paragraphs.append(b_str)

        #remove empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p != '']

        # Remove new lines and hyphens across them.
        paragraphs = [self.remove_hyphens_and_nl(p) for p in paragraphs]

        paragraphs = [self.str_to_paragraph(p) for p in paragraphs]

        return paragraphs

    @staticmethod
    def str_to_paragraph(p):
        paragraph = Paragraph()
        paragraph.kind = "paragraph"
        paragraph.value = p
        return paragraph

    @staticmethod
    def remove_hyphens_and_nl(p):
        p = p.replace("- \n", "")
        p = p.replace("- \r", "")
        p = p.replace("\n", "")
        p = p.replace("\r", "")
        return p

    def text_conf_matches_from_tesseract_data(self):
        return [[text, conf] for text, conf in zip(self.data['text'], self.data['conf']) if conf != "-1"]

    def get_average_conf(self):
        """ Gets the average of the confidence score
        :return: A float with the average confidence score
        """
        confidences = [int(x) for x in self.data['conf'] if 0 <= int(x) <= 100]

        # Avoid divide by zero
        if len(confidences) == 0:
            return 0
        return sum(confidences) / len(confidences)
