import statistics
import math
from typing import List
from alto_segment_lib.segment import Segment, Line, SegmentType
import configparser

class SegmentHelper:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.__threshold_block_header_to_paragraph = float(config['page_segmentation']['threshold_block_header_to_paragraph'])
        self.__threshold_line_header_to_paragraph = float(config['page_segmentation']['threshold_line_header_to_paragraph'])
        self.__min_lines_to_compare_block_height_instead_of_line_height = int(config['page_segmentation']['min_lines_to_compare_block_height_instead_of_line_height'])
        self.__group_same_column_margin = float(config['page_segmentation']['group_same_column_margin'])
        self.__group_same_segment_margin_px = float(config['page_segmentation']['group_same_segment_margin_px'])
        self.__min_cluster_size = int(config['page_segmentation']['min_cluster_size'])

    def group_lines_into_paragraphs_headers(self, lines: List):
        """ Groups headers together in one list and paragraphs in another list
        @param lines: a list of text lines
        @return: headers, paragraphs: a tuple including a list of headers and a list of paragraphs
        """
        paragraphs = []
        headers = []
        median = statistics.median([line.height() for line in lines])

        for line in lines:
            height = line.height()
            # If line belongs to a block_segment, and that block_segment has more than some
            # minimum amount of lines, we assign the height we compare to the median of the
            # block_segment rather than the line.
            if line.block_segment is not None and line.block_segment.line_count >= \
                    self.__min_lines_to_compare_block_height_instead_of_line_height:
                height = statistics.median([x.height() for x in line.block_segment.lines])
            # Checks if line height indicates that the line is a paragraph
            if line.height() > height * self.__threshold_line_header_to_paragraph or\
                    height > median * self.__threshold_block_header_to_paragraph:
                headers.append(line)
            else:
                paragraphs.append(line)

        if len(headers) > 0:
            (headers, new_paragraphs) = self.__repair_header_clusters(headers)
            paragraphs.extend(new_paragraphs)
        return headers, paragraphs

    @staticmethod
    def remove_segments_within_segments(outer_segs, inner_segs):
        """ Removes paragraphs that are completely within a header or headers within paragraphs

        @param outer_segs: a list of segments
        @param inner_segs: a list of segments
        @return: updated_paragraphs: a list of paragraphs
        """
        updated_segs = inner_segs.copy()
        for outer_seg in outer_segs:
            for inner_seg in inner_segs:
                if outer_seg.between_y_coordinates(inner_seg.y1) \
                        and outer_seg.between_y_coordinates(inner_seg.y2) \
                        and outer_seg.between_x_coordinates(inner_seg.x1) \
                        and outer_seg.between_x_coordinates(inner_seg.x2) \
                        and inner_seg in updated_segs:
                    updated_segs.remove(inner_seg)

        return updated_segs

    def __repair_header_clusters(self, headers):
        """ Finds headers that are clustered together and turns them into paragraphs

        @param headers: list of headers
        @return: new_headers, new_paragraphs: a tuple including a list of headers and a list of paragraphs
        """
        header_column_groups = self.__group_same_column(headers)
        header_segment_groups = self.__group_same_segment(header_column_groups, True)
        new_paragraphs = []
        new_headers = []

        for grouped_headers in header_segment_groups:
            if len(grouped_headers) >= self.__min_cluster_size:
                new_paragraphs.extend(grouped_headers)
            else:
                new_headers.extend(grouped_headers)

        return new_headers, new_paragraphs

    def combine_lines_into_segments(self, text_lines: list):
        """ Groups text lines into segments

        @param text_lines: list of text lines
        @return: segments: list of segments
        """
        segments = []
        column_groups = self.__group_same_column(text_lines)
        segment_groups = self.__group_same_segment(column_groups, False)

        for group in segment_groups:
            if len(group) > 0:
                new_segment = self.make_box_around_lines(group)
                new_segment.type = SegmentType.paragraph
                segments.append(new_segment)
        return segments

    def __group_same_column(self, text_lines):
        """ Groups text lines into columns

        @param text_lines: list of text lines
        @return: column_groups: list of lists containing lines
        """
        previous_line = None
        temp = []
        column_groups = []
        median = statistics.median([line.width() for line in text_lines]) * self.__group_same_column_margin

        # Sorts the list in an ascending order based on x1
        text_lines = sorted(text_lines, key=lambda sorted_line: sorted_line.x1)

        for text_line in text_lines:
            if previous_line is None:
                previous_line = text_line
                temp = [text_line]
                continue

            # Checks if the current and previous line are in the sane column
            if text_line.x1 - previous_line.x1 < median:
                temp.append(text_line)
            else:
                column_groups.append(temp)
                temp = [text_line]
                previous_line = text_line

        # Saves the last column
        if len(temp) > 0:
            column_groups.append(temp)

        return column_groups

    def __group_same_segment(self, column_groups, ignore_width):
        """ Groups text lines within columns into segments

        @param column_groups: list of lists containing lines
        @param ignore_width: boolean indicating whether width should be checked
        @return: segments: list of lists containing segments
        """
        temp = []
        segment_groups = []

        for group in column_groups:
            group = sorted(group, key=lambda sorted_group: sorted_group.y1)
            median = statistics.median([line.height() for line in group]) * (0.2 if ignore_width else 1)
            previous_line = None

            for index, text_line in enumerate(group):

                if previous_line is None:
                    previous_line = text_line
                    temp = [text_line]
                    continue

                x1_diff = text_line.x1 - previous_line.x1
                x2_diff = text_line.x2 - previous_line.x2

                margin = self.__group_same_segment_margin_px

                # Is true if considered same segment, based on previous, current and next line.
                is_width_ok = (not x1_diff < -margin and ((-margin < x2_diff < margin)
                                            or not self.__is_next_line_similiar_x2(index, group)))

                # Checks if the current and previous lines are in the same segment
                if text_line.y1 - previous_line.y2 < median and (ignore_width or is_width_ok):
                    temp.append(text_line)
                # Makes a new segment and adds the first text line
                else:
                    segment_groups.append(temp)
                    temp = [text_line]
                previous_line = text_line

            # Saves the last segment
            if len(temp) > 0:
                segment_groups.append(temp)
                temp = []

        return segment_groups

    def __is_next_line_similiar_x2(self, index, group) -> bool:
        # If last element, then return false.
        if len(group) == index + 1:
            return False

        curr_line = group[index]
        next_line = group[index + 1]
        x2_diff = curr_line.x2 - next_line.x2

        # If x2_diff within margin
        return -self.__group_same_segment_margin_px < x2_diff < self.__group_same_segment_margin_px

    @staticmethod
    def make_box_around_lines(text_lines: list, return_coordinates=False):
        """ Finds the coordinates for the segment containing the lines and creates the segment
        # todo Lau: Kan vi ikke bare kalde .to_array() istedet for at lave metoden til at returnere array?
        # todo : 16 linjer duplikeret kode længere nede i get_content_bounds()
        @param return_coordinates:
        @param text_lines: list of text lines
        @return: segment
        """
        if len(text_lines) == 0:
            return None

        x1 = text_lines[0].x1
        x2 = text_lines[0].x2
        y1 = text_lines[0].y1
        y2 = text_lines[0].y2

        # Finds width and height line and change box height and width accordingly
        for line in text_lines:
            # Find x-coordinate upper left corner
            if line.x1 < x1:
                x1 = line.x1

            # Find x-coordinate lower right corner
            if line.x2 > x2:
                x2 = line.x2

            # Find y-coordinate upper left corner
            if line.y1 < y1:
                y1 = line.y1

            # Find y-coordinate lower right corner
            if line.y2 > y2:
                y2 = line.y2

        if return_coordinates:
            return x1, y1, x2, y2

        segment = Segment([x1, y1, x2, y2])
        segment.lines = text_lines

        return segment

    def split_segments_by_lines(self, text_lines: list, lines: list):
        """ Splits text lines spanning over several columns into smaller lines

        @param text_lines: list of text lines
        @param lines: list of lines
        @return: new_lines: a list of text lines spanning only one column
        """
        new_text_lines = []
        for text_line in text_lines:
            if text_line.is_box_horizontal():
                # Gets whether the text line is intersected and which lines intersect it
                (does_line_intersect, intersecting_lines) = self.__does_line_intersect_text_line(
                    text_line, lines)
                if does_line_intersect:
                    intersecting_lines.sort(key=lambda line: line.x1)
                    line_rest = Line(text_line.to_array())
                    for line in intersecting_lines:
                        split_x_coord = int(self.__find_split_x_coord(text_line, line))

                        new_text_lines.append(
                            Line([line_rest.x1, line_rest.y1, split_x_coord, line_rest.y2]))
                        line_rest.x1 = split_x_coord
                    new_text_lines.append(line_rest)
                else:
                    new_text_lines.append(text_line)

        return new_text_lines

    @staticmethod
    def __does_line_intersect_text_line(text_line, lines: list):
        """ Checks whether a vertical line intersects the text_line

        @param text_line: list of text lines
        @param lines: list of lines
        @return: new_lines: returns a tuple with a boolean which is false if no lines found, as well as the lines found
        """
        new_lines = []

        for line in lines:
            # Finds 5% of the width as a buffer to avoid false positives due to crooked lines
            width_5_percent = (text_line.x2 - text_line.x1) * 0.05

            if not line.is_horizontal():
                # Checks if the line vertically intersects the text line
                if text_line.x1 + width_5_percent < line.x1 < text_line.x2 - width_5_percent:
                    # Checks if the line horizontally intersects the text line
                    if line.y1 < text_line.y1 < line.y2 or line.y1 < text_line.y2 < line.y2:
                        new_lines.append(line)

        if len(new_lines) != 0:
            return True, new_lines
        return False, None

    @staticmethod
    def get_content_bounds(segments: list):
        """
        todo
        @param segments:
        @return:
        """
        # x1 and y1 need to be reduced to lowest possible value, we start at high value (10000).
        x1 = y1 = 10000
        x2 = y2 = 0

        for segment in segments:
            # Find x-coordinate upper left corner
            if segment.x1 < x1:
                x1 = segment.x1

            # Find x-coordinate lower right corner
            if segment.x2 > x2:
                x2 = segment.x2

            # Find y-coordinate upper left corner
            if segment.y1 < y1:
                y1 = segment.y1

            # Find y-coordinate lower right corner
            if segment.y2 > y2:
                y2 = segment.y2

        return x1, y1, x2, y2

    @staticmethod
    def __find_split_x_coord(text_line, line):
        """ Finds the x-coordinate where the line intersects with text line

        @param text_line: the text line that should be split
        @param line: the line intersecting the text line
        @return: split_x_coord: the x-coordinate for where the text line should be split
        """
        # Calculates coordinates for B based on angle A, C and line b, where C is 90
        # Calculate A
        line_slope = abs(line.x2 - line.x1) / abs(line.y2 - line.y1)
        line_degree = math.atan(line_slope)
        # Calculate B
        other_angle = 180 - 90 - line_degree
        # Calculate b
        line_height_from_text = text_line.y1 - line.y1

        # Calculate a, which is the distance from the line to the
        dist_text_to_line = line_height_from_text / math.sin(other_angle) * math.sin(line_degree)
        # The x-coordinate for B where the line and text_line intersect
        split_x_coord = (line.x1 + dist_text_to_line) if line.x1 < line.x2 else (line.x1 - dist_text_to_line)

        return split_x_coord

    @staticmethod
    def group_headers_into_segments(header_lines):
        """
        todo
        @param header_lines:
        @return:
        """
        header_segments = []
        segment = None

        x1 = x2 = y1 = y2 = 0
        radius = 0
        threshold = 100  # ToDo: make smart

        for line in header_lines:
            if radius > 0 and SegmentHelper.__is_inside_circle(x1, y1, radius, line.x1, line.y1):
                # The line is within the circle of the header
                segment.add_line(line)
            elif x1 != x2 != y1 != y2 != 0 and abs(line.x1 - x2) < threshold and abs(line.y1 - y1) < threshold:
                # The line is right next to the header
                segment.add_line(line)
            else:
                if segment is not None:
                    segment.update_coordinates_based_on_lines()
                    header_segments.append(segment)

                segment = Segment()
                segment.type = SegmentType.heading
                segment.add_line(line)

            x1 = line.x1
            y1 = line.y1
            x2 = line.x2
            y2 = line.y2
            radius = line.height() + 400  # TODO: Make smarter

        if segment is not None:
            segment.update_coordinates_based_on_lines()
            header_segments.append(segment)

        return header_segments

    @staticmethod
    def __is_inside_circle(circle_x, circle_y, rad, x, y):
        # https://www.geeksforgeeks.org/find-if-a-point-lies-inside-or-on-circle/
        # Compare radius of circle
        # with distance of its center
        # from given point
        return (x - circle_x) * (x - circle_x) + (y - circle_y) * (y - circle_y) <= rad * rad

    @staticmethod
    def inside_box(box_coords: list, x: int, y: int):
        if len(box_coords) == 4:
            return box_coords[0] <= x <= box_coords[2] and box_coords[1] <= y <= box_coords[3]
        return False

    @staticmethod
    def distance_between_coordinates(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return math.sqrt(dx ** 2 + dy ** 2)