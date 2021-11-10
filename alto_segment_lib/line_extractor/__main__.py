"""Module for line extraction"""
import argparse

from alto_segment_lib.line_extractor.extractor import LineExtractor

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # defines input and output path
    parser.add_argument("path", help="The path to the image")

    args = parser.parse_args()

    LineExtractor().extract_lines_via_path(args.path)
