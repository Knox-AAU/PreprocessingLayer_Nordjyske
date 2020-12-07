import os
from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
from alto_segment_lib.example import display_segments
from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.repair_segments import RepairSegments
from alto_segment_lib.segment import SegmentType
from alto_segment_lib.segment_grouper import SegmentGrouper
from alto_segment_lib.segment_helper import SegmentHelper
import configparser


class SegmentModule:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.__threshold_block_header_to_paragraph = float(config['page_segmentation']['threshold_block_header_to_paragraph'])
        self.__threshold_line_header_to_paragraph = float(config['page_segmentation']['threshold_line_header_to_paragraph'])
        self.__min_lines_to_compare_block_height_instead_of_line_height = int(config['page_segmentation']['min_lines_to_compare_block_height_instead_of_line_height'])
        self.__group_same_column_margin = float(config['page_segmentation']['group_same_column_margin'])
        self.__group_same_segment_margin_px = float(config['page_segmentation']['group_same_segment_margin_px'])
        self.__min_cluster_size = int(config['page_segmentation']['min_cluster_size'])

    @staticmethod
    def run_segmentation(file_path):
        line_extractor = LineExtractor()
        lines = line_extractor.extract_lines_via_path(file_path + ".jp2")
        # display_lines([], lines, file_path, "streger")

        altoExtractor = AltoSegmentExtractor(file_path + ".alto.xml")
        altoExtractor.set_dpi(300)
        altoExtractor.set_margin(0)

        segment_helper = SegmentHelper()

        text_lines = altoExtractor.extract_lines()

        text_lines = segment_helper.repair_text_lines(text_lines, lines)
        lists = segment_helper.group_lines_into_paragraphs_headers(text_lines, file_path + ".alto.xml")
        # display_lines(lists[0], lists[1], "lines", file_path)
        header_lines = lists[0]
        segments = segment_helper.combine_lines_into_segments(lists[1])
        # display_segments(segments, file_path, "segments")

        header_as_segment = SegmentHelper.group_headers_into_segments(header_lines)

        print(len(header_as_segment))

        headers = [segment for segment in segments if segment.type == SegmentType.heading]
        paragraphs = [segment for segment in segments if segment.type == SegmentType.paragraph]
        repair = RepairSegments(paragraphs, 30)
        rep_rows_segments2 = repair.repair_rows()

        segments_para = rep_rows_segments2
        # display_segments(segments_para, file_path, "repaired")
        lines = [element for element, element in enumerate(lines) if element.is_horizontal()]

        grouper = SegmentGrouper()
        ordered_segments = grouper.order_segments(header_as_segment, paragraphs, lines)

        return ordered_segments

    def segment_page(self, file_path: str, image=None) -> [list, list]:
        """
        Segments the page into headers and paragraphs
        @param file_path: The path to the file we are segmentibng
        @param image: The image we are segmenting
        @return: headers, paragraphs: a tuple including a list of headers and a list of paragraphs
        """
        assert file_path.endswith(".jp2")

        image_file_path = file_path
        alto_file_path = f"{file_path.split('.jp2')[0]}.alto.xml"

        assert os.path.isfile(image_file_path)
        assert os.path.isfile(alto_file_path)

        # Find the text-lines from Alto-xml
        alto_extractor = AltoSegmentExtractor(alto_file_path)
        alto_extractor.dpi = 300
        alto_extractor.margin = 0
        text_lines = alto_extractor.extract_lines()

        (headers, paragraphs) = SegmentHelper.group_lines_into_paragraphs_headers(text_lines)

        # Find lines in image, then split segments that cross those lines.
        lines = LineExtractor().extract_lines_via_path(image_file_path) \
            if image is None else LineExtractor().extract_lines_via_image(image)
        paragraphs = SegmentHelper.split_segments_by_lines(paragraphs, lines)

        # Combine closely related text lines into actual paragraphs.
        paragraphs = SegmentHelper.combine_lines_into_segments(paragraphs)

        # Remove segments that are completely within other segments,
        paragraphs = RepairSegments(paragraphs, 30).repair_rows()

        paragraphs = SegmentHelper.remove_segments_within_segments(headers, paragraphs)
        headers = SegmentHelper.remove_segments_within_segments(paragraphs, headers)
        return headers, paragraphs
