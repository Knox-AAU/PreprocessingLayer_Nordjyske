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

    paragraphs.append(Segment([13, 0, 130, 10], SegmentType.paragraph))
    paragraphs.append(Segment([10, 30, 100, 100], SegmentType.paragraph))

    # Act
    segment_lines = SegmentLines(paragraphs, headers)
    vertical_line = segment_lines.find_vertical_lines()

    # Assert


