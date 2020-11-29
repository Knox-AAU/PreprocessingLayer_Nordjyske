from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
from alto_segment_lib.example import display_segments
from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.repair_segments import RepairSegments
from alto_segment_lib.segment_helper import SegmentHelper


class SegmentModule:

    @staticmethod
    def run_segmentation(file_path):

        lines = LineExtractor().extract_lines_via_path(file_path + ".jp2")
        alto_extractor = AltoSegmentExtractor(file_path + ".alto.xml")
        alto_extractor.set_dpi(300)
        alto_extractor.set_margin(0)

        segment_helper = SegmentHelper(file_path + ".alto.xml")

        text_lines = alto_extractor.extract_lines()
        text_lines = segment_helper.repair_text_lines(text_lines, lines)
        lists = segment_helper.group_lines_into_paragraphs_headers(text_lines)
        segments = segment_helper.combine_lines_into_segments(lists[1])

        paragraphs = [segment for segment in segments if segment.type == "paragraph"]
        repair = RepairSegments(paragraphs, 30)
        rep_rows_segments = repair.repair_rows()
        paragraphs.clear()
        segments_para = rep_rows_segments
        display_segments(segments_para, file_path, "repaired")

        return segments_para
