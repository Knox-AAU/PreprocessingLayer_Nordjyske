from enum import Enum
from typing import List


from alto_segment_lib.line import Line


class SegmentType(Enum):
    """The types a segment can be."""
    paragraph = 1
    heading = 2
    line = 3
    unknown = 4


class Segment(Line):
    """
    Segment is a set of two coordinates, combined with a SegmentType and optionally a list of coords.
    """
    type: SegmentType
    lines: list

    def __init__(self, coord: list = None, seg_type: SegmentType = SegmentType.unknown):
        super().__init__(coord)
        self.lines = []
        self.type = seg_type

    def add_line(self, line: object):
        """
        Adds the line to the lines of the segment

        @param line: The line to add
        @return: void
        """
        self.lines.append(line)

    def update_coordinates_based_on_lines(self):
        """
        Updates the coordinates of the segment based on the coordinates of its internal lines

        @return: void
        """
        if len(self.lines) == 0:
            return

        self.x1 = self.lines[0].x1
        self.x2 = self.lines[0].x2
        self.y1 = self.lines[0].y1
        self.y2 = self.lines[0].y2

        # Finds width and height line and change box height and width accordingly
        for line in self.lines:
            # Find x-coordinate upper left corner
            if line.x1 < self.x1:
                self.x1 = line.x1

            # Find x-coordinate lower right corner
            if line.x2 > self.x2:
                self.x2 = line.x2

            # Find y-coordinate upper left corner
            if line.y1 < self.y1:
                self.y1 = line.y1

            # Find y-coordinate lower right corner
            if line.y2 > self.y2:
                self.y2 = line.y2

    @classmethod
    def to_segment(cls, line: Line, segment_type: SegmentType):
        """
        Converts the line to a segment

        @param segment_type: The type of the resulting segment
        @return: The line as a segment
        """
        return cls([line.x1,line.y1,line.x2,line.y2], segment_type)


class SegmentGroup:
    """
    todo
    """
    headers: List[Segment]
    paragraphs: List[Segment]

    def __init__(self):
        self.headers = []
        self.paragraphs = []
