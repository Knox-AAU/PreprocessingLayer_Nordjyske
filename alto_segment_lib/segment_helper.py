import statistics
import math

from alto_segment_lib.alto_segment_extractor import AltoSegmentExtractor
from alto_segment_lib.segment import Segment, Line


class SegmentHelper:
    __file_path: str

    def __init__(self, file_path):
        self.__file_path = file_path

    @staticmethod
    def find_line_height_median(lines):
        height = []
        for line in lines:
            height.append(line.height())
        return statistics.median(height)

    @staticmethod
    def find_line_width_median(lines):
        width = []
        for line in lines:
            width.append(line.width())
        return statistics.median(width)

    def group_lines_into_paragraphs_headers(self, lines):
        paragraphs = []
        headers = []
        alto_extractor = AltoSegmentExtractor(self.__file_path)
        median = self.find_line_height_median(lines)
        threshold = 1.39

        paragraph_list = alto_extractor.find_paragraphs()
        header_list = alto_extractor.find_headlines()

        for line in lines:
            # Checks if line height or font size indicates that the line is a paragraph
            if line.height() < (median * threshold) \
                    and [line.x1, line.y1, line.x2, line.y2] in paragraph_list \
                    and [line.x1, line.y1, line.x2, line.y2] not in header_list:
                paragraphs.append(line)
            elif line.height() > (median * threshold * 1.1):
                headers.append(line)
            else:
                paragraphs.append(line)

        if len(headers) > 0:
            (headers, new_paragraphs) = self.repair_header_clusters(headers)
            paragraphs.extend(new_paragraphs)

            (headers, new_paragraphs) = self.repair_headers_in_paragraphs(headers, paragraphs)
            paragraphs.extend(new_paragraphs)

            paragraphs = self.remove_paragraphs_within_headers(headers, paragraphs)

        return headers, paragraphs

    def remove_paragraphs_within_headers(self, headers, paragraphs):
        updated_paragraphs = paragraphs.copy()
        for header in headers:
            for paragraph in paragraphs:
                if header.between_y_coords(paragraph.y1) \
                        and header.between_y_coords(paragraph.y2) \
                        and header.between_x_coords(paragraph.x1) \
                        and header.between_x_coords(paragraph.x2) \
                        and paragraph in updated_paragraphs:
                    updated_paragraphs.remove(paragraph)

        return updated_paragraphs

    def repair_headers_in_paragraphs(self, headers, paragraphs):
        new_headers = headers.copy()
        new_paragraphs = []
        margin = 2

        for paragraph in paragraphs:
            for header in headers:
                if (paragraph.between_x_coords(header.x1 + margin) and paragraph.between_y_coords(header.y1 - margin)) \
                        or (paragraph.between_x_coords(header.x2 - margin) and paragraph.between_y_coords(header.y2 + margin)):
                    new_paragraphs.append(header)
                    if header in new_headers:
                        new_headers.remove(header)

        return new_headers, new_paragraphs

    def repair_header_clusters(self, headers):
        header_column_groups = self.__group_same_column(headers)
        header_segment_groups = self.__group_same_segment(header_column_groups, True)
        new_paragraphs = []
        new_headers = []

        for grouped_headers in header_segment_groups:
            if len(grouped_headers) > 3:
                new_paragraphs.extend(grouped_headers)
            else:
                new_headers.extend(grouped_headers)

        return new_headers, new_paragraphs

    def combine_lines_into_segments(self, lines):
        segments = []
        column_groups = self.__group_same_column(lines)
        segment_groups = self.__group_same_segment(column_groups, False)

        for group in segment_groups:
            if len(group) > 0:
                new_segment = self.make_box_around_lines(group)
                new_segment.type = "paragraph"
                segments.append(new_segment)
        return segments

    def __group_same_column(self, lines):
        previous_line = None
        temp = []
        column_groups = []
        median = self.find_line_width_median(lines) * 0.4  # Adds a 40 % margin

        # Sorts the list in an ascending order based on x1
        lines = sorted(lines, key=lambda sorted_line: sorted_line.x1)

        for line in lines:
            if previous_line is None:
                previous_line = line
                temp = [line]
                continue

            # Checks if the current and previous line are in the sane column
            if line.x1 - previous_line.x1 < median:
                temp.append(line)
            else:
                column_groups.append(temp)
                temp = [line]
                previous_line = line

        # Saves the last column
        if len(temp) > 0:
            column_groups.append(temp)

        return column_groups

    def __group_same_segment(self, column_groups, ignore_width):
        temp = []
        segment_groups = []

        for group in column_groups:
            group = sorted(group, key=lambda sorted_group: sorted_group.y1)
            median = self.find_line_height_median(group) * 3 if ignore_width else 1
            previous_line = None

            for line in group:
                if previous_line is None:
                    previous_line = line
                    temp = [line]
                    continue

                line_diff = line.width() - previous_line.width()
                max_diff = 100

                # Checks if the current and previous lines are in the same segment
                if line.y1 - previous_line.y2 < median and (ignore_width or line_diff in range(-max_diff, max_diff)):
                    temp.append(line)
                else:
                    segment_groups.append(temp)
                    temp = [line]
                previous_line = line

            # Saves the last segment
            if len(temp) > 0:
                segment_groups.append(temp)
                temp = []

        return segment_groups

    @staticmethod
    def make_box_around_lines(lines: list):
        if len(lines) == 0:
            return None

        x1 = lines[0].x1
        x2 = lines[0].x2
        y1 = lines[0].y1
        y2 = lines[0].y2

        # Finds width and height line and change box height and width accordingly
        for line in lines:
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

        segment = Segment([x1, y1, x2, y2])
        segment.lines = lines

        return segment

    def repair_text_lines(self, text_lines, lines):
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

    def __find_split_x_coord(self, text_line, line):
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
