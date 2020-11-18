import statistics

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
        paragraph = []
        header = []
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
                paragraph.append(line)
            elif line.height() > (median * threshold):
                header.append(line)
            else:
                paragraph.append(line)

        return header, paragraph

    def combine_lines_into_segments(self, lines):
        segments = []
        column_groups = self.__group_same_column(lines)
        segment_groups = self.__group_same_segment(column_groups)

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
        median = self.find_line_width_median(lines) * 0.4 # Add a 40 % margin

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

    def __group_same_segment(self, column_groups):
        temp = []
        segment_groups = []

        for group in column_groups:
            group = sorted(group, key=lambda sorted_group: sorted_group.y1)
            median = self.find_line_height_median(group)
            previous_line = None

            for line in group:
                if previous_line is None:
                    previous_line = line
                    temp = [line]
                    continue

                line_diff = line.width() - previous_line.width()
                max_diff = 100

                # Checks if the current and previous lines are in the same segment
                if line.y1 - previous_line.y2 < median and line_diff in range(-max_diff, max_diff):
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
        for text_line in text_lines:
            if text_line.is_box_horizontal():
                # Gets whether the text line is intersected and which lines intersect it
                (does_line_intersect, intersecting_lines) = self.__does_line_intersect_text_line(text_line, lines)
                if does_line_intersect:
                    for line in intersecting_lines:
                        coords = [line.x1, text_line.y1, text_line.x2, text_line.y2]
                        text_line.x2 = line.x1

                        text_lines.append(Line(coords))

        return text_lines

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
