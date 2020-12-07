from alto_segment_lib.repair_segments import *
from alto_segment_lib.segment import Segment, SegmentType


class TestRepairSegments:

    def test_repair_rows_segment_within_success(self):
        big_segment = Segment([0, 0, 100, 100])
        small_segment = Segment([10, 10, 50, 50])
        repair_segments = RepairSegments([big_segment, small_segment])
        repaired_segments = repair_segments.repair_rows()

        assert len(repaired_segments) == 1 and repaired_segments[0] == big_segment

    def test_repair_rows_segment_within_fail(self):
        first_segment = Segment([0, 0, 50, 50])
        second_segment = Segment([40, 40, 70, 70])
        repair_segments = RepairSegments([first_segment, second_segment])
        repaired_segments = repair_segments.repair_rows()

        assert len(repaired_segments) == 2

    def test_repair_rows_segment_move_down_success(self):
        first_segment = Segment([0, 0, 100, 100])
        second_segment = Segment([0, 50, 100, 150])
        repair_segments = RepairSegments([first_segment, second_segment])
        repaired_segments = repair_segments.repair_rows()

        assert len(repaired_segments) == 2 and repaired_segments[1].y1 == first_segment.y2

    def test_repair_rows_segment_move_up_success(self):
        first_segment = Segment([0, 100, 100, 300])
        second_segment = Segment([0, 0, 100, 200])
        repair_segments = RepairSegments([first_segment, second_segment])
        repaired_segments = repair_segments.repair_rows()

        assert len(repaired_segments) == 2 and repaired_segments[1].y2 == first_segment.y1

    def test_merge_segments_success(self):
        segment1 = Segment([0, 0, 100, 100], SegmentType.paragraph)
        segment2 = Segment([0, 110, 100, 200], SegmentType.paragraph)
        segments = [segment1, segment2]

        merged_segments = merge_segments(segments)

        assert len(merged_segments) == 1

    def test_merge_segments_success_no_segments_within_distance(self):
        segment1 = Segment([0, 0, 100, 100], SegmentType.paragraph)
        segment2 = Segment([0, 190, 100, 300], SegmentType.paragraph)
        segments = [segment1, segment2]

        merged_segments = merge_segments(segments)

        assert len(merged_segments) == 2

    def test_merge_segments_failed(self):
        segment1 = Segment([0, 0, 100, 100], SegmentType.paragraph)
        segment2 = Segment([0, 190, 100, 300], SegmentType.paragraph)
        segments = [segment1, segment2]

        merged_segments = merge_segments(segments)

        assert not len(merged_segments) == 1
