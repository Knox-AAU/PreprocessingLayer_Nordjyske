"""Module for page segmentation"""
import argparse
import os

os.environ["OPENCV_IO_ENABLE_JASPER"] = "true"
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
from alto_segment_lib.segment_module import *


def display_segments_headers(headers, segments_for_display, file_path, file_name):
    """
    Plots the segmented headers

    @param headers: list of headers
    @param segments_for_display:
    @param file_path:path to the file being segmented
    @param file_name: name of the file being segmented
    """
    print(file_path)

    plt.imshow(Image.open(file_path))
    plt.rcParams.update({"font.size": 3, "text.color": "red", "axes.labelcolor": "red"})

    for segment in headers:
        plt.gca().add_patch(
            Rectangle(
                (segment.x1, segment.y1),
                (segment.x2 - segment.x1),
                (segment.y2 - segment.y1),
                linewidth=0.3,
                edgecolor="b",
                facecolor="none",
            )
        )
        plt.text(
            segment.x1,
            segment.y1,
            f"[{segment.x1},{segment.y1}],[{segment.x2},{segment.y2}]",
            horizontalalignment="left",
            verticalalignment="top",
            fontsize=1,
            color="blue",
        )

    for segment in segments_for_display:
        plt.gca().add_patch(
            Rectangle(
                (segment.x1, segment.y1),
                (segment.x2 - segment.x1),
                (segment.y2 - segment.y1),
                linewidth=0.3,
                edgecolor="r",
                facecolor="none",
            )
        )
        plt.text(
            segment.x1,
            segment.y1,
            f"[{segment.x1},{segment.y1}],[{segment.x2},{segment.y2}]",
            horizontalalignment="left",
            verticalalignment="top",
            fontsize=1,
            color="blue",
        )
    plt.savefig(file_path + "-" + file_name + ".png", dpi=600, bbox_inches="tight")
    plt.gca().clear()


def run_multiple_files(basepath):
    """
    Runs page segmentation on all files in a directory
    @param basepath: The directory to search for files in.
    """
    [
        run_file(os.path.join(basepath, file_name))
        for file_name in os.listdir(basepath)
        if file_name.endswith(".jp2")
    ]


def run_file(file_path):
    """
    Runs page segmentation on one files
    @param file_path: The path of the JP2-image to run page segmentation on.
    """
    headers, paragraphs = SegmentModule.segment_headers_paragraph_from_file(file_path)
    display_segments_headers(headers, paragraphs, file_path, "repaired")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="The path to the image folder")
    parser.add_argument("filename", help="The name of the file without filetype")

    args = parser.parse_args()

    base_path = args.path
    filename = args.filename
    filepath = base_path + filename

    # run_multiple_files(base_path)
    run_file(filepath)
