from alto_segment_lib.segment import SegmentType, Segment


class SegmentGroup:
    """
    todo
    """
    type: str
    x1: int
    y1: int
    x2: int
    y2: int
    lines: list

    def to_segment(self, segment_type: SegmentType):
        """
        Converts the line to a segment

        @param segment_type: The type of the resulting segment
        @return: The line as a segment
        """
        return Segment([self.x1, self.y1, self.x2, self.y2], segment_type)