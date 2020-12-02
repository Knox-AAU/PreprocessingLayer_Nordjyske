from typing import List

from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.segment import Line
from alto_segment_lib.segment_helper import SegmentHelper


class SegmentLines:

    def find_vertical_lines(self, segments, image):
        # 1) - Find page bounds (Use existing function)
        # 2) - Try to merge as many
        # 2) - Find vertical lines: Loop all paragraphs:
        #         - Generate lines on the left-side of each element as long as the element is high.
        #         (line.x1 = paragraph.x1 - 2px, same for line.x2, Skip lines outside page bounds)
        #         - Loop the new lines
        #             - merge lines that align based on thres (Check for intersection, should maybe be multiple lines).
        #             - expand lines down and up (Until intersecting or outside page bounds)
        # 3) - Find horizontal lines: Loop all paragraphs.
        content_bound = SegmentHelper().get_content_bounds(segments)

        segments = sorted(segments, key=lambda segment: segments.x1)

        lines = self.__create_vertical_lines_for_each_segment(segments)

        LineExtractor().show_lines_on_image(image, lines)



    def __create_vertical_lines_for_each_segment(self, segments):
        """

        :rtype: Lines
        """
        lines = [List]
        for segment in segments:
            # make a line that is parallel with the left side of the segment
            lines.append(Line([segment.x1-2, segment.y1, segment.x1-2, segment.y2]))

        return lines























