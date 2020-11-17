from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.segment import Line


def test_filter_by_angle_diversion_from_horizontal_and_vertical():
    #arrange
    lines = [
        Line(0,0,10,0), #horizontal
        Line(0,0,1,3), #horizontal but not enough
        Line(0,0,1,1), #45 degrees
        Line(0,0,0,10), #vertical
        Line(0,0,3,1), #vertical but not enough
    ]
    le = LineExtractor()
    le.diversion = 5 # max 5 degrees instead of loading from config

    #act
    result_lines = le.filter_by_angle_diversion_from_horizontal_and_vertical(lines)

    #assert
    assert lines[0] in result_lines
    assert lines[1] not in result_lines
    assert lines[2] not in result_lines
    assert lines[3] in result_lines
    assert lines[4] not in result_lines
