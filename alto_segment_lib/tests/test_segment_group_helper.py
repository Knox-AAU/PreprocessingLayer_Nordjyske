from alto_segment_lib.segment import Line
from alto_segment_lib.segment_group_handler import *


class TestSegmentGroupHelper:

    def test_start_group_sets_unfinished_group_to_current_group(self):
        segment_group_handler = SegmentGroupHandler()
        paragraph = Segment()
        paragraph.type = SegmentType.paragraph

        segment_group_handler.start_group()
        segment_group_handler.add_segment(paragraph)

        segment_group_handler.start_group()

        assert segment_group_handler.unfinished_group.paragraphs.__contains__(paragraph)

    def test_start_group_adds_unfinished_group_to_groups_when_new_group_is_started(self):
        segment_group_handler = SegmentGroupHandler()
        paragraph = Segment()
        paragraph.type = SegmentType.paragraph

        segment_group_handler.start_group()
        segment_group_handler.add_segment(paragraph)

        segment_group_handler.start_group()
        segment_group_handler.add_segment(paragraph)

        group = segment_group_handler.unfinished_group

        segment_group_handler.start_group()

        assert segment_group_handler.groups.__contains__(group)

    def test_start_group_sets_current_group_to_empty_group(self):
        segment_group_handler = SegmentGroupHandler()

        segment_group_handler.start_group()

        assert segment_group_handler.current_group.paragraphs.__len__() == 0 and segment_group_handler.current_group.headers.__len__() == 0

    def test_add_segment(self):
        assert True

    def test_end_group_sets_current_group_to_none(self):
        segment_group_handler = SegmentGroupHandler()

        segment_group_handler.start_group()
        segment_group_handler.end_group()

        assert segment_group_handler.current_group is None

    def test_end_group_does_not_add_empty_group_to_groups_list(self):
        segment_group_handler = SegmentGroupHandler()

        segment_group_handler.start_group()
        segment_group_handler.end_group()

        assert segment_group_handler.groups.__len__() == 0

    def test_end_group_adds_current_group_with_paragraph_to_groups_list(self):
        segment_group_handler = SegmentGroupHandler()
        paragraph = Segment()
        paragraph.type = SegmentType.paragraph

        segment_group_handler.start_group()
        segment_group_handler.add_segment(paragraph)
        segment_group_handler.end_group()

        assert segment_group_handler.groups.__len__() == 1

    def test_end_group_adds_current_group_with_header_to_groups_list(self):
        segment_group_handler = SegmentGroupHandler()
        heading = Segment()
        heading.type = SegmentType.heading
        heading.lines.append(Line())

        segment_group_handler.start_group()
        segment_group_handler.add_segment(heading)
        segment_group_handler.end_group()

        assert segment_group_handler.groups.__len__() == 1


