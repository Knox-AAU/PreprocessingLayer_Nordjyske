import math
from enum import Enum


class SegmentType(Enum):
    """The types a segment can be."""
    paragraph = 1
    heading = 2
    line = 3
    unknown = 4


class Segment:
    """
    todo
    """
    type: SegmentType
    x1: int
    y1: int
    x2: int
    y2: int
    lines: list

    def __init__(self, coord: list = None, seg_type: SegmentType = SegmentType.unknown):
        self.lines = []

        if coord is None:
            coord = []

        if len(coord) == 4:
            self.x1 = coord[0]
            self.y1 = coord[1]
            self.x2 = coord[2]
            self.y2 = coord[3]
        else:
            self.x1 = 0
            self.y1 = 0
            self.x2 = 0
            self.y2 = 0

        self.type = seg_type

    def compare(self, other: object):
        """
        Compares two segments to see if they are the same based on their coordinates

        @param other: The segment to compare self to
        @return: Boolean (whether the segments are equal)
        """
        return isinstance(other, Segment) and (self.x1 == other.x1 and self.y1 == other.y1
                                               and self.x2 == other.x2 and self.y2 == other.y2)

    def between_x_coordinates(self, value: int, margin: int = 0):
        """
        Check if a value is between x1 and x2 of the segment with the given margin

        @param value: The value to be checked
        @param margin: Margin subtracted and added to x1 and x2 respectively
        @return: Boolean (Whether the value is between x1 and x2)
        """
        return (self.x1 * (1 - margin)) <= value <= (self.x2 * (1 + margin))

    def between_y_coordinates(self, value: int, margin: int = 0):
        """
        Check if a value is between y1 and y2 of the segment with the given margin

        @param value: The value to be checked
        @param margin: Margin subtracted and added to y1 and y2 respectively
        @return: Boolean (Whether the value is between y1 and y2)
        """
        return (self.y1 * (1 - margin)) <= value <= (self.y2 * (1 + margin))

    def width(self):
        """
        Get the width of the segment

        @return: Width of the segment
        """
        return self.x2 - self.x1

    def height(self):
        """
        Get the height of the segment

        @return: Height of the segment
        """
        return self.y2 - self.y1

    def add_line(self, line: object):
        """
        Adds the line to the lines of the segment

        @param line: The line to add
        @return: void
        """
        self.lines.append(line)

    def get_center(self):
        """
        Get the center of the segment

        @return: Center of the segment
        """
        return (self.x2 - (self.x2 - self.x1) / 2), (self.y2 - (self.y2 - self.y1) / 2)

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


class Line:
    """
    todo
    """
    x1: int
    y1: int
    x2: int
    y2: int
    font: float
    block_segment: Segment

    def __init__(self, coord: list = None, font: float = None, block_segment: Segment = None):
        if coord is None:
            coord = []

        if len(coord) == 4:
            self.x1 = coord[0]
            self.y1 = coord[1]
            self.x2 = coord[2]
            self.y2 = coord[3]
            self.length = math.sqrt(math.pow((self.x2 - self.x1), 2) + math.pow((self.y2 - self.y1), 2))
            self.orientation = self.get_orientation()

        self.font = font
        self.block_segment = block_segment

    def width(self):
        """
        Get the width of the segment

        @return: Width of the segment
        """
        return self.x2 - self.x1

    def height(self):
        """
        Get the height of the segment

        @return: height of the segment
        """
        return self.y2 - self.y1

    def is_box_horizontal(self):
        """
        Checks if the box of the line is horizontal

        @return: Boolean (whether the box is horizontal)
        """
        return self.x2 - self.x1 > self.y2 - self.y1

    def to_array(self) -> list:
        """
        Returns the coordinates of the line as an array
        @return: list
        """
        return [self.x1, self.y1, self.x2, self.y2]

    @classmethod
    def from_array(cls, array):
        """
        Creates line from array

        @param array: Array of 4 values representing the x1, y1, x2, and y2 coordinates of the resulting line
        @return: Line generated from the array
        """
        return Line([array[0], array[1], array[2], array[3]])

    def get_orientation(self):
        """
        Gets orientation of a line, using its length
        https://en.wikipedia.org/wiki/Atan2

        @return Orientation of the line as a float
        """
        orientation = math.atan2(abs((self.x1 - self.x2)), abs((self.y1 - self.y2)))
        return math.degrees(orientation)

    def __eq__(self, other: object):
        """
        Checks if the two lines are equal based on their coordinates

        @param other: Line to be compared with
        @return: Boolean (the equality of the lines)
        """
        return isinstance(other, Line) and (self.x1 == other.x1 and self.y1 == other.y1
                                            and self.x2 == other.x2 and self.y2 == other.y2)

    def is_horizontal(self):
        """
        Checks if the line is horizontal

        @return: Boolean (whether the line is horizontal or not)
        """
        orientation = self.get_orientation()
        # if horizontal
        return 45 < orientation < 135

    def is_horizontal_or_vertical(self):
        """
        Checks if the line is horizontal or vertical

        @return: Boolean (whether the line is either horizontal or vertical, or not)
        """
        orientation = self.get_orientation()
        # if horizontal
        return 85 <= orientation <= 95 or 0 <= orientation <= 20

    def between_x_coordinates(self, value: int, margin: float = 0.0):
        """
        Check if a value is between x1 and x2 of the line with the given margin

        @param value: The value to be checked
        @param margin: Margin subtracted and added to x1 and x2 respectively
        @return: Boolean (Whether the value is between x1 and x2)
        """
        return (self.x1 * (1 - margin)) <= value <= (self.x2 * (1 + margin))

    def between_y_coordinates(self, value: int, margin: int = 0):
        """
        Check if a value is between x1 and x2 of the line with the given margin

        @param value: The value to be checked
        @param margin: Margin subtracted and added to x1 and x2 respectively
        @return: Boolean (Whether the value is between x1 and x2)
        """
        return (self.y1 * (1 - margin)) <= value <= (self.y2 * (1 + margin))


class SegmentGroup:
    """
    todo
    """
    headers: list[Line]
    paragraphs: list[Segment]

    def __init__(self):
        self.headers = []
        self.paragraphs = []
