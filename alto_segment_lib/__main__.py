import argparse
import os
from threading import Lock

from joblib import Parallel, delayed

from alto_segment_lib.repair_segments import RepairSegments
from alto_segment_lib.segment import Segment, SegmentType
from alto_segment_lib.segment_grouper import SegmentGrouper
from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
import matplotlib.pyplot as plt
from alto_segment_lib.segment_helper import SegmentHelper
from matplotlib.patches import Rectangle
from PIL import Image

from alto_segment_lib.line_extractor.extractor import LineExtractor

base_path: str
filename: str
filepath: str
filetype = ".jp2"

lock = Lock()


def display_segments(segments_for_display, file_path, name, color='r'):
    plt.imshow(Image.open(file_path + filetype))
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

    counter = 1

    # Add the patch to the Axes
    # plt.hlines(100, 100, 100+repair.get_median_column_width(), colors='k', linestyles='solid', label='Median paragraph width')

    for segment in segments_for_display:
        plt.gca().add_patch(
            Rectangle((segment.x1, segment.y1), (segment.x2 - segment.x1), (segment.y2 - segment.y1), linewidth=0.3,
                      edgecolor=color, facecolor='none'))
        # plt.text(segment.x1+25, segment.y1+30, "["+str(counter)+"]", horizontalalignment='left', verticalalignment='top')
        # plt.text(seg[0]+45, seg[1] + 200, str((seg[2]-seg[0])), horizontalalignment='left', verticalalignment='top')
        counter += 1

    plt.savefig(file_path + "-" + name + ".png", dpi=600, bbox_inches='tight')
    plt.gca().clear()


def display_segments_headers(headers, segments_for_display, file_path, name):
    plt.imshow(Image.open(file_path + filetype))
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

    for segment in headers:
        plt.gca().add_patch(
            Rectangle((segment.x1, segment.y1), (segment.x2 - segment.x1),
                      (segment.y2 - segment.y1), linewidth=0.3,
                      edgecolor='b', facecolor='none'))
        plt.text(segment.x1, segment.y1, f"[{segment.x1},{segment.y1}],[{segment.x2},{segment.y2}]",
                 horizontalalignment='left', verticalalignment='top', fontsize=1, color="blue")

    for segment in segments_for_display:
        plt.gca().add_patch(
            Rectangle((segment.x1, segment.y1), (segment.x2 - segment.x1),
                      (segment.y2 - segment.y1), linewidth=0.3,
                      edgecolor='r', facecolor='none'))
        plt.text(segment.x1, segment.y1, f"[{segment.x1},{segment.y1}],[{segment.x2},{segment.y2}]",
                 horizontalalignment='left', verticalalignment='top', fontsize=1, color="blue")
    plt.savefig(file_path + "-" + name + ".png", dpi=600, bbox_inches='tight')
    plt.gca().clear()


def display_lines(headers_for_display, paragraphs_for_display, file_path, name):
    plt.imshow(Image.open(file_path + filetype))
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

    for segment in headers_for_display:
        plt.gca().add_patch(
            Rectangle((segment.x1, segment.y1), (segment.x2 - segment.x1), (segment.y2 - segment.y1), linewidth=0.3,
                      edgecolor='b', facecolor='none'))
        # plt.text(segment.x1+25, segment.y1+30, "["+str(segment.font)+"]", horizontalalignment='left', verticalalignment='top')

    for segment in paragraphs_for_display:
        plt.gca().add_patch(
            Rectangle((segment.x1, segment.y1), (segment.x2 - segment.x1), (segment.y2 - segment.y1), linewidth=0.3,
                      edgecolor='r', facecolor='none'))
        # plt.text(segment.x1+25, segment.y1+30, "["+str(segment.font)+"]", horizontalalignment='left', verticalalignment='top')

    plt.savefig(file_path + "-" + name + ".png", dpi=600, bbox_inches='tight')
    plt.gca().clear()


def run_multiple_files(basepath):
    Parallel(n_jobs=16, prefer="threads")(
        delayed(run_mt)(file_name, basepath)
        for file_name in os.listdir(basepath))


def run_mt(file_name, basepath):
    file_path = os.path.join(basepath, file_name)

    if not os.path.isfile(file_path) or not file_path.endswith(".jp2"):
        return
    file_path = file_path.split(".jp2")[0]

    run_file(file_path)


def run_file(file_path):
    lines = LineExtractor().extract_lines_via_path(file_path + ".jp2")
    # display_lines([], lines, file_path, "streger")

    altoExtractor = AltoSegmentExtractor(file_path + ".alto.xml")
    altoExtractor.set_dpi(300)
    altoExtractor.set_margin(0)

    segment_helper = SegmentHelper()

    text_lines = altoExtractor.extract_lines()
    (headers, text_lines) = segment_helper.group_lines_into_paragraphs_headers(text_lines)
    # display_lines(headers, text_lines, file_path, "para-header-repair")
    text_lines = segment_helper.split_segments_by_lines(text_lines, lines)
    #headers = segment_helper.split_segments_by_lines(headers, lines)
    segments = segment_helper.combine_lines_into_segments(text_lines)
    # display_segments(segments, file_path, "segments")

    paragraphs = [segment for segment in segments if segment.type == "paragraph"]
    paragraphs = RepairSegments(paragraphs, 30).repair_rows()

    paragraphs = segment_helper.remove_segments_within_segments(headers, paragraphs)
    headers = segment_helper.remove_segments_within_segments(paragraphs, headers)

    lock.acquire()
    display_segments_headers(headers, paragraphs, file_path, "repaired")
    lock.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='The path to the image folder')
    parser.add_argument('filename', help='The name of the file without filetype')

    args = parser.parse_args()

    base_path = args.path
    filename = args.filename
    filepath = base_path + filename

    run_multiple_files(base_path)
    # run_file(filepath)
