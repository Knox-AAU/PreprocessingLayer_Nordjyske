from alto_segment_lib.segment import Segment, SegmentType, Line
from alto_segment_lib.segment_lines.segment_lines import SegmentLines


def test_find_vertical_lines():
    headers = []
    paragraphs = []

    paragraphs.append(Segment([10,0,10,10], SegmentType.paragraph))
    paragraphs.append(Segment([10,15,10,30], SegmentType.paragraph))

    segment_lines = SegmentLines(paragraphs, headers)
    vertical_line = segment_lines.find_vertical_lines()

    assert vertical_line[0] == Line([10, 0, 10, 30])


def test_find_vertical_lines_not_aligned():
    headers = []
    paragraphs = []

    paragraphs.append(Segment([80, 0, 80, 10], SegmentType.paragraph))
    paragraphs.append(Segment([10, 15, 10, 30], SegmentType.paragraph))

    segment_lines = SegmentLines(paragraphs, headers)
    vertical_line = segment_lines.find_vertical_lines()

    assert vertical_line[0] == Line([80, 0, 80, 10])
    assert vertical_line[1] == Line([10, 15, 10, 30])