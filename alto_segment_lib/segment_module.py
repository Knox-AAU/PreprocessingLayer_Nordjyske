from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
from alto_segment_lib.example import display_segments
from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.repair_segments import RepairSegments
from alto_segment_lib.segment import SegmentType
from alto_segment_lib.segment_grouper import SegmentGrouper
from alto_segment_lib.segment_helper import SegmentHelper


class SegmentModule:

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
