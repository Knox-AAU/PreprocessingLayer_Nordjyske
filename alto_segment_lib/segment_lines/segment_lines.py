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

        lines = self.__fix_and_extend_vertical_lines(lines, segments)

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
            # lines.append(Line([segment.x2 + 2, segment.y1, segment.x2 + 2, segment.y2]))      # Lines on both sides of the segment

        return lines

    def __fix_and_extend_vertical_lines(self, vertical_lines, segments):
        merge_margin = 10
        final_lines = []
        content_bound = SegmentHelper().get_content_bounds(segments)

        # Finds similar lines
        lines_to_be_merged = self.__find_similar_lines(vertical_lines, merge_margin)

        # Merges lines
        for line_group in lines_to_be_merged:
            # Find statistics for line groups
            statistics = self.__get_statistics_for_line_group(line_group)
            min_y = statistics[0]
            max_y = statistics[1]
            average_x = statistics[2]

            # Finds affected segments
            affected_segments = self.__find_affected_segments_between_lines(segments, min_y, max_y, average_x)
            all_affected_segments = self.__find_affected_segments(segments, min_y, max_y, average_x)

            if len(affected_segments) == 0 or len(line_group) == 1:
                final_lines.append(Line([average_x, min_y, average_x, max_y]))
            else:
                wip_merged_lines = self.__merge_all_lines_not_intersecting_segment(line_group, all_affected_segments)
                extended_to_bounds_lines = self.__extend_lines(wip_merged_lines, all_affected_segments, content_bound)
                # extended_lines = extended_to_bounds_lines
                extended_lines = self.__extend_lines_to_segment_borders(extended_to_bounds_lines, all_affected_segments)

                for line in extended_lines:
                    final_lines.append(line)

        return final_lines

    @staticmethod
    def __is_line_in_groups(lines_to_be_merged, line):
        for group in lines_to_be_merged:
            if group.__contains__(line):
                return True

    def __find_similar_lines(self, vertical_lines, merge_margin):
        lines_to_be_merged = [[]]

        for line in vertical_lines:
            if self.__is_line_in_groups(lines_to_be_merged, line):
                continue

            found_lines = []

            for line_to_be_checked in vertical_lines:
                # Only checks if x1 is the same (plus margin) for the two lines, since their x1 and x2 are the same
                if line.x1 - merge_margin < line_to_be_checked.x1 < line.x1 + merge_margin:
                    found_lines.append(line_to_be_checked)

            lines_to_be_merged.append(found_lines)

        return lines_to_be_merged

    @staticmethod
    def __get_statistics_for_line_group(line_group):
        if len(line_group) == 0:
            return 0, 0, 0

        sum_x = 0
        min_y = -1
        max_y = 0

        for line in line_group:
            sum_x += line.x1

            if line.y1 < min_y or min_y == -1:
                min_y = line.y1

            if line.y2 > max_y:
                max_y = line.y2

        average_x = int(sum_x / len(line_group))

        return min_y, max_y, average_x

    @staticmethod
    def __find_affected_segments(segments, min_y, max_y, x_cord):
        affected_segments = []

        for segment in segments:
            if segment.x1 < x_cord < segment.x2:
                affected_segments.append(segment)

        return affected_segments

    @staticmethod
    def __find_affected_segments_between_lines(segments, min_y, max_y, x_cord):
        affected_segments = []

        for segment in segments:
            if segment.x1 < x_cord < segment.x2 \
                    and segment.y1 > min_y \
                    and segment.y2 < max_y:
                affected_segments.append(segment)

        return affected_segments

    @staticmethod
    def __find_segments_above_line(line, segments):
        segments_above_line = []

        for segment in segments:
            if segment.y1 < line.y1:
                segments_above_line.append(segment)

        return segments_above_line

    def __find_segments_below_line(self, line, segments):
        segments_below_line = []

        for segment in segments:
            if segment.y1 > line.y2:
                segments_below_line.append(segment)

        return segments_below_line

    @staticmethod
    def __merge_two_lines(line1, line2):
        return Line([line1.x1, line1.y1, line2.x2, line2.y2])

    def __merge_all_lines_not_intersecting_segment(self, lines, segments):
        if len(lines) <= 1:
            return lines

        lines = sorted(lines, key=lambda line: line.y1)

        merged_lines = self.__merge_lines(lines, segments)

        previous_merged_line_count = 0
        while previous_merged_line_count != len(merged_lines):
            previous_merged_line_count = len(merged_lines)

            merged_lines = self.__merge_lines(merged_lines, segments)
            merged_lines = sorted(merged_lines, key=lambda line: line.y1)

        return merged_lines

    def __merge_lines(self, lines, segments):
        if len(lines) <= 1:
            return lines
        i = 0
        merged_lines = []

        for line in lines:
            if i == 0:
                i += 1
                merged_lines.append(line)
                continue
            previous_line = lines[i-1]

            if self.__is_any_segment_intersected(segments, previous_line.y2, line.y1):
                merged_lines.append(line)
            else:
                merged_lines.append(Line([line.x1, previous_line.y1, line.x1, line.y2]))
            i += 1

        return merged_lines

    def __is_any_segment_intersected(self, segments, min_y, max_y):
        for segment in segments:
            if self.__is_segment_intersected(segment, min_y, max_y):
                return True
        return False

    @staticmethod
    def __is_segment_intersected(segment, min_y, max_y):
        # Line going through segment
        if min_y < segment.y1 and max_y > segment.y2:
            return True

        # Line goes through top or bottom of the segment
        elif min_y < segment.y1 < max_y:
            return True
        elif min_y < segment.y2 < max_y:
            return True

        else:
            return False

    def __extend_lines(self, lines, segments, content_bound):
        extended_lines = []

        highest_line = min(lines, key=lambda line: line.y1)
        lowest_line = max(lines, key=lambda line: line.y2)

        for line in lines:
            if line != highest_line or line != lowest_line:
                extended_lines.append(line)

        if not self.__find_segments_above_line(highest_line, segments):
            extended_lines.append(Line([highest_line.x1, content_bound[1], highest_line.x2, highest_line.y2]))

        if not self.__find_segments_below_line(lowest_line, segments):
            extended_lines.append(Line([lowest_line.x1, lowest_line.y1, lowest_line.x2, content_bound[3]]))

        return extended_lines

    def __extend_lines_to_segment_borders(self, lines, segments):
        extended_lines = []

        for line in lines:
            y1 = 0
            y2 = 0

            above_segments = self.__find_segments_above_line(line, segments)
            if len(above_segments) == 0:
                y1 = line.y1
            else:
                above_segment = max(above_segments, key=lambda segment: segment.y2)
                y1 = above_segment.y2

            below_segments = self.__find_segments_below_line(line, segments)
            if len(below_segments) == 0:
                y2 = line.y2
            else:
                below_segment = min(below_segments, key=lambda segment: segment.y1)
                y2 = below_segment.y1

            extended_lines.append(Line([line.x1, y1, line.x2, y2]))

        return extended_lines






