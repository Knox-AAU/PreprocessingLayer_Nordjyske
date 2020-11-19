from os import environ

from knox_source_data_io.models.publication import Article
from pytesseract import pytesseract

from alto_segment_lib.segment_module import SegmentModule
from ocr.tesseract import TesseractModule

environ["OPENCV_IO_ENABLE_JASPER"] = "true"
import cv2

class OCRRunner:

    def __init__(self, ):
        i=0


    @classmethod
    def run_ocr(self, file, language='dan', tesseract_path=None):

        image = cv2.imread(file.path)
        segments = SegmentModule.run_segmentation(file.path.split(".")[0])

        article = Article()
        articles = []

        segments[40].type = "headline"

        for segment in segments:
            cropped_image = image[segment.y1:segment.y2, segment.x1:segment.x2]

            if segment.type == "paragraph":
                paragraphs = TesseractModule.from_file(cropped_image).to_paragraphs()
                [article.add_paragraph(p) for p in paragraphs]

            if segment.type == "headline":
                # todo implement when ordering is done
                articles.append(article)
                article = Article()
                headline = TesseractModule.from_file(cropped_image).to_paragraphs()
                article.headline = headline[0].value

        articles.append(article)
        publication = TesseractModule.from_articles_to_publication(articles)

        return publication