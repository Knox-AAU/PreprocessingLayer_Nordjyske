from alto_segment_lib.segment_helper import *


class TestSegmentHelper:

    def test_find_line_width_median_success(self):
        lines = [Line([0, 0, 10, 10]), Line([0, 0, 20, 20]), Line([0, 0, 20, 20]), Line([0, 0, 2000, 2000]),
                 Line([0, 0, 2000, 2000])]

        median = SegmentHelper.find_line_width_median(lines)

        assert median == 20

    def test_find_line_height_median_success(self):
        lines = [Line([0, 0, 10, 10]), Line([0, 0, 20, 20]), Line([0, 0, 20, 20]), Line([0, 0, 2000, 2000]),
                 Line([0, 0, 2000, 2000])]

        median = SegmentHelper.find_line_height_median(lines)

        assert median == 20

    def test_group_lines_into_paragraphs_headers_header_success(self):
        segment_helper = SegmentHelper()
        header = Line([0, 0, 2000, 2000])
        lines = [Line([0, 0, 10, 10]), Line([0, 0, 20, 20]), Line([0, 0, 20, 20]), Line([0, 0, 25, 25]),
                 header]

        (headers, paragraph) = segment_helper.group_lines_into_paragraphs_headers(lines)

        assert len(headers) == 1 and headers[0] == header

    def test_group_lines_into_paragraphs_headers_paragraph_success(self):
        segment_helper = SegmentHelper()
        paragraph = Line([0, 0, 10, 10])
        lines = [paragraph, Line([0, 0, 20, 20]), Line([0, 0, 20, 20]), Line([0, 0, 25, 25]),
                 Line([0, 0, 2000, 2000])]

        (headers, paragraphs) = segment_helper.group_lines_into_paragraphs_headers(lines)

        assert len(paragraphs) == 4 and paragraphs[0] == paragraph

    def test_make_box_around_lines_success(self):
        lines = [Line([0, 0, 10, 10]), Line([5, 10, 15, 20]), Line([0, 20, 10, 30])]

        segment = SegmentHelper.make_box_around_lines(lines)
        expected_segment = Segment([0, 0, 15, 30])

        assert segment.x1 == expected_segment.x1 \
            and segment.x2 == expected_segment.x2 \
            and segment.y1 == expected_segment.y1 \
            and segment.y2 == expected_segment.y2

    def test_combine_lines_into_segments_success(self):
        segment_helper = SegmentHelper()

        lines = [Line([0, 0, 10, 10]), Line([0, 10, 10, 20]), Line([0, 20, 10, 30]),
                 Line([500, 0, 510, 10]), Line([500, 10, 510, 20]), Line([500, 20, 510, 30])]

        segments = segment_helper.combine_lines_into_segments(lines)
        expected_first = Segment([0, 0, 10, 30])
        expected_second = Segment([500, 0, 510, 30])

        assert len(segments) == 2 \
            and segments[0].x1 == expected_first.x1 \
            and segments[0].x2 == expected_first.x2 \
            and segments[0].y1 == expected_first.y1 \
            and segments[0].y2 == expected_first.y2 \
            and segments[1].x1 == expected_second.x1 \
            and segments[1].x2 == expected_second.x2 \
            and segments[1].y1 == expected_second.y1 \
            and segments[1].y2 == expected_second.y2

    def test_repair_text_lines_success(self):
        segment_helper = SegmentHelper()
        text_line = [Line([0, 50, 100, 100])]
        line = [Line([50, 0, 50, 100])]

        result = segment_helper.repair_text_lines(text_line, line)
        expected_first = Segment([0, 50, 50, 100])
        expected_second = Segment([50, 50, 100, 100])

        assert len(result) == 2 \
            and result[0].x1 == expected_first.x1 \
            and result[0].x2 == expected_first.x2 \
            and result[0].y1 == expected_first.y1 \
            and result[0].y2 == expected_first.y2 \
            and result[1].x1 == expected_second.x1 \
            and result[1].x2 == expected_second.x2 \
            and result[1].y1 == expected_second.y1 \
            and result[1].y2 == expected_second.y2

    def test_repair_text_lines_fail(self):
        segment_helper = SegmentHelper()
        text_line = [Line([0, 50, 100, 100])]
        line = [Line([200, 0, 200, 100])]

        result = segment_helper.repair_text_lines(text_line, line)

        assert len(result) == 1 and result == text_line
