import argparse
import codecs
import os

from knox_source_data_io.io_handler import IOHandler, Generator

from crawler.file import File
from crawler.file_types import FileType
from ocr.tesseract import TesseractModule

os.environ["OPENCV_IO_ENABLE_JASPER"] = "true"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # defines input and output path
    parser.add_argument('path', help='Input file')

    # defines toDate argument
    parser.add_argument('-o', '--output_dest', dest="output_path", default=None,
                        help='Optional output path, which a json file will be saved to.')

    parser.add_argument('--tesseract-path', dest="tesseract_path", default=None,
                        help='If tesseract is not in PATH, you can define tesseracts location here.')

    parser.add_argument('-lan','--language', dest="language", default="dan",
                        help='If other language than "dan" is to be used, define here.')

    args = parser.parse_args()
    tm = TesseractModule.from_file(File(args.path, FileType.JP2))
    publication = tm.to_publication()
    if args.output_path is None:
        print(publication.to_json())
    else:
        handler = IOHandler(Generator(app="OCR", version=1.0), "link/to/schema.json")  # ToDo: insert link
        with codecs.open(args.output_path, 'w', encoding="utf-8") as outfile:
            handler.write_json(publication, outfile)
