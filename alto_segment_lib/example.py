import argparse
import os
os.environ["OPENCV_IO_ENABLE_JASPER"] = "true"
import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from alto_segment_lib.repair_segments import RepairSegments
from alto_segment_lib.segment_grouper import SegmentGrouper
from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.segment_helper import SegmentHelper
from PIL import Image

base_path: str
filename: str
filepath: str
filetype = ".jp2"


def display_segments(segments_for_display, file_path, name):
    image = cv2.imread(file_path + filetype)
    cv2.imwrite(file_path + ".tiff", image)
    plt.imshow(Image.open(file_path + ".tiff"))
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

    counter = 1

    # Add the patch to the Axes
    # plt.hlines(100, 100, 100+repair.get_median_column_width(), colors='k', linestyles='solid', label='Median paragraph width')

    for segment in segments_for_display:
        plt.gca().add_patch(
            Rectangle((segment.x1, segment.y1), (segment.x2 - segment.x1), (segment.y2 - segment.y1), linewidth=0.3,
                      edgecolor='r', facecolor='none'))
        plt.text(segment.x1+25, segment.y1+30, "["+str(counter)+"]", horizontalalignment='left', verticalalignment='top')
        # plt.text(seg[0]+45, seg[1] + 200, str((seg[2]-seg[0])), horizontalalignment='left', verticalalignment='top')
        counter += 1

    plt.savefig(file_path + "-" + name + ".png", dpi=600, bbox_inches='tight')
    plt.gca().clear()


def display_lines(headers_for_display, paragraphs_for_display, file_path, name):
    plt.imshow(Image.open(file_path + filetype))
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

    counter = 1

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
    for file_name in os.listdir(basepath):
        file_path = os.path.join(basepath, file_name)

        if not os.path.isfile(file_path) or not file_path.endswith(".jp2"):
            continue
        file_path = file_path.split(".jp2")[0]
        print(file_path)

        run_file(file_path)


def run_file(file_path):
    line_extractor = LineExtractor()
    lines = line_extractor.extract_lines_via_path(file_path + ".jp2")
    # display_lines([], lines, file_path, "streger")

    altoExtractor = AltoSegmentExtractor(file_path + ".alto.xml")
    altoExtractor.set_dpi(300)
    altoExtractor.set_margin(0)

    segment_helper = SegmentHelper(file_path + ".alto.xml")

    text_lines = altoExtractor.extract_lines()

    text_lines = segment_helper.repair_text_lines(text_lines, lines)
    lists = segment_helper.group_lines_into_paragraphs_headers(text_lines)
    #display_lines(lists[0], lists[1], "lines", file_path)
    header_segments = segment_helper.combine_lines_into_segments(lists[0])
    segments = segment_helper.combine_lines_into_segments(lists[1])
    #display_segments(segments, file_path, "segments")

    headers = [segment for segment in segments if segment.type == "header"]
    paragraphs = [segment for segment in segments if segment.type == "paragraph"]
    repair = RepairSegments(paragraphs, 30)
    rep_rows_segments2 = repair.repair_rows()

    segments_para = rep_rows_segments2
    display_segments(segments_para, file_path, "repaired")
    lines = [element for element, element in enumerate(lines) if element.is_horizontal()]

    #grouper = SegmentGrouper()
    #groups = grouper.group_segments_in_order(header_segments, paragraphs, lines)
    #print("Groups: "+str(len((groups))))

    #display_segments(lines, file_path, "grouped")
    #display_segments(segments_para, file_path, "paragrphs")
    #display_segments(header_segments, file_path, "segments")


    paragraphs.clear()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='The path to the image folder')
    parser.add_argument('filename', help='The name of the file without filetype')

    args = parser.parse_args()

    base_path = args.path
    filename = args.filename
    filepath = base_path + filename

    #run_multiple_files(base_path)
    run_file(filepath)
