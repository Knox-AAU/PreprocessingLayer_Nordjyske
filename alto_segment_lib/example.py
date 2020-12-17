import argparse
import os

from alto_segment_lib.line import Line
from alto_segment_lib.repair_segments import RepairSegments
from alto_segment_lib.segment import Segment, SegmentType
from alto_segment_lib.segment_grouper import SegmentGrouper
from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
import matplotlib.pyplot as plt
from alto_segment_lib.segment_helper import SegmentHelper
from matplotlib.patches import Rectangle
from PIL import Image
from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.repair_segments import merge_segments
import matplotlib.patheffects as peffect
from alto_segment_lib.segment_lines.segment_lines import SegmentLines
os.environ["OPENCV_IO_ENABLE_JASPER"] = "true"
from cv2 import cv2

base_path: str
filename: str
filepath: str
filetype = ".jp2"


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

    segment_helper = SegmentHelper()

    image_file_path = file_path+".jp2"
    alto_file_path = file_path+".alto.xml"

    # Find the text-lines from Alto-xml
    alto_extractor = AltoSegmentExtractor(alto_file_path)
    alto_extractor.dpi = 300
    alto_extractor.margin = 0
    text_lines = alto_extractor.extract_lines()

    (headers, paragraphs) = segment_helper.group_lines_into_paragraphs_headers(text_lines)

    # Find lines in image, then split segments that cross those lines.
    lines = LineExtractor().extract_lines_via_path(image_file_path)
    paragraphs = segment_helper.split_segments_by_lines(paragraphs, lines)

    # Combine closely related text lines into actual paragraphs.
    paragraphs = segment_helper.combine_lines_into_segments(paragraphs)

    # Remove segments that are completely within other segments,
    paragraphs = RepairSegments(paragraphs, 30).repair_rows()

    paragraphs = segment_helper.remove_segments_within_segments(headers, paragraphs)
    headers = segment_helper.remove_segments_within_segments(paragraphs, headers)

    print("Headers before: " + str(len(headers)))

    print("Before: "+str(len(paragraphs)))
    display_segments(paragraphs, file_path, "paragraphs-before")
    paragraphs = merge_segments(paragraphs)
    print("After:  " + str(len(paragraphs)))
    display_segments(paragraphs, file_path, "paragraphs-after")

    our_headers = segment_helper.group_headers_close_in_proximity_into_a_single_segment(headers)
    segment_lines = SegmentLines(paragraphs, our_headers)
    # (horizontal_lines, vertical_lines) = segment_lines.find_vertical_and_horizontal_lines()
    horizontal_lines = []

    # horizontal_lines.clear()
    LineExtractor.show_lines_on_image(cv2.imread(file_path + ".jp2", cv2.CV_8UC1), horizontal_lines, "-Wupti")

    display_segments(horizontal_lines, file_path, "paragraphs-before")


    # Grouping


    grouper = SegmentGrouper()
    grouped_headers = SegmentHelper.group_headers_close_in_proximity_into_a_single_segment(headers)

    print("Headers after : " + str(len(grouped_headers)))

    display_segments(grouped_headers, file_path, "box-headers")
    groups = grouper.order_segments(grouped_headers, paragraphs, lines)
    # groups = grouper.order_segments(grouped_headers, paragraphs, horizontal_lines)

    image = Image.open(file_path + filetype)
    image.putalpha(128)

    plt.imshow(image)
    plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})
    counter = 1
    color_counter = 0

    colors = ['magenta', 'blue', 'green', 'brown', 'orange', 'yellow', 'purple']

    for group in groups:
        if color_counter >= len(colors):
            color_counter = 0
        color = colors[color_counter]
        color_counter += 1

        for segment in group.paragraphs:
            plt.gca().add_patch(
                Rectangle((segment.x1, segment.y1), (segment.x2 - segment.x1), (segment.y2 - segment.y1), linewidth=0.5,
                          edgecolor=color, facecolor='none'))

        if len(group.headers) > 0:
            header = group.headers[0]
            circle = plt.Circle((header.x1 + 100, header.y1 + 100), 150, linewidth=0.35, edgecolor="black", facecolor=color)
            plt.gca().add_patch(circle)
            plt.rcParams.update({'font.size': 6, 'text.color': 'white', 'axes.labelcolor': 'white'})
            padding = 51
            if counter > 9:
                padding -= 50
            text = plt.text(header.x1+padding, header.y1+45, str(counter), horizontalalignment='left', verticalalignment='top')
            text.set_path_effects([peffect.Stroke(linewidth=0.7, foreground='black'), peffect.Normal()])


        counter += 1

    plt.savefig(file_path + "-grouped.png", dpi=600, bbox_inches='tight')
    plt.gca().clear()

    display_segments(lines, file_path, "lines")
    display_segments(paragraphs, file_path, "paragrphs")
    display_segments(our_headers, file_path, "headers")

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
