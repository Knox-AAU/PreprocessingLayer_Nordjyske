from os import environ
from typing import List

from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.line_extractor.hough_bundler import HoughBundler
from alto_segment_lib.segment import Line
from alto_segment_lib.segment_helper import SegmentHelper

environ["OPENCV_IO_ENABLE_JASPER"] = "true"
import cv2


class SegmentLines:

    def find_vertical_lines(self, segments, filepath):
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

        segments = sorted(segments, key=lambda segment: segment.x1)
        image = cv2.imread(filepath, cv2.CV_8UC1)

        lines = self.__create_vertical_lines_for_each_segment(segments)

        LineExtractor().show_lines_on_image(image, lines, "beforeMerge")

        lines = self.__merge_vertical_lines(lines, segments)

        LineExtractor().show_lines_on_image(image, lines, "afterMerge")

    def __create_vertical_lines_for_each_segment(self, segments):
        """
        Creates a line to the left of every segment
        @param segments: List of all text segments
        @return: A list of lines
        """
        lines = []
        for segment in segments:
            # make a line that is parallel with the left side of the segment
            lines.append(Line([segment.x1 - 2, segment.y1, segment.x1 - 2, segment.y2]))

        return lines
    
    def __merge_vertical_lines(self, vertical_lines, segments):
        merged_lines = []
        merge_margin = 10
        
        # Finds similar lines 
        lines_to_be_merged = [[]]
        merged_lines = []
        merged_lines.clear()

        content_bound = SegmentHelper().get_content_bounds(segments)

        for line in vertical_lines:
            if self.__is_line_in_groups(lines_to_be_merged, line):
                continue
            
            found_lines = []

            for line_to_be_checked in vertical_lines:
                # Only checks if x1 is the same for the two lines, since their x1 and x2 are the same
                if line.x1 - merge_margin < line_to_be_checked.x1 < line.x1 + merge_margin:
                    found_lines.append(line_to_be_checked)

            lines_to_be_merged.append(found_lines)

        test = 0
        # Merges lines
        # Find statistics for line groups
        for line_group in lines_to_be_merged:
            sum_x = 0
            min_y = 100000
            max_y = 0

            if len(line_group) == 0:
                continue

            average_x = 0

            for line in line_group:
                sum_x += line.x1
                
                if line.y1 < min_y:
                    min_y = line.y1
                
                if line.y2 > max_y:
                    max_y = line.y2

            average_x = int(sum_x / len(line_group))

            # Finds affected segments
            affected_segments = []
            affected_segments.clear()

            for segment in segments:
                if segment.x1 < average_x < segment.x2\
                        and segment.y1 > min_y\
                        and segment.y2 < max_y:
                    affected_segments.append(segment)

            if len(affected_segments) == 0:
                merged_lines.append(Line([average_x, min_y, average_x, max_y]))


            else:
                # dont merge lines that intersect the segment
                i = 0
                affected_segments = sorted(affected_segments, key=lambda segment: segment.y1)
                for segment in affected_segments:
                    if i == 0:
                        merged_lines.append(Line([average_x, content_bound[1], average_x, segment.y1]))
                    elif i < len(affected_segments):
                        previous_segment = affected_segments[i - 1]
                        if previous_segment.y2 - segment.y1 > 150:
                            merged_lines.append(Line([average_x, previous_segment.y2, average_x, segment.y1]))
                    else:
                        merged_lines.append(Line([average_x, segment.y2, average_x, content_bound[3]]))

                    i += 1

        return merged_lines

    @staticmethod
    def __is_line_in_groups(lines_to_be_merged, line):
        for group in lines_to_be_merged:
            if group.__contains__(line):
                return True






















