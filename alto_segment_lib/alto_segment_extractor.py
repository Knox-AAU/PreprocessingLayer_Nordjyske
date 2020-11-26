from xml.dom import minidom
import operator
import enum
from alto_segment_lib.segment import Segment, SegmentType
from alto_segment_lib.segment import Line
import statistics
import re


class FindType(enum.Enum):
    Paragraph = 1
    Header = 2


def determine_most_frequent_list_element(the_list: list):
    return max(set(the_list), key=the_list.count)


class AltoSegmentExtractor:
    __path: str
    __dpi: int
    __margin: int
    __xmldoc: minidom
    __para_fonts = []
    __head_fonts = []

    def __init__(self, alto_path: str = "", dpi: int = 300, margin: int = 0):
        self.__dpi = dpi
        self.__margin = margin
        self.set_path(alto_path)
        self.__median_line_width = 0

    def set_path(self, path: str):
        self.__path = path
        self.__xmldoc = minidom.parse(self.__path)
        self.__font_statistics()

    def set_dpi(self, dpi: int):
        self.__dpi = dpi

    def get_dpi(self):
        return self.__dpi

    def set_margin(self, margin: int):
        self.__margin = margin

    def get_margin(self):
        return self.__margin

    def __find_segments_by_tag_name(self, tagname: str):
        segments: list = []
        elements = self.__xmldoc.getElementsByTagName(tagname)

        for element in elements:
            coordinate = self.__extract_coordinates(element)
            segments.append(Segment(coordinate))

        return segments

    def find_blocks_coordinates(self):
        return self.__find_segments_by_tag_name('TextBlock')

    def find_lines_coordinates(self):
        return self.__find_segments_by_tag_name('TextLine')

    def find_lines_in_segment(self, elem: minidom):
        segments: list = []

        text_lines = elem.getElementsByTagName('TextLine')

        for text_line in text_lines:
            coordinate = self.__extract_coordinates(text_line)
            segments.append(coordinate)

        return segments

    def find_headlines(self):
        return self.__find_lines_with_type(FindType.Header)

    def find_paragraphs(self):
        return self.__find_lines_with_type(FindType.Paragraph)

    def __find_segs_with_type(self, SegmentsToExtract: FindType):
        segments: list = []
        lines: list = []

        text_blocks = self.__xmldoc.getElementsByTagName('TextBlock')

        for text_block in text_blocks:
            text_lines = text_block.getElementsByTagName('TextLine')
            text_lines_coord = self.find_lines_in_segment(text_block)
            coordinate = None

            if SegmentsToExtract == FindType.Header:
                if text_lines[0].attributes['STYLEREFS'].value in self.__para_fonts:
                    coordinate = self.__extract_coordinates(text_block)
            elif SegmentsToExtract == FindType.Paragraph:
                if text_lines[0].attributes['STYLEREFS'].value not in self.__para_fonts:
                    coordinate = self.__extract_coordinates(text_block)

            if coordinate is not None:
                coordinate.append(text_lines_coord)
                segments.append(coordinate)

        return segments

    def __find_lines_with_type(self, LinesToExtract: FindType):
        lines: list = []

        text_blocks = self.__xmldoc.getElementsByTagName('TextBlock')

        for text_block in text_blocks:
            text_lines = text_block.getElementsByTagName('TextLine')
            for text_line in text_lines:
                coordinate = None

                if LinesToExtract == FindType.Header:
                    if text_line.attributes['STYLEREFS'].value not in self.__para_fonts \
                            and text_line.attributes['STYLEREFS'].value is not None:
                        coordinate = self.__extract_coordinates(text_line)
                elif LinesToExtract == FindType.Paragraph:
                    if text_line.attributes['STYLEREFS'].value in self.__para_fonts:
                        coordinate = self.__extract_coordinates(text_line)

                if coordinate is not None:
                    lines.append(coordinate)

        return lines

    def extract_segments(self):
        segments = []
        text_blocks = self.__xmldoc.getElementsByTagName('TextBlock')

        for text_block in text_blocks:
            text_block_coordinates = self.__extract_coordinates(text_block)
            segment = Segment(text_block_coordinates)
            text_lines = text_block.getElementsByTagName('TextLine')
            text_line_fonts = []

            for text_line in text_lines:
                text_line_coordinates = self.__extract_coordinates(text_line)
                line = Line(text_line_coordinates)
                if segment.between_x_coords(line.x1 + 10) and segment.between_x_coords(line.x2 - 10):
                    text_line_fonts.append(text_line.attributes['STYLEREFS'].value)
                    segment.lines.append(line)

            style = determine_most_frequent_list_element(text_line_fonts)

            if style in self.__para_fonts:
                segment.type = SegmentType.paragraph
            elif style in self.__head_fonts:
                segment.type = SegmentType.heading
            else:
                segment.type = SegmentType.unknown

            segments.append(segment)

        return segments

    def extract_lines(self):
        lines = []
        text_lines = self.__xmldoc.getElementsByTagName('TextLine')

        for text_line in text_lines:
            text_line_coordinates = self.__extract_coordinates(text_line)
            font = self.__extract_font(text_line)
            line = Line(text_line_coordinates, font)

            lines.append(line)

        return lines

    def __analyze_coordinates(self, lines):
        all_para = []
        for line in lines:
            all_para.append(line.x2 - line.x1)
        self.__median_line_width = statistics.median(all_para)

    def __extract_coordinates(self, element: minidom):
        coordinates = [
            int(element.attributes['HPOS'].value),
            int(element.attributes['VPOS'].value),
            int(element.attributes['WIDTH'].value) + int(element.attributes['HPOS'].value),
            int(element.attributes['HEIGHT'].value) + int(element.attributes['VPOS'].value)
        ]

        for idx in range(4):
            va = coordinates[idx]
            if isinstance(va, int):
                coordinates[idx] = self.inch1200_to_px(coordinates[idx])

        if self.__margin > 0:
            coordinates[0] -= self.__margin
            coordinates[1] -= self.__margin
            coordinates[2] += self.__margin
            coordinates[3] += self.__margin

        return coordinates

    def __extract_font(self, element: minidom):
        font = str(element.attributes['STYLEREFS'].value)
        return float(font.split("TS")[1])

    def inch1200_to_px(self, inch1200: int):
        return int(round((inch1200 * self.__dpi) / 1200))

    def __font_statistics(self):
        fonts: dict = self.__find_font_sizes()
        stats = {}

        # Finds how many instances there are of each font
        for key in fonts:
            lines = self.__xmldoc.getElementsByTagName('TextLine')
            for line in lines:
                if line.attributes['STYLEREFS'].value == key:
                    if not stats.__contains__(key):
                        stats[key] = 1
                    else:
                        stats[key] += 1

        most_used_font = max(stats.items(), key=operator.itemgetter(1))[0]

        # Add each font to either para fonts or head fonts
        for key in fonts:
            if fonts.get(key) <= fonts.get(most_used_font) + 1.5:
                self.__para_fonts.append(key)
            else:
                self.__head_fonts.append(key)

    def __find_font_sizes(self):
        fonts = {}
        styles = self.__xmldoc.getElementsByTagName('TextStyle')
        for style in styles:
            fonts[str(style.attributes['ID'].value)] = float(style.attributes['FONTSIZE'].value)
        return fonts
