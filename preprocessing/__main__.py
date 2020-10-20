import argparse
import json
import codecs
from nitf_parser.parser import NitfParser
from preprocessing.main import Preprocessing

if __name__ == '__main__':
    preprocesser = Preprocessing()
    preprocesser_image = preprocesser.do_preprocessing("1988.jp2")

