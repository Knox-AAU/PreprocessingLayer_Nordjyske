from os import environ

from knox_source_data_io.models.publication import Article
from pytesseract import pytesseract

from alto_segment_lib.segment_module import SegmentModule

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
        data = []
        i = 0
        for segment in segments:

            if i < 3:
                cropped_image = image[segment.y1:segment.y2, segment.x1:segment.x2]

                data.append(pytesseract.image_to_data(image, lang=language, output_type='dict', config=""))
                i += 1
            else:
                continue