from unittest.mock import Mock

import pytest

from alto_segment_lib.alto_segment_extractor import *


alto_segment_extractor = AltoSegmentExtractor()


@pytest.fixture(autouse=True)
def run_around_tests():
    # Code that will run before every test:
    global alto_segment_extractor
    alto_segment_extractor = AltoSegmentExtractor()
    alto_segment_extractor.dpi = 1200  # will ignore
    alto_segment_extractor.margin = 0 # in case config file changes.
    yield
    # Code that will run after every test:
    pass # Nothing to run after every test.

class PseudoValue:
    def __init__(self, value):
        self.value = value


def test_inch1200_to_px_conversion_success():
    extractor = AltoSegmentExtractor()
    extractor.dpi = 300
    inch1200 = 14500

    assert extractor.inch1200_to_px(inch1200) == 3625


def test_inch1200_to_px_conversion_failed():
    extractor = AltoSegmentExtractor()
    extractor.dpi = 300
    inch1200 = 14000

    assert not extractor.inch1200_to_px(inch1200) == 3625


def test_extract_lines():
    line_1 = Mock()
    line_1.attributes = {
        "HPOS": PseudoValue(0),
        "VPOS": PseudoValue(1),
        "WIDTH": PseudoValue(100),
        "HEIGHT": PseudoValue(100)}

    block_1 = Mock()
    block_1.attributes = {
        "HPOS": PseudoValue(0),
        "VPOS": PseudoValue(1),
        "WIDTH": PseudoValue(100),
        "HEIGHT": PseudoValue(100)
    }
    block_1.getElementsByTagName.return_value = [line_1]

    global alto_segment_extractor
    alto_segment_extractor._AltoSegmentExtractor__xml_doc = Mock()
    alto_segment_extractor._AltoSegmentExtractor__xml_doc.getElementsByTagName.return_value = [block_1]

    result_lines = alto_segment_extractor.extract_lines()

    array_lines = [line.to_array() for line in result_lines]

    assert array_lines == [[0, 1, 100, 101]]


def test_extract_lines_block_segment_success():
    line_1 = Mock()
    line_1.attributes = {
        "HPOS": PseudoValue(1),
        "VPOS": PseudoValue(2),
        "WIDTH": PseudoValue(2),
        "HEIGHT": PseudoValue(2)}

    line_2 = Mock()
    line_2.attributes = {
        "HPOS": PseudoValue(5),
        "VPOS": PseudoValue(6),
        "WIDTH": PseudoValue(2),
        "HEIGHT": PseudoValue(2)}

    block_1 = Mock()
    block_1.attributes = {
        "HPOS": PseudoValue(9),
        "VPOS": PseudoValue(10),
        "WIDTH": PseudoValue(2),
        "HEIGHT": PseudoValue(2)
    }
    block_1.getElementsByTagName.return_value = [line_1, line_2]

    global alto_segment_extractor
    alto_segment_extractor._AltoSegmentExtractor__xml_doc = Mock()
    alto_segment_extractor._AltoSegmentExtractor__xml_doc.getElementsByTagName.return_value = [block_1]

    result_lines = alto_segment_extractor.extract_lines()

    assert len(result_lines) == 2
    assert result_lines[0] == Line([1, 2, 3, 4])
    assert result_lines[1] == Line([5, 6, 7, 8])
    assert result_lines[0].block_segment == result_lines[1].block_segment
    assert result_lines[0].block_segment == Segment([9, 10, 11, 12])
    assert len(result_lines[0].block_segment.lines) == 2
    assert result_lines[0].block_segment.lines[0] == Line([1, 2, 3, 4])
    assert result_lines[0].block_segment.lines[1] == Line([5, 6, 7, 8])

def test_extract_lines_margin_success():
    line_1 = Mock()
    line_1.attributes = {
        "HPOS": PseudoValue(0),
        "VPOS": PseudoValue(0),
        "WIDTH": PseudoValue(1),
        "HEIGHT": PseudoValue(1)}

    block_1 = Mock()
    block_1.attributes = {
        "HPOS": PseudoValue(9),
        "VPOS": PseudoValue(10),
        "WIDTH": PseudoValue(2),
        "HEIGHT": PseudoValue(2)
    }
    block_1.getElementsByTagName.return_value = [line_1]

    global alto_segment_extractor
    alto_segment_extractor._AltoSegmentExtractor__xml_doc = Mock()
    alto_segment_extractor.margin = 1
    alto_segment_extractor._AltoSegmentExtractor__xml_doc.getElementsByTagName.return_value = [block_1]

    result_lines = alto_segment_extractor.extract_lines()

    assert len(result_lines) == 1
    assert result_lines[0] == Line([-1,-1,2,2])
