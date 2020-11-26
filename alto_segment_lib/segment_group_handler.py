from alto_segment_lib.segment import SegmentGroup, Segment, SegmentType
from alto_segment_lib.segment_helper import SegmentHelper


class SegmentGroupHandler:
    groups: list[SegmentGroup]
    current_group: SegmentGroup = None
    unfinished_group: SegmentGroup = None

    def __init__(self):
        self.groups = []

    def start_group(self):
        # Cleanup
        if self.current_group is not None and len(self.current_group.paragraphs) > 0:
            if self.unfinished_group is not None:
                self.groups.append(self.unfinished_group)
            self.unfinished_group = self.current_group
        self.current_group = SegmentGroup()

    def add_segment(self, segment: Segment):
        if self.current_group is not None:
            if segment.type == SegmentType.heading:
                self.current_group.headers = segment.lines
                # ToDo: remove; Option to add more headers to heading list[self.current_group.headers.append(sub_head) for sub_head in segment.lines]
            elif segment.type == SegmentType.paragraph:
                self.current_group.paragraphs.append(segment)
        else:
            if self.unfinished_group is not None:
                if segment.type == SegmentType.heading:
                    self.unfinished_group.headers.append(segment)
                elif segment.type == SegmentType.paragraph:
                    self.unfinished_group.paragraphs.append(segment)

    def end_group(self):
        if self.current_group is not None:
            if len(self.current_group.headers) > 0 or len(self.current_group.paragraphs) > 0:
                self.groups.append(self.current_group)
            self.current_group = None

    def finalize(self):
        if self.unfinished_group is not None:
            self.groups.append(self.unfinished_group)
            self.unfinished_group = None

        if self.current_group is not None:
            self.groups.append(self.current_group)
            self.current_group = None

    def get_header_segment(self):
        if self.current_group is not None:
            return SegmentHelper.make_box_around_lines(self.current_group.headers)
        return None
