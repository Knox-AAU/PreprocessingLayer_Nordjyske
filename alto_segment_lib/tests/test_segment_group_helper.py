from alto_segment_lib.segment import SegmentGroup, Segment, SegmentType
from alto_segment_lib.segment_helper import SegmentHelper
from alto_segment_lib.segment_group_handler import *


class TestSegmentGroupHelper:

    def test_start_group_sets_unfinished_group_to_current_group(self):
        segment_handler = SegmentGroupHandler()
        paragraph = Segment()
        paragraph.type = SegmentType.paragraph

        segment_handler.start_group()
        segment_handler.add_segment(paragraph)

        segment_handler.start_group()

        assert segment_handler.unfinished_group.paragraphs.__contains__(paragraph)

    def test_start_group_adds_unfinished_group_to_groups_when_new_group_is_started(self):
        segment_handler = SegmentGroupHandler()
        paragraph = Segment()
        paragraph.type = SegmentType.paragraph

        segment_handler.start_group()
        segment_handler.add_segment(paragraph)

        segment_handler.start_group()
        segment_handler.add_segment(paragraph)

        group = segment_handler.unfinished_group

        segment_handler.start_group()

        assert segment_handler.groups.__contains__(group)

    def test_start_group_sets_current_group_to_empty_group(self):
        segment_handler = SegmentGroupHandler()

        segment_handler.start_group()

        assert segment_handler.current_group.paragraphs.__len__() == 0 and segment_handler.current_group.headers.__len__() == 0


