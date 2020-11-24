import math


class Segment:
    type: str
    x1: int
    y1: int
    x2: int
    y2: int
    lines: list

    def __init__(self, coord: list = None, seg_type: str = "unknown"):
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

    def compare(self, segment):
        if not isinstance(segment, Segment):
            return False
        return (self.x1 == segment.x1 and self.y1 == segment.y1
                and self.x2 == segment.x2 and self.y2 == segment.y2)

    def between_x_coords(self, coord: int, margin: int = 0):
        return (self.x1 * (1 - margin)) <= coord <= (self.x2 * (1 + margin))

    def between_y_coords(self, coord: int, margin: int = 0):
        return (self.y1 * (1 - margin)) <= coord <= (self.y2 * (1 + margin))

    def width(self):
        return self.x2 - self.x1

    def height(self):
        return self.y2 - self.y1

    def add_line(self, line):
        self.lines.append(line)

    def calculate_coordinates(self):
        if len(self.lines) == 0:
            return None

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
    x1: int
    y1: int
    x2: int
    y2: int
    font: float

    def __init__(self, coord: list = None, font: float = None):
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

    def width(self):
        return self.x2 - self.x1

    def height(self):
        return self.y2 - self.y1

    def is_box_horizontal(self):
        if (self.x2 - self.x1) > (self.y2 - self.y1):
            return True

    @classmethod
    def from_array(cls, array):
        return Line([array[0], array[1], array[2], array[3]])

    def get_orientation(self):
        """get orientation of a line, using its length
        https://en.wikipedia.org/wiki/Atan2
        """
        orientation = math.atan2(abs((self.x1 - self.x2)), abs((self.y1 - self.y2)))
        return math.degrees(orientation)

    def __eq__(self, other):
        return self.x1 == other.x1 and self.y1 == other.y1 and self.x2 == other.x2 and self.y2 == other.y2

    def is_horizontal(self):
        orientation = self.get_orientation()
        # if horizontal
        if 45 < orientation < 135:
            return True

    def is_horizontal_or_vertical(self):
        orientation = self.get_orientation()
        # if horizontal
        if 85 <= orientation <= 95:
            return True
        elif 0 <= orientation <= 20:
            return True

        return False

    def between_x_coords(self, coord: int, margin: float = 0.0):
        return (self.x1 * (1 - margin)) <= coord <= (self.x2 * (1 + margin))

    def between_y_coords(self, coord: int, margin: int = 0):
        return (self.y1 * (1 - margin)) <= coord <= (self.y2 * (1 + margin))


class SegmentGroup:
    headers: list[Segment]
    paragraphs: list[Segment]

    def __init__(self):
        self.headers = []
        self.paragraphs = []

    def between_x_coords(self, coord: int, margin: float = 0.0):
        return (self.x1 * (1 - margin)) <= coord <= (self.x2 * (1 + margin))

    def between_y_coords(self, coord: int, margin: int = 0):
        return (self.y1 * (1 - margin)) <= coord <= (self.y2 * (1 + margin))
