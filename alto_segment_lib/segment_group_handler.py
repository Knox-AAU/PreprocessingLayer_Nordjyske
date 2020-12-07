from typing import List
from alto_segment_lib.segment import SegmentGroup, Segment, SegmentType


class SegmentGroupHandler:
    """
    todo
    """
    groups: List[SegmentGroup]
    current_group: SegmentGroup = None
    unfinished_group: SegmentGroup = None

    def __init__(self):
        self.groups = []

    def start_group(self):
        """
        Moves the current group to unfinished, ends the current unfinished group if not null, and sets current
        group to None

        @return: void
        """
        # Cleanup
        if self.current_group is not None and len(self.current_group.paragraphs) > 0:
            if self.unfinished_group is not None:
                self.groups.append(self.unfinished_group)
            self.unfinished_group = self.current_group
        self.current_group = SegmentGroup()

    def add_segment(self, segment: Segment):
        """
        Adds the segment to the current or unfinished group if not None. Paragraphs are added to the paragraphs list
        and all lines of headings are added to the headers list

        @param segment: the segment to add
        @return: void
        """
        if self.current_group is not None:
            if segment.type == SegmentType.heading:
                self.current_group.headers = segment.lines
                # ToDo: (remove or use) Option to add more headers to heading
                # list[self.current_group.headers.append(sub_head) for sub_head in segment.lines]
            elif segment.type == SegmentType.paragraph:
                self.current_group.paragraphs.append(segment)
        elif self.unfinished_group is not None:
            if segment.type == SegmentType.heading:
                self.unfinished_group.headers.append(segment)
            elif segment.type == SegmentType.paragraph:
                self.unfinished_group.paragraphs.append(segment)

    def end_group(self):
        """
        Appends the current group to the groups list and sets it to None

        @return: void
        """
        if self.current_group is not None:
            if len(self.current_group.headers) > 0 or len(self.current_group.paragraphs) > 0:
                self.groups.append(self.current_group)
            self.current_group = None

    def finalize(self):
        """
        Appends the current and unfinished groups to the groups list and sets both to None

        @return:
        """
        if self.unfinished_group is not None:
            self.groups.append(self.unfinished_group)
            self.unfinished_group = None

        if self.current_group is not None and (
                len(self.current_group.headers) > 0 or len(self.current_group.paragraphs) > 0):
            self.groups.append(self.current_group)
            self.current_group = None
