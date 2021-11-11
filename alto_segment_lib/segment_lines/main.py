import argparse

from alto_segment_lib.segment_module import SegmentModule

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="The path to the image")

    args = parser.parse_args()

    filepath = args.filepath

    SegmentModule().run_segmentation(filepath)
