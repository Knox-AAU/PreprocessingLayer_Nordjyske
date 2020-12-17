import os
from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.repair_segments import RepairSegments, merge_segments
from alto_segment_lib.segment import SegmentType, Segment
from alto_segment_lib.segment_grouper import SegmentGrouper
from alto_segment_lib.segment_helper import SegmentHelper
from alto_segment_lib.segment_lines.segment_lines import SegmentLines


class SegmentModule:
    @staticmethod
    def run_segmentation(file_path):
        """
        Runs segmentation on a given .jp2 file.
        @param file_path: Path to jp2
        @return: ToDo
        """
        headers, paragraphs = SegmentModule.segment_headers_paragraph_from_file(file_path)

        # Returns no segment if there are more than 300 (to avoid adverts and stocks from stock market)
        if len(headers + paragraphs) > 300:
            return [], []

        segment_lines = SegmentLines(paragraphs, headers)
        (horizontal_lines, vertical_lines) = segment_lines.find_vertical_and_horizontal_lines()

        # Grouping
        grouper = SegmentGrouper()
        grouped_headers = SegmentHelper.group_headers_into_segments(headers)
        groups = grouper.order_segments(grouped_headers, paragraphs, horizontal_lines)
        ordered_segments = grouper.convert_groups_into_segments(groups)

        return ordered_segments

    @staticmethod
    def segment_headers_paragraph_from_file(file_path):
        """
        Gets headers and paragraphs from a .jp2 file.
        @param file_path: The path to a jp2 file.
        @return: ToDo
        """
        segment_helper = SegmentHelper()
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
        (headers, paragraphs) = segment_helper.group_lines_into_paragraphs_headers(text_lines)
        # Find lines in image, then split segments that cross those lines.
        lines = LineExtractor().extract_lines_via_path(image_file_path)
        paragraphs = segment_helper.split_segments_by_lines(paragraphs, lines)
        # Combine closely related text lines into actual paragraphs.
        paragraphs = segment_helper.combine_lines_into_segments(paragraphs)
        headers = [Segment.from_line(line, SegmentType.heading) for line in headers]
        # Remove segments that are completely within other segments,
        paragraphs = RepairSegments(paragraphs, 30).repair_rows()
        paragraphs = segment_helper.remove_segments_within_segments(headers, paragraphs)
        headers = segment_helper.remove_segments_within_segments(paragraphs, headers)
        paragraphs = merge_segments(paragraphs)

        return headers, paragraphs
