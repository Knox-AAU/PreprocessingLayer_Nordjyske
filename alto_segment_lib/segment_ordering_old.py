import statistics
from os import environ
from matplotlib.patches import ConnectionPatch
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
from alto_segment_lib.segment import Segment
from alto_segment_lib.line_extractor.extractor import LineExtractor
from alto_segment_lib.segment import Line
environ["OPENCV_IO_ENABLE_JASPER"] = "true"


class SegmentOrdering:


    Paragraph_normal_width: float

    def __init__(self, file_path, file_name):
        self.File_path = file_path
        self.File_name = file_name

    def distribute_segments_into_articles(self, headers_org, paragraphs):
        """ Distributes the segments into articles
        :param headers_org: List of header segments
        :param paragraphs: List of paragraph segments
        """
        self.Paragraph_normal_width = self.__median_para_width(paragraphs)
        headers: list = []
        for header in headers_org:
            headers.append(header)

        # Remove Date, paper name, page number
        # self.__y_cord_of_top_vertical_line()
        headers = self.__remove_date_papername_pagenumber(headers)
        paragraphs = self.__remove_date_papername_pagenumber(paragraphs)

        # Match headers with subheaders
        headers_with_subheaders = self.__match_headers_with_subheaders(headers, self.Paragraph_normal_width)
        # self.__display_header_pairs(headers_with_subheaders)

        # Match paragraphs with each other in order per article
        # articles: list = [[]]       # A list of articles with their paragraphs in an ordered list, and their header(s) as the first (and second) element(s)
        # articles = self.__matchParagraphsWithHeaders(headers_with_subheaders, paragraphs)

    def __remove_date_papername_pagenumber(self, segments: list):
        """ Removes the date paper name and page number from the list of segments. These are always found at the top of
        the page, and is therefore found from the position. This should maybe be done by the page header line.
        :param segments: A list of segments
        :return: The list of segments without null entries and date, paper name, page number
        """
        page_header_ends_at = 300
        segments = [i for i in segments if i]
        for segment in segments:
            if segment.y1 < page_header_ends_at:
                segments.remove(segment)
        return segments

    def __y_cord_of_top_vertical_line(self):
        line_extractor = LineExtractor()
        all_lines = line_extractor.extract_lines_via_path(self.File_path + self.File_name + ".jp2")
        lines: list = []

        # Find the right line
        for line in all_lines:
            #if line.y1 > 500 or line.y2 > 500 or line.y1 < 50:
             #   continue
            lines.append(line)

        # Find the top three lines
        average_y = self.__find_top_three_lines(lines)
        self.display_lines(lines)

    def __sort_by_y(self, line: Line):
        return line.y1

    def __find_top_three_lines(self, lines) -> int:
        current_max_y = -1
        top_three_lines: list = []

        lines.sort(key=self.__sort_by_y)

        top_three_lines.append(lines[0])
        top_three_lines.append(lines[0])
        top_three_lines.append(lines[0])

        average = (top_three_lines[0].y1 + top_three_lines[1].y1 + top_three_lines[2].y1) / 3
        return average
        # for line in lines:
        #     if len(top_three_lines) >= 3:
        #         break
        #     if current_max_y == -1:
        #         top_three_lines.append(line)
        #         current_max_y



    def __sort_by_y_cord(self, header: Segment):
        """ Simply used to sort a list of headers by their y coordinate
        :param header: Header to check
        :return: The headers y coordinate
        """
        return header.y1

    def __match_headers_with_subheaders(self, headers, median_line_width: float):
        """ Finds header, subheader pairs and returns them
        :param headers: Header pairs
        :param median_line_width: Normal paragraph width
        :return: A list of pairs of headers with subheaders. These pairs also contains pairs with a single element,
            these are the the headers without a subheader
        """
        headers_with_subheaders: list = []
        index_to_delete: list = []
        headers.sort(key=self.__sort_by_y_cord)

        # Finds header pairs
        for header in headers:
            for checking_header in headers:
                if checking_header == header:
                    continue
                if self.__is_subheader(header, checking_header, median_line_width):
                    pair: list = [header, checking_header]
                    headers_with_subheaders.append(pair)
                    # Adds the header to be removed later
                    if not index_to_delete.__contains__(header):
                        index_to_delete.append(header)
                    if not index_to_delete.__contains__(checking_header):
                        index_to_delete.append(checking_header)
        # Removes headers from headers list, to find the single headers
        for elm in index_to_delete:
            headers.remove(elm)

        # Add the last non header pairs
        for header in headers:
            headers_with_subheaders.append([header])

        return headers_with_subheaders

    def __is_subheader(self, header: Segment, possible_subheader: Segment, median_line_width: float):
        """ Checks if the possible_subheader is a subheader to the header
        :param header: Header segment
        :param possible_subheader: The header segment to check if it's a subheader to the header
        :param median_line_width: Normal paragraph width
        :return: True if they are a pair, false if aren't
        """
        header_width = header.x2 - header.x1
        subheader_height = possible_subheader.y2 - possible_subheader.y1
# 116
        if (-20 <= possible_subheader.y1 - header.y2 < 150 and -header_width <= header.x1 - possible_subheader.x1 <= header_width) \
                or (header.x2 - header.x1 < median_line_width * 0.6 and -subheader_height <= possible_subheader.y1 - header.y2 < subheader_height and -50 <= header.x2 -
                    possible_subheader.x1 <= header_width):
            return True
        else:
            return False

    def __median_para_width(self, segments: list):
        """ Finds the normal paragraph width
        :param segments: A list of segments
        :return: The normal paragraph width
        """
        all_para = []
        for segment in segments:
            all_para.append(segment.x2 - segment.x1)
        return float(statistics.median(all_para))


    def __display_header_pairs(self, headers_with_subheaders: list):
        """ Outputs a picture with headers and subheaders marked
        :param headers_with_subheaders: A list of pairs and non pairs of headers
        """
        plt.imshow(Image.open(self.File_path + self.File_name + ".jp2"))
        plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

        for pair in headers_with_subheaders:
            for elm in pair:
                plt.gca().add_patch(
                    Rectangle((elm.x1, elm.y1), (elm.x2 - elm.x1), (elm.y2 - elm.y1), linewidth=0.3, edgecolor='b',
                              facecolor='none'))
            if len(pair) > 1:
                plt.gca().add_patch(
                    Rectangle((pair[0].x1, pair[0].y1), (pair[1].x2 - pair[0].x1), (pair[1].y2 - pair[0].y1),
                              linewidth=0.3, edgecolor='r',
                              facecolor='none'))
        file_name = "Pairs.png"
        plt.savefig(self.File_path + file_name, dpi=1000, bbox_inches='tight')
        print("File have been made: '" + self.File_path + file_name + "'")

    def display_lines(self, lines):
        """ Outputs a picture with headers and subheaders marked
        @param lines: A list of pairs and non pairs of headers
        """
        plt.imshow(Image.open(self.File_path + self.File_name + ".jp2"))
        plt.rcParams.update({'font.size': 3, 'text.color': "red", 'axes.labelcolor': "red"})

        for line in lines:
            plt.gca().add_patch(
                ConnectionPatch((line.x1, line.y1), (line.x2, line.y2), coordsA='data',linewidth=0.3, edgecolor='r', facecolor='none'))
        file_name = "Lines.png"
        plt.savefig(self.File_path + file_name, dpi=1000, bbox_inches='tight')
        print("File have been made: '" + self.File_path + file_name + "'")

    def __match_paragraphs_with_headers(self, headers_with_subheaders, paragraphs):
        pass
