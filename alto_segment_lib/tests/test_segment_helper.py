from alto_segment_lib.segment_helper import *


class TestSegmentHelper:
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

        result = segment_helper.split_segments_by_lines(text_line, line)
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

        result = segment_helper.split_segments_by_lines(text_line, line)

        assert len(result) == 1 and result == text_line

    def test_group_headers_into_segments_single_header_success(self):
        header_line1 = Line()
        header_line1.x1 = 0
        header_line1.y1 = 0
        header_line1.x2 = 100
        header_line1.y2 = 20

        header_line2 = Line()
        header_line2.x1 = 5
        header_line2.y1 = 25
        header_line2.x2 = 100
        header_line2.y2 = 45

        header_lines = [header_line1, header_line2]
        header_segments = SegmentHelper.group_headers_into_segments(header_lines)

        assert len(header_segments) == 1

    def test_group_headers_into_segments_multiple_header_success(self):
        # First group of lines for header 1
        header_line1 = Line()
        header_line1.x1 = 0
        header_line1.y1 = 0
        header_line1.x2 = 100
        header_line1.y2 = 20

        header_line2 = Line()
        header_line2.x1 = 0
        header_line2.y1 = 30
        header_line2.x2 = 100
        header_line2.y2 = 50

        # Second group of lines for header 2
        header_line3 = Line()
        header_line3.x1 = 0
        header_line3.y1 = 600
        header_line3.x2 = 100
        header_line3.y2 = 620

        header_line4 = Line()
        header_line4.x1 = 0
        header_line4.y1 = 630
        header_line4.x2 = 100
        header_line4.y2 = 650

        header_lines = [header_line1, header_line2, header_line3, header_line4]
        header_segments = SegmentHelper.group_headers_into_segments(header_lines)

        assert len(header_segments) == 2

    def test_inside_box_actually_inside_box(self):
        the_box = [10, 10, 100, 100]
        assert SegmentHelper.inside_box(the_box, 50, 50)

    def test_inside_box_actually_outside_box(self):
        the_box = [10, 10, 100, 100]
        assert not SegmentHelper.inside_box(the_box, 101, 101)

    def test_distance_between_coordinates_success(self):
        dot1_x = 0
        dot2_x = 100
        dot1_y = dot2_y = 0

        distance = SegmentHelper.distance_between_coordinates(dot1_x, dot1_y, dot2_x, dot2_y)
        assert distance == 100

    def test_distance_between_coordinates_failed(self):
        dot1_x = 0
        dot2_x = 400
        dot1_y = dot2_y = 0

        distance = SegmentHelper.distance_between_coordinates(dot1_x, dot1_y, dot2_x, dot2_y)
        assert not distance == 500
