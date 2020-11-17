import re
from datetime import datetime
import cv2
import pytesseract
from knox_source_data_io.models.publication import Publication, Article, Paragraph

from alto_segment_lib.segment_module import SegmentModule
from crawler.file import File


class TesseractModule:

    def __init__(self, image, segments, language='dan', tesseract_path=None):
        if tesseract_path is not None:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        for segment in segments:
            cropped_image = image[segment.y1:segment.y2, segment.x1:segment.x2]


            cv2.imwrite(r"/home/jakob/Desktop/test/output/segment.png", cropped_image)

            text = pytesseract.image_to_data(image, lang=language, output_type='dict', config="")


        #self.data = pytesseract.image_to_data(image, lang=language, output_type='dict', config="")

    @classmethod
    def from_file(cls, file: File):
        # todo do preprocessing methods instead of loading file
        img = cv2.imread(file.path)

        segments = SegmentModule.run_segmentation(file.path.split(".")[0])

        tm = cls(img, segments)

        return tm

    def to_publication(self):
        #todo find publication, published, publisher, and page count.
        pub = Publication()
        pub.publication = "hej"
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
                if len(b_str) > 0 and b_str[-1] == "\n":
                    paragraphs.append(b_str.strip())
                    b_str = ""
                else:
                    b_str += "\n"
            else:
                b_str += f"{t} "

        paragraphs = [p for p in paragraphs if p != '']

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
        p = p.replace("\n", "")
        return p

    def text_from_tesseract_data(self):
        # todo handle newlines.
        pattern = re.compile(r'\s+')
        out_str = ""
        for text in self.data['text']:
            out_str += re.sub(pattern, '', text) + " "
        return out_str

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
