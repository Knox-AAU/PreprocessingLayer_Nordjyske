from os import environ
from typing import List
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.segment import Line, SegmentType, Segment
from alto_segment_lib.segment_helper import SegmentHelper


class SegmentLines:

    def __init__(self, paragraphs, headers):
        """
        Sets some internal properties.
        @param paragraphs: A list of paragraph segments
        @param headers: A list of header segments
        """
        self.paragraphs = paragraphs
        self.headers = headers
        self.vertical_lines = []
        content_bound = SegmentHelper().get_content_bounds(paragraphs+headers)
        self.page_x1 = content_bound[0]
        self.page_y1 = content_bound[1]
        self.page_x2 = content_bound[2]
        self.page_y2 = content_bound[3]

    def find_vertical_and_horizontal_lines(self) -> List[Line]:
        """
        Finds the horizontal lines from the given segments and returns them.
        @return: A list of horizontal lines
        """
        vertical_lines = self.find_vertical_lines()
        self.vertical_lines = vertical_lines
        horizontal_lines = self.__find_horizontal_lines()

        return horizontal_lines, vertical_lines

    def __find_horizontal_lines(self):
        """
        Finds horizontal lines from the segments, and processes them to return the extended ones
        @return: A list of horizontal lines
        """
        horizontal_lines = self.__make_line_over_headers()
        horizontal_lines = self.__extend_horizontal_lines(horizontal_lines)

        return horizontal_lines

    def __make_line_over_headers(self):
        """
        Creates lines over the header segments
        @return: A list of basic horizontal lines
        """
        horizontal_lines = []
        margin = 2
        for header in self.headers:
            horizontal_lines.append(Line([header.x1, header.y1 - margin, header.x2, header.y1 - margin]))

        return horizontal_lines

    def __extend_horizontal_lines(self, horizontal_lines):
        """
        Extends horizontal lines the nearest vertical line on both sides
        @param horizontal_lines:
        @return:
        """
        extended_horizontal_lines = []
        margin = 2

        for horizontal_line in horizontal_lines:
            left_line, right_line = self.find_nearest_vertical_lines(horizontal_line, self.vertical_lines)
            extended_horizontal_lines.append(Line([left_line.x1, horizontal_line.y1 + margin, right_line.x1, horizontal_line.y2 + margin]))

        return extended_horizontal_lines

    def find_nearest_vertical_lines(self, horizontal_line, vertical_lines):
        """
        Finds the closest vertical line to the left and right of the horizontal line
        @param horizontal_line: A horizontal line
        @param vertical_lines: A list of vertical lines
        @return: The closest vertical line to the left and right of the horizontal line
        """
        vertical_lines.sort(key=lambda line: line.x1)

        left_side_lines = []
        right_side_lines = []

        for vertical_line in vertical_lines:
            # Line has to be left of the line and intersect it
            if vertical_line.x1 < horizontal_line.x1\
                    and vertical_line.y1 < horizontal_line.y1\
                    and vertical_line.y2 > horizontal_line.y2:
                left_side_lines.append(vertical_line)
            elif vertical_line.x1 > horizontal_line.x2 \
                    and vertical_line.y1 < horizontal_line.y1 \
                    and vertical_line.y2 > horizontal_line.y2:
                right_side_lines.append(vertical_line)
        # If empty then add a line along the pages content bound
        if len(left_side_lines) == 0:
            left_side_lines.append(Line([self.page_x1, self.page_y1,
                                         self.page_x1, self.page_y2]))
        if len(right_side_lines) == 0:
            right_side_lines.append(Line([self.page_x2, self.page_y1,
                                         self.page_x2, self.page_y2]))

        return min(left_side_lines, key=lambda line: horizontal_line.x1 - line.x1), min(right_side_lines, key=lambda line: line.x1 - horizontal_line.x1)

    def find_vertical_lines(self):
        """
        Finds all vertical lines from the segments, depending on the segments.
        @return: A list of vertical lines
        """
        segments = self.paragraphs + self.headers

        segments.sort(key=lambda segment: segment.x1)

        lines = self.__create_vertical_lines_for_each_segment(self.paragraphs)

        lines = self.__fix_and_extend_vertical_lines(lines, segments)

        return lines

    @staticmethod
    def __create_vertical_lines_for_each_segment(segments):
        """
        Creates a line to the left of every segment
        @param segments: List of all text segments
        @return: A list of lines
        """
        lines = []
        margin = 2
        for segment in segments:
            if segment.type == SegmentType.paragraph:
                # Make a line that is parallel with the left side of the segment
                lines.append(Line([segment.x1 - margin, segment.y1, segment.x1 - margin, segment.y2]))
                lines.append(Line([segment.x2 + margin, segment.y1, segment.x2 + margin, segment.y2]))      # Lines on both sides of the segment

        return lines

    def __fix_and_extend_vertical_lines(self, vertical_lines, segments):
        """
        Merges similar lines, extends them to page bounds, extends them to the nearest segments and finally removing
        duplicate lines
        @param vertical_lines: A list of vertical lines
        @param segments: A list of segments
        @return: A list of finalized vertical lines
        """
        merge_margin = 30
        final_lines = []

        # Finds similar lines
        lines_to_be_merged = self.__find_similar_lines(vertical_lines, merge_margin)

        # Merges lines
        for line_group in lines_to_be_merged:
            # Find statistics for line groups
            (min_y, max_y, average_x) = self.__get_statistics_for_line_group(line_group)

            # Finds affected segments
            affected_segments = self.__find_affected_segments_between_lines(segments, min_y, max_y, average_x)
            all_affected_segments = self.__find_affected_segments(segments, average_x)

            if len(affected_segments) == 0 or len(line_group) == 1:
                final_lines.append(Line([average_x, min_y, average_x, max_y]))
            else:
                merged_lines = self.__merge_all_lines_not_intersecting_segment(line_group, all_affected_segments)
                extended_to_bounds_lines = self.__extend_vertical_lines(merged_lines, all_affected_segments)
                extended_lines = self.__extend_lines_to_segment_borders(extended_to_bounds_lines, all_affected_segments)
                fixed_lines = self.__merge_similar_lines(extended_lines)

                for line in fixed_lines:
                    final_lines.append(line)

        return final_lines

    @staticmethod
    def __is_line_in_groups(lines_to_be_merged, line):
        """
        Checks if a group is in any group of a list of groups of lines
        @param lines_to_be_merged: A list of groups of lines
        @param line: A line
        @return: True if the any group contains the line, and False otherwise
        """
        for group in lines_to_be_merged:
            if group.__contains__(line):
                return True

    def __find_similar_lines(self, vertical_lines, merge_margin):
        lines_to_be_merged = []

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
        """
        Fetches some key statistics for a line group used for merging and extending lines
        @param line_group: A list of lines
        @return: The minimum y-value, maximum y-value and average x-value for the line group
        """
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
    def __find_affected_segments(segments, x_cord):
        """
        Finds all encountered segments on an x-cord
        @param segments: A list of segments
        @param x_cord: An x coordinate
        @return: All the encountered segments
        """
        affected_segments = []

        for segment in segments:
            if segment.x1 < x_cord < segment.x2:
                affected_segments.append(segment)

        return affected_segments

    @staticmethod
    def __find_affected_segments_between_lines(segments, min_y, max_y, x_cord):
        """
        Finds all encountered segments on an x-cord between two y-values
        @param segments: A list of segments
        @param min_y: The low y-value
        @param max_y: The high y-value
        @param x_cord: An x coordinate
        @return: All the encountered segments between the two y-values
        """
        affected_segments = []

        for segment in segments:
            if segment.x1 < x_cord < segment.x2 \
                    and segment.y1 > min_y \
                    and segment.y2 < max_y:
                affected_segments.append(segment)

        return affected_segments

    @staticmethod
    def __find_segments_above_line(line, segments):
        """
        Finds the segments above a specific line
        @param line: A line
        @param segments: A list of segments
        @return: The segments above a line
        """
        segments_above_line = []

        for segment in segments:
            if segment.y1 < line.y1:
                segments_above_line.append(segment)

        return segments_above_line

    @staticmethod
    def __find_segments_below_line(line, segments):
        """
        Finds the segments below a specific line
        @param line: A line
        @param segments: A list of segments
        @return: The segments above a line
        """
        segments_below_line = []

        for segment in segments:
            if segment.y1 > line.y2:
                segments_below_line.append(segment)

        return segments_below_line

    @staticmethod
    def __merge_two_lines(line1, line2):
        """
        Merges two lines
        @param line1: First line
        @param line2: Second line
        @return: A merged line
        """
        return Line([line1.x1, line1.y1, line2.x2, line2.y2])

    def __merge_all_lines_not_intersecting_segment(self, lines, segments):
        """
        Handles the merging of all lines that are not intersecting segments.
        @param lines: A list of lines
        @param segments: A list of segments
        @return: A list of the non-merged and merged lines
        """
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
        """
        Merges all lines that are not intersecting segments. The output of this method is not guaranteed to be merged
        as much as possible, and therefore recommended to be called multiple times
        @param lines: A list of lines
        @param segments: A list of segments
        @return: A list of the non-merged and merged lines
        """
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
        """
        Checks if any segment in a list of segments is intersected/lays between the two y-values, corresponding
        to a line.
        @param segments: A list of segments
        @param min_y: The lowest y-value
        @param max_y: The highest y-value
        @return: True, if any segment was intersected and False otherwise
        """
        for segment in segments:
            if self.__is_segment_intersected(segment, min_y, max_y):
                return True
        return False

    @staticmethod
    def __is_segment_intersected(segment, min_y, max_y):
        """
        Checks if a single segment is intersected/lays between the two y-values, corresponding to a line.
        @param segment: A segment
        @param min_y: The lowest y-value
        @param max_y: The highest y-value
        @return: True, if the segment was intersected and False otherwise
        """
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

    def __extend_vertical_lines(self, lines, segments):
        """
        Extends the lines to the page bounds, if possible.
        @param lines: A list of lines
        @param segments: A list of segments
        @return: A list of lines that have been extended to the page bounds where possible
        """
        extended_lines = []

        highest_line = min(lines, key=lambda line: line.y1)
        lowest_line = max(lines, key=lambda line: line.y2)

        for line in lines:
            if line != highest_line and line != lowest_line:
                extended_lines.append(line)

        if not self.__find_segments_above_line(highest_line, segments):
            extended_lines.append(Line([highest_line.x1, self.page_y1, highest_line.x2, highest_line.y2]))

        if not self.__find_segments_below_line(lowest_line, segments):
            extended_lines.append(Line([lowest_line.x1, lowest_line.y1, lowest_line.x2, self.page_y2]))

        return extended_lines

    def __extend_lines_to_segment_borders(self, lines, segments):
        """
        Extends the lines to the nearest segment borders.
        @param lines: A list of lines
        @param segments: A list of segments
        @return: A list of lines that have been extended to their nearest segment
        """
        extended_lines = []

        for line in lines:
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

            if not extended_lines.__contains__(Line([line.x1, y1, line.x2, y2])):
                extended_lines.append(Line([line.x1, y1, line.x2, y2]))

        return extended_lines

    def __merge_similar_lines(self, lines):
        """
        Merges similar lines
        @param lines: A list of lines
        @return: A list of merged lines
        """
        lines_to_remove = []

        for outer_line in lines:
            for inner_line in lines:
                if outer_line == inner_line:
                    continue
                if self.__is_line_inside_other_line(outer_line, inner_line):
                    lines_to_remove.append(inner_line)

        for line in lines_to_remove:
            if lines.__contains__(line):
                lines.remove(line)

        return lines

    @staticmethod
    def __is_line_inside_other_line(outer_line, inner_line):
        """
        Checks if an line is inside another line. Does not check the x-value
        @param outer_line: The longer line
        @param inner_line: The smaller line
        @return: True if the inner_line is inside the outer_line, false otherwise
        """
        if inner_line.y1 >= outer_line.y1 and inner_line.y2 <= outer_line.y2:
            return True
        else:
            return False
