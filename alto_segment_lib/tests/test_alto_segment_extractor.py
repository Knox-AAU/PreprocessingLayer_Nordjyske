from alto_segment_lib.alto_segment_extractor import *

class TestAltoSegmentExtractor:

    def test_inch1200_to_px_conversion_success(self):
        extractor = AltoSegmentExtractor()
        extractor.set_dpi(300)
        inch1200 = 14500

        assert extractor.inch1200_to_px(inch1200) == 3625

    def test_inch1200_to_px_conversion_failed(self):
        extractor = AltoSegmentExtractor()
        extractor.set_dpi(300)
        inch1200 = 14000

        assert not extractor.inch1200_to_px(inch1200) == 3625

    def test_determine_most_frequent_list_element_success(self):
        list_of_names = ['hans', 'hanne', 'flemming', 'hans', 'ole', 'hans']

        most_frequent_element = determine_most_frequent_list_element(list_of_names)

        assert most_frequent_element == "hans"

    def test_determine_most_frequent_list_element_failed(self):
        list_of_names = ['hans', 'hanne', 'flemming', 'hans', 'ole', 'hans']

        most_frequent_element = determine_most_frequent_list_element(list_of_names)

        assert not most_frequent_element == "ole"
