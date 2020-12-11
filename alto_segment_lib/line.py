import math


class Line:
    """
    A line is a combination of two coordinates, with relevant methods.
    """
    x1: int
    y1: int
    x2: int
    y2: int

    def __init__(self, coord: list = None, block_segment = None):
        if coord is None:
            coord = []

        if len(coord) == 4:
            self.x1 = coord[0]
            self.y1 = coord[1]
            self.x2 = coord[2]
            self.y2 = coord[3]
            self.length = math.sqrt(math.pow((self.x2 - self.x1), 2) + math.pow((self.y2 - self.y1), 2))
            self.orientation = self.get_orientation()
        self.block_segment = block_segment

    def width(self):
        """
        Gets the width of the segment

        @return: Width of the segment
        """
        return self.x2 - self.x1

    def height(self):
        """
        Gets the height of the segment

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
        Using: https://en.wikipedia.org/wiki/Atan2

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

    def __repr__(self):
        """
        Makes a string representation of the coordinates
        @return: string representation
        """
        return str(self.to_array())

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

    def get_center(self):
        """
        Gets the center of the segment

        @return: Center of the segment
        """
        return (self.x2 - (self.x2 - self.x1) / 2), (self.y2 - (self.y2 - self.y1) / 2)
