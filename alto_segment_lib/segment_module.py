import os

from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.repair_segments import RepairSegments
from alto_segment_lib.segment import SegmentType
from alto_segment_lib.segment_grouper import SegmentGrouper
from alto_segment_lib.segment_helper import SegmentHelper
from alto_segment_lib.segment_lines.segment_lines import SegmentLines


class SegmentModule:

    @staticmethod
    def run_segmentation(file_path):
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

        # Remove segments that are completely within other segments,
        paragraphs = RepairSegments(paragraphs, 30).repair_rows()

        paragraphs = segment_helper.remove_segments_within_segments(headers, paragraphs)
        headers = segment_helper.remove_segments_within_segments(paragraphs, headers)

        segment_lines = SegmentLines(paragraphs, headers, file_path)
        segment_lines.find_vertical_lines()
        segment_lines.find_horizontal_lines()

        return headers, paragraphs











        segment_helper = SegmentHelper()
        altoExtractor = AltoSegmentExtractor(file_path + ".alto.xml")
        altoExtractor.set_dpi(300)
        altoExtractor.set_margin(0)


        # Lines are found in the image
        lines = LineExtractor().extract_lines_via_path(file_path + ".jp2")
        # display_lines([], lines, file_path, "streger")

        text_lines = altoExtractor.extract_lines()

        text_lines = segment_helper.repair_text_lines(text_lines, lines)
        lists = segment_helper.group_lines_into_paragraphs_headers(text_lines, file_path + ".alto.xml")
        # display_lines(lists[0], lists[1], "lines", file_path)
        header_lines = lists[0]


        # Segments are found
        segments = segment_helper.combine_lines_into_segments(lists[1])
        # display_segments(segments, file_path, "segments")

        header_as_segment = SegmentHelper.group_headers_into_segments(header_lines)

        paragraphs = [segment for segment in segments if segment.type == SegmentType.paragraph]
        repair = RepairSegments(paragraphs, 30)
        rep_rows_segments = repair.repair_rows()

        segments_para = rep_rows_segments

        vertical_segment_lines = SegmentLines().find_vertical_lines(segments_para + header_lines, file_path + ".jp2")

        lines = [element for element, element in enumerate(lines) if element.is_horizontal()]

        #grouper = SegmentGrouper()

        #groups = grouper.group_segments_in_order(header_as_segment, paragraphs, lines)

        #return groups