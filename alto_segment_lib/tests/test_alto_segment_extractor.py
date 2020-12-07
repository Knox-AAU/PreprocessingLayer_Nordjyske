from alto_segment_lib.alto_segment_extractor import *

class TestAltoSegmentExtractor:

    def test_inch1200_to_px_conversion_success(self):
        extractor = AltoSegmentExtractor()
        extractor.dpi = 300
        inch1200 = 14500

        assert extractor.inch1200_to_px(inch1200) == 3625

    def test_inch1200_to_px_conversion_failed(self):
        extractor = AltoSegmentExtractor()
        extractor.dpi = 300
        inch1200 = 14000

        assert not extractor.inch1200_to_px(inch1200) == 3625
