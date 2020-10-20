import argparse
import codecs
from knox_source_data_io.models import *
from knox_source_data_io.io_handler import IOHandler, Generator

from initial_ocr.teseract_module import TesseractModule

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # defines input and output path
    parser.add_argument('path', help='Input file')

    # defines toDate argument
    parser.add_argument('-o', '--output', dest="output_path", default=None,
                        help='Optional output path, which a json file will be saved to.')

    parser.add_argument('--tesseract-path', dest="tesseract_path", default=None,
                        help='If tesseract is not in PATH, you can define tesseracts location here.')

    parser.add_argument('-lan','--language', dest="language", default="dan",
                        help='If other language than "dan" is to be used, define here.')

    args = parser.parse_args()
    tesseract_module = TesseractModule()
    publication = tesseract_module.run_tesseract_on_image(args.path, language=args.language, tesseract_path=args.tesseract_path)
    if args.output_path is None:
        print(publication.to_json())
    else:
        handler = IOHandler(Generator(app="haha tesseract go brbrb", version=1.0), "link/to/schema.json")
        with codecs.open(args.output_path, 'w', encoding="utf-8") as outfile:
            handler.write_json(publication, outfile)
