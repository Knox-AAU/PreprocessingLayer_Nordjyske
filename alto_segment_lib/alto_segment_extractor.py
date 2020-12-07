from xml.dom import minidom
from alto_segment_lib.segment import Segment
from alto_segment_lib.segment import Line


class AltoSegmentExtractor:
    """
    Class that extracts segments from ALTO xml files.
    """

    dpi: int
    margin: int
    __xml_doc: minidom

    @property
    def path(self):
        """
        Gets the path
        @return: path
        """
        return self.__path

    @path.setter
    def path(self, path):
        """
        Sets the path
        @param path: The new path
        """
        self.__path = path
        self.__xml_doc = minidom.parse(self.path)

    def __init__(self, alto_path: str = "", dpi: int = 300, margin: int = 0):
        self.dpi = dpi
        self.margin = margin
        if alto_path != "":
            self.__path = alto_path
            self.__xml_doc = minidom.parse(self.path)

    def extract_lines(self):
        """
        Extracts text lines from an alto xml file.
        @return: lines: list of lines
        """
        lines = []

        text_blocks = self.__xml_doc.getElementsByTagName('TextBlock')
        for text_block in text_blocks:
            text_block_segment = Segment(self.__extract_coordinates(text_block))
            text_lines = text_block.getElementsByTagName('TextLine')
            text_block_segment.line_count = len(text_lines)
            text_block_segment.lines = [
                Line(self.__extract_coordinates(text_line), block_segment=text_block_segment)
                for text_line in text_lines
            ]
            lines.extend(text_block_segment.lines)
        return lines

    def __extract_coordinates(self, element: minidom):
        coordinates = [
            int(element.attributes['HPOS'].value),
            int(element.attributes['VPOS'].value),
            int(element.attributes['WIDTH'].value) + int(element.attributes['HPOS'].value),
            int(element.attributes['HEIGHT'].value) + int(element.attributes['VPOS'].value)
        ]

        for index in range(4):
            var = coordinates[index]
            # todo do we need this line?
            if isinstance(var, int):
                coordinates[index] = self.inch1200_to_px(coordinates[index])

        if self.margin > 0:
            coordinates[0] -= self.margin
            coordinates[1] -= self.margin
            coordinates[2] += self.margin
            coordinates[3] += self.margin

        return coordinates

    def inch1200_to_px(self, inch1200):
        """
        Converts inch1200 notation to pixel location.
        @param inch1200:
        @return: pixel location
        """
        return int(round((inch1200 * self.dpi) / 1200))
