from alto_segment_lib.segment import Segment, SegmentType, Line
from alto_segment_lib.segment_lines.segment_lines import SegmentLines


def test_find_vertical_lines():
    # Arrange
    headers = []
    paragraphs = []
    margin = 2

    paragraphs.append(Segment([10, 0, 101, 10], SegmentType.paragraph))
    paragraphs.append(Segment([10, 15, 1000, 30], SegmentType.paragraph))

    # Act
    segment_lines = SegmentLines(paragraphs, headers)
    vertical_line = segment_lines.find_vertical_lines()

    # Assert
    assert vertical_line[0] == Line([10 - margin, 0, 10 - margin, 30])


def test_find_vertical_lines_not_aligned():
    # Arrange
    headers = []
    paragraphs = []
    margin = 2

    paragraphs.append(Segment([80, 0, 800, 10], SegmentType.paragraph))
    paragraphs.append(Segment([10, 15, 1000, 30], SegmentType.paragraph))

    # Act
    segment_lines = SegmentLines(paragraphs, headers)
    vertical_line = segment_lines.find_vertical_lines()

    # Assert
    assert vertical_line[0] == Line([80 - margin, 0, 80 - margin, 10])
    assert vertical_line[2] == Line([10 - margin, 15, 10 - margin, 30])


def test_find_vertical_lines_far_apart():
    # Arrange
    headers = []
    paragraphs = []
    margin = 2

    paragraphs.append(Segment([10, 0, 101, 10], SegmentType.paragraph))
    paragraphs.append(Segment([10, 300, 1001, 1000], SegmentType.paragraph))

    # Act
    segment_lines = SegmentLines(paragraphs, headers)
    vertical_line = segment_lines.find_vertical_lines()

    # Assert
    assert vertical_line[0] == Line([10 - margin, 0, 10 - margin, 1000])


def test_find_vertical_lines_merge_lines_within_margin():
    # Arrange
    headers = []
    paragraphs = []
    margin = 2

    paragraphs.append(Segment([13, 0, 130, 10], SegmentType.paragraph))
    paragraphs.append(Segment([10, 30, 100, 100], SegmentType.paragraph))
    average_x = int((13 - margin + 10 - margin) / 2)

    # Act
    segment_lines = SegmentLines(paragraphs, headers)
    vertical_line = segment_lines.find_vertical_lines()

    # Assert
    assert vertical_line[0] == Line([average_x, 0, average_x, 100])


def test_find_vertical_lines_intersects_segment():
    # Arrange
    headers = []
    paragraphs = []
    margin = 2

    paragraphs.append(Segment([40, 15, 1000, 100], SegmentType.paragraph))
    paragraphs.append(Segment([40, 400, 1000, 500], SegmentType.paragraph))
    paragraphs.append(Segment([10, 200, 10000, 300], SegmentType.paragraph))

    # Act
    segment_lines = SegmentLines(paragraphs, headers)
    vertical_line = segment_lines.find_vertical_lines()

    # Assert
    assert vertical_line[0] == Line([40 - margin, 15, 40 - margin, 200])
    assert vertical_line[1] == Line([40 - margin, 300, 40 - margin, 500])

def test_find_vertical_lines_merge_lines():
    # Arrange
    headers = []
    paragraphs = []
    margin = 2

    paragraphs.append(Segment([40, 15, 1000, 100], SegmentType.paragraph))
    paragraphs.append(Segment([40, 25, 1000, 80], SegmentType.paragraph))

    # Act
    segment_lines = SegmentLines(paragraphs, headers)
    vertical_line = segment_lines.find_vertical_lines()

    # Assert
    assert vertical_line[0] == Line([40 - margin, 15, 1000 - margin, 100])


def test_find_horizontal_lines_extend_horizontal_lines_to_vertical_lines():
    # Arrange
    headers = []
    paragraphs = []
    margin = 2

    paragraphs.append(Segment([10, 0, 100, 1000], SegmentType.paragraph))
    paragraphs.append(Segment([400, 0, 500, 1000], SegmentType.paragraph))

    headers.append(Segment([150, 100, 250, 150], SegmentType.heading))

    # Act
    segment_lines = SegmentLines(paragraphs, headers)
    horizontal_lines = segment_lines.find_vertical_and_horizontal_lines()

    # Assert
    assert horizontal_lines[0] == Line([100 + margin, 100, 400 - margin, 100])

def test_find_horizontal_lines_extend_horizontal_lines_to_page_bound():
    # Arrange
    headers = []
    paragraphs = []

    paragraphs.append(Segment([0, 0, 1000, 0], SegmentType.paragraph))

    headers.append(Segment([150, 100, 250, 150], SegmentType.heading))

    # Act
    segment_lines = SegmentLines(paragraphs, headers)
    horizontal_lines = segment_lines.find_vertical_and_horizontal_lines()

    # Assert
    assert horizontal_lines[0] == Line([0, 100, 1000, 100])



