import configparser
import numpy as np
import math
from math import atan2
from os import environ
from alto_segment_lib.line_extractor.hough_bundler import HoughBundler
from alto_segment_lib.segment import Line
environ["OPENCV_IO_ENABLE_JASPER"] = "true"
from cv2 import cv2


class LineExtractor:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.rho = int(self.config['line_extraction']['rho'])  # distance resolution in pixels of the Hough grid
        self.theta = np.pi / int(
            self.config['line_extraction']['theta_divisions'])  # angular resolution in radians of the Hough grid
        self.threshold = int(
            self.config['line_extraction']['threshold'])  # minimum number of votes (intersections in Hough grid cell)
        self.min_line_length = int(
            self.config['line_extraction']['min_line_length'])  # minimum number of pixels making up a line
        self.max_line_gap = int(
            self.config['line_extraction']['max_line_gap'])  # maximum gap in pixels between connectable line segments
        self.diversion = int(self.config['line_extraction']['diversion'])
        self.adaptive_threshold = [int(a) for a in self.config['line_enhancement']['threshold'].split(',')]
        self.vertical_size = int(self.config['line_enhancement']['vertical_size'])
        self.horizontal_size = int(self.config['line_enhancement']['horizontal_size'])

    def extract_lines_via_path(self, image_path: str):
        """
        Executes line extraction on the image located at the given image_path

        @param image_path: The path to the image from which the lines should be extracted
        @return: List of extracted lines
        """
        image = cv2.imread(image_path, cv2.CV_8UC1)

        lines = self.extract_lines_via_image(image)
        extended_lines = self.extend_lines_vertically(lines, image)
        final_lines = self.remove_outline_lines(extended_lines, image)
        return final_lines

    def extract_lines_via_image(self, image: object):
        """
        Extracts lines from the image

        @param image: The CV2 image object from which the lines should be extracted
        @return: List of extracted lines
        """
        enhanced_image = self.clarify_lines(image)
        return self.get_lines_from_binary_image(enhanced_image)

    @staticmethod
    def remove_outline_lines(lines, image):
        """
        Removes the lines constituting the outline of the image

        @param lines: List of lines from which the outline lines should be removed
        @param image: The image from which the lines were extracted
        @return: List of lines with the outline lines removed
        """
        outline_stop = 100
        max_x, max_y = image.shape
        lines_to_remove = []

        for line in lines:
            if 0 < line.x1 < outline_stop and 0 < line.x2 < outline_stop or max_x - outline_stop < line.x1 < max_x and max_x - outline_stop < line.x2 < max_x:
                lines_to_remove.append(line)

            elif 0 < line.y1 < outline_stop and 0 < line.y2 < outline_stop or max_y - outline_stop < line.y1 < max_y and max_y - outline_stop < line.y2 < max_y:
                lines_to_remove.append(line)

        lines_to_remove.reverse()

        for line in lines_to_remove:
            lines.remove(line)

        return lines

    def clarify_lines(self, image):
        """
        Turns the vertical and horizontal lines in the image white and everything else black

        @param image: The image on which the processing should be performed
        @return: The image with only the lines visible
        """

        # apply mean tresholding to bring out lines
        image_thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                             self.adaptive_threshold[0],
                                             self.adaptive_threshold[1])

        # saves the thresholding image for later use
        image_horizontal = image_thresh
        image_vertical = image_thresh

        # gets height and width of image, and specifies how long a line can be
        horizontal_size, vertical_size = image_thresh.shape
        horizontal_size = int(horizontal_size / self.horizontal_size)
        vertical_size = int(vertical_size / self.vertical_size)

        # opencv function to find horizontal/vertical lines
        horizontal_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
        vertical_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))

        kernel = np.ones((1, 1), np.uint8)
        image_horizontal = cv2.erode(image_horizontal, horizontal_structure, kernel)
        image_horizontal = cv2.dilate(image_horizontal, horizontal_structure, kernel)

        kernel = np.ones((1, 1), np.uint8)
        image_vertical = cv2.erode(image_vertical, vertical_structure, kernel)
        image_vertical = cv2.dilate(image_vertical, vertical_structure, kernel)

        merged_image = cv2.addWeighted(image_horizontal, 1, image_vertical, 1, 0)

        return merged_image

    def get_lines_from_binary_image(self, image):
        """
        Extract the lines from a binary image

        @param image: The CV2 image form which the lines should be extracted
        @return: List of extracted lines
        """
        lines = cv2.HoughLinesP(image, self.rho, self.theta, self.threshold, np.array([]),
                                self.min_line_length, self.max_line_gap)

        line_objects = [Line.from_array(line[0]) for line in lines]

        lines_groups = HoughBundler().process_lines(line_objects)

        return self.filter_by_angle_diversion_from_horizontal_and_vertical(lines_groups)

    def filter_by_angle_diversion_from_horizontal_and_vertical(self, lines_groups):
        """
        Removes lines that are not horizontal nor vertical

        @param lines_groups: List of lines to filter
        @return: List of filtered lines
        """
        min_horizontal_angle = -self.diversion
        max_horizontal_angle = self.diversion
        min_vertical_angle = 90 - self.diversion
        max_vertical_angle = 90 + self.diversion
        filtered_lines = []

        for line in lines_groups:
            angle = atan2(line.y2 - line.y1, line.x2 - line.x1) * 180.0 / math.pi
            if min_vertical_angle < angle < max_vertical_angle or min_horizontal_angle < angle < max_horizontal_angle:
                filtered_lines.append(line)
        return filtered_lines

    @staticmethod
    def show_lines_on_image(image, lines, name):
        """
        Displays the lines on the image

        @param image: The image to display the lines on
        @param lines: The lines to display
        @return: void
        """
        line_image = np.copy(image) * 0  # creating a blank to draw lines on
        line_image = cv2.cvtColor(line_image, cv2.COLOR_GRAY2RGB)
        for line in lines:
            cv2.line(line_image, (line.x1, line.y1), (line.x2, line.y2), (0, 0, 255), 3)

        image_in_color = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        lines_edges = cv2.addWeighted(image_in_color, 0.5, line_image, 1, 0)

        cv2.imwrite(r"/home/jakob/Desktop/test/2015-01-01-01/" + name + ".png", lines_edges)
        # cv2.imwrite(r"C:\Users\Alexi\Desktop\KnoxFiler\5\2015-01-01-01" + name + ".png", lines_edges)
        # cv2.imwrite("C:\\Users\\Alexi\\Desktop\\KnoxTing\\5\\2015-01-01-01\\" + name + ".png", lines_edges)
        # cv2.imwrite("E:\\Nordjyske\\2015-01-01-01\\" + name + ".png", lines_edges)
        # print("done")
        # cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        # cv2.imshow("image", lines_edges)
        # cv2.waitKey(0)

    @staticmethod
    def extend_lines_vertically(lines, image):
        """
        Extends the lines vertically by decreasing y1 and increasing y2 of the lines

        @param lines: The lines to extend
        @param image: The image from which the lines are extracted
        @return: List of updated lines
        """
        horizontal_size, vertical_size = image.shape

        for line in lines:
            if not line.is_horizontal():
                if line.y2 > vertical_size - 200:
                    line.y2 = line.y2 + 150

        return lines

    @staticmethod
    def correct_lines(lines):
        """
        ToDo: Add this!!!

        @param lines:
        @return:
        """
        new_lines = []

        for line in lines:
            if not line.is_horizontal_or_vertical():
                continue

            if not line.is_horizontal():
                if line.x1 < line.x2:
                    temp = line.x1
                    line.x1 = line.x2
                    line.x2 = temp

                median = int((line.x1 - line.x2) / 2)
                line.x1 -= median
                line.x2 += median
            else:
                if line.y1 < line.y2:
                    temp = line.y1
                    line.y1 = line.y2
                    line.y2 = temp

                median = int((line.y1 - line.y2) / 2)
                line.y1 -= median
                line.y2 += median

            new_lines.append(line)

        return new_lines
