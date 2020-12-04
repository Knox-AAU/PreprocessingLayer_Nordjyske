import statistics
import math

from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
from alto_segment_lib.segment import Segment, Line, SegmentType


class SegmentHelper:

    @staticmethod
    def find_line_height_median(lines: list):
        height = []
        for line in lines:
            height.append(line.height())
        return statistics.median(height)

    @staticmethod
    def find_line_width_median(lines: list):
        width = []
        for line in lines:
            width.append(line.width())
        return statistics.median(width)


    def group_lines_into_paragraphs_headers(self, lines: list, file_path: str):
        """ Groups headers together in one list and paragraphs in another list

        @param lines: a list of text lines
        @return: headers, paragraphs: a tuple including a list of headers and a list of paragraphs
        """
        paragraphs = []
        headers = []
        alto_extractor = AltoSegmentExtractor(file_path)
        median = self.find_line_height_median(lines)
        threshold = 1.39
        threshold_increase = 1.1

        paragraph_list = alto_extractor.find_paragraphs()
        header_list = alto_extractor.find_headlines()

        for line in lines:
            # Checks if line height or font size indicates that the line is a paragraph
            if line.height() < (median * threshold) \
                    and [line.x1, line.y1, line.x2, line.y2] in paragraph_list \
                    and [line.x1, line.y1, line.x2, line.y2] not in header_list:
                paragraphs.append(line)
            elif line.height() > (median * threshold * threshold_increase):
                headers.append(line)
            else:
                paragraphs.append(line)

        if len(headers) > 0:
            (headers, new_paragraphs) = self.__repair_header_clusters(headers)
            paragraphs.extend(new_paragraphs)

            (headers, new_paragraphs) = self.__repair_headers_in_paragraphs(headers, paragraphs)
            paragraphs.extend(new_paragraphs)

            paragraphs = self.__remove_paragraphs_within_headers(headers, paragraphs)

        return headers, paragraphs

    def __remove_paragraphs_within_headers(self, headers, paragraphs):
        """ Removes paragraphs that are completely within a header

        @param headers: a list of headers
        @param paragraphs: a list of paragraphs
        @return: updated_paragraphs: a list of paragraphs
        """
        updated_paragraphs = paragraphs.copy()
        for header in headers:
            for paragraph in paragraphs:
                if header.between_y_coordinates(paragraph.y1) \
                        and header.between_y_coordinates(paragraph.y2) \
                        and header.between_x_coordinates(paragraph.x1) \
                        and header.between_x_coordinates(paragraph.x2) \
                        and paragraph in updated_paragraphs:
                    updated_paragraphs.remove(paragraph)

        return updated_paragraphs

    def __repair_headers_in_paragraphs(self, headers, paragraphs):
        """ Determines headers as paragraphs instead if it overlaps with a paragraph

        @param headers: a list of headers
        @param paragraphs: a list of paragraphs
        @return: new_headers, new_paragraphs: a tuple with a lists of new headers and new pararaphc
        """
        new_headers = headers.copy()
        new_paragraphs = []
        margin = 2

        for paragraph in paragraphs:
            for header in headers:
                if (paragraph.between_x_coordinates(header.x1 + margin) and paragraph.between_y_coordinates(header.y1 - margin)) \
                        or (paragraph.between_x_coordinates(header.x2 - margin) and paragraph.between_y_coordinates(header.y2 + margin)):
                    new_paragraphs.append(header)
                    if header in new_headers:
                        new_headers.remove(header)

        return new_headers, new_paragraphs

    def __repair_header_clusters(self, headers):
        """ Finds headers that are clustered together and turns them into paragraphs

        @param headers: list of headers
        @return: list of headers and paragraphs
        """
        header_column_groups = self.__group_same_column(headers)
        header_segment_groups = self.__group_same_segment(header_column_groups, True)
        new_paragraphs = []
        new_headers = []
        min_cluster_size = 6

        for grouped_headers in header_segment_groups:
            if len(grouped_headers) > min_cluster_size:
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
        margin = 0.4
        median = self.find_line_width_median(text_lines) * margin

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
            median = self.find_line_height_median(group) * (3 if ignore_width else 1)
            previous_line = None

            for text_line in group:
                if previous_line is None:
                    previous_line = text_line
                    temp = [text_line]
                    continue

                line_diff = text_line.width() - previous_line.width()
                max_diff = 100

                # Checks if the current and previous lines are in the same segment
                if text_line.y1 - previous_line.y2 < median and (ignore_width or line_diff in range(-max_diff, max_diff)):
                    temp.append(text_line)
                else:
                    segment_groups.append(temp)
                    temp = [text_line]
                previous_line = text_line

            # Saves the last segment
            if len(temp) > 0:
                segment_groups.append(temp)
                temp = []

        return segment_groups

    @staticmethod
    def make_box_around_lines(text_lines: list, return_coordiantes=False):
        """ Finds the coordinates for the segment containing the lines and creates the segment

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

        if return_coordiantes:
            return x1, y1, x2, y2

        segment = Segment([x1, y1, x2, y2])
        segment.lines = text_lines

        return segment

    def repair_text_lines(self, text_lines: list, lines: list):
        """ Splits text lines spanning over several columns into smaller lines

        @param text_lines: list of text lines
        @param lines: list of lines
        @return: new_lines: a list of text lines spanning only one column
        """
        new_text_lines = []
        for text_line in text_lines:
            if text_line.is_box_horizontal():
                # Gets whether the text line is intersected and which lines intersect it
                (does_line_intersect, intersecting_lines) = self.__does_line_intersect_text_line(text_line, lines)
                if does_line_intersect:
                    for line in intersecting_lines:
                        split_x_coord = int(self.__find_split_x_coord(text_line, line))
                        coords = [split_x_coord, text_line.y1, text_line.x2, text_line.y2]

                        new_text_lines.append(Line([text_line.x1, text_line.y1, split_x_coord, text_line.y2]))
                        new_text_lines.append(Line(coords))
                else:
                    new_text_lines.append(text_line)

        return new_text_lines

    def __does_line_intersect_text_line(self, text_line, lines: list):
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
        else:
            return False, None

    @staticmethod
    def get_content_bounds(segments: list):
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


    def __find_split_x_coord(self, text_line, line):
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
        header_segments = []
        segment = None

        x1 = x2 = y1 = y2 = 0
        radius = 0
        threshold = 100  # ToDo: make smart

        for line in header_lines:
            if radius > 0 and SegmentHelper.isInsideCircle(x1, y1, radius, line.x1, line.y1):
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
            radius = line.height()+400  # TODO: Make smarter

        if segment is not None:
            segment.update_coordinates_based_on_lines()
            header_segments.append(segment)

        return header_segments

    # https://www.geeksforgeeks.org/find-if-a-point-lies-inside-or-on-circle/
    @staticmethod
    def isInsideCircle(circle_x, circle_y, rad, x, y):
        # Compare radius of circle
        # with distance of its center
        # from given point
        return (x - circle_x) * (x - circle_x) + (y - circle_y) * (y - circle_y) <= rad * rad

    @staticmethod
    def inside_box(box_coords: list, x: int, y: int):
        if len(box_coords) == 4:
            return box_coords[0] <= x <= box_coords[2] and box_coords[1] <= y <= box_coords[2]
        return False

    @staticmethod
    def distance_between_coordinates(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return math.sqrt(dx ** 2 + dy ** 2)