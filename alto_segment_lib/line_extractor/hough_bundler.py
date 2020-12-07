# pylint: skip-file
import configparser
import math
from math import atan2

from alto_segment_lib.segment import Line


class HoughBundler:
    '''Clasterize and merge each cluster of cv2.HoughLinesP() output
    a = HoughBundler()
    foo = a.process_lines(houghP_lines, binary_image)
    '''

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.max_distance_to_merge = int(self.config['hough_bundler']['max_distance_to_merge'])
        self.max_angle_to_merge = int(self.config['hough_bundler']['max_angle_to_merge'])

    def check_is_line_different(self, line_new, groups):
        '''Check if line have enough distance and angle to be count as similar
        '''
        for group in groups:
            # walk through existing line groups
            for line_old in group:
                # check distance
                if self.get_distance(line_old, line_new) <= self.max_distance_to_merge:
                    # check the angle between lines
                    orientation_new = line_new.get_orientation()
                    orientation_old = line_old.get_orientation()
                    # if all is ok -- line is similar to others in group
                    if abs(orientation_new - orientation_old) <= self.max_angle_to_merge:
                        group.append(line_new)
                        return False
        # if it is totally different line
        return True

    def distance_point_to_line(self, point, line):
        """Get distance between point and line
        http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/source.vba
        """
        px, py = point

        def line_magnitude(x1, y1, x2, y2):
            'Get line (aka vector) length'
            lineMagnitude = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))
            return lineMagnitude

        #todo wtf is this next 4 lines?
        line_mag = line.length
        if line_mag < 0.00000001:
            distance_point_line = 9999
            return distance_point_line

        u1 = (((px - line.x1) * (line.x2 - line.x1)) + ((py - line.y1) * (line.y2 - line.y1)))
        u = u1 / (line_mag * line_mag)

        if (u < 0.00001) or (u > 1):
            # closest point does not fall within the line segment, take the shorter distance to an endpoint
            ix = line_magnitude(px, py, line.x1, line.y1)
            iy = line_magnitude(px, py, line.x2, line.y2)
            if ix > iy:
                distance_point_line = iy
            else:
                distance_point_line = ix
        else:
            # Intersecting point is on the line, use the formula
            ix = line.x1 + u * (line.x2 - line.x1)
            iy = line.y1 + u * (line.y2 - line.y1)
            distance_point_line = line_magnitude(px, py, ix, iy)

        return distance_point_line

    def get_distance(self, a_line, b_line):
        """Get all possible distances between each dot of two lines and second line
        return the shortest
        """
        dist1 = self.distance_point_to_line([a_line.x1, a_line.y1], b_line)
        dist2 = self.distance_point_to_line([a_line.x2, a_line.y2], b_line)
        dist3 = self.distance_point_to_line([b_line.x1, b_line.y1], a_line)
        dist4 = self.distance_point_to_line([b_line.x1, b_line.y1], a_line)

        return min(dist1, dist2, dist3, dist4)

    def merge_lines_into_groups(self, lines):
        'Clusterize (group) lines'
        groups = [[lines[0]]]  # all lines groups are here
        # first line will create new group every time
        # if line is different from existing gropus, create a new group
        for line_new in lines[1:]:
            if self.check_is_line_different(line_new, groups):
                groups.append([line_new])

        return groups

    def merge_group_into_line(self, lines):
        """Sort lines cluster and return first and last coordinates
        """
        orientation = lines[0].get_orientation()

        # special case
        if len(lines) == 1:
            return lines[0]

        # [[1,2,3,4],[]] to [[1,2],[3,4],[],[]]
        points = []
        for line in lines:
            points.append([line.x1, line.y1])
            points.append([line.x2, line.y2])
        # if horizontal
        if 45 < orientation < 135:
            # sort by x
            points = sorted(points, key=lambda point: point[0])
        else:
            # sort by y
            points = sorted(points, key=lambda point: point[1])

        # return first and last point in sorted group
        # [[x,y],[x,y]]
        return Line([points[0][0], points[0][1], points[-1][0], points[-1][1]])

    def process_lines(self, lines):
        '''Main function for lines from cv.HoughLinesP() output merging
        for OpenCV 3
        lines -- cv.HoughLinesP() output
        img -- binary image.jp2
        '''
        lines_x, lines_y = self.split_lines_into_horizontal_and_vertical(lines)
        merged_lines_all = []

        # for each cluster in vertical and horizantal lines leave only one line
        for i in [lines_x, lines_y]:
            if len(i) > 0:
                merged_lines_all.extend(
                    [self.merge_group_into_line(group) for group in self.merge_lines_into_groups(i)])

        return merged_lines_all


    def split_lines_into_horizontal_and_vertical(self, lines):
        lines_vertical = []
        lines_horizontal = []
        # for every line of cv2.HoughLinesP()
        for line_i in lines:
            orientation = line_i.get_orientation()
            # if horizontal
            if 45 < orientation < 135:
                lines_vertical.append(line_i)
            else:
                lines_horizontal.append(line_i)
        lines_horizontal = sorted(lines_horizontal, key=lambda line: line.y1)
        lines_vertical = sorted(lines_vertical, key=lambda line: line.x1)
        return lines_vertical, lines_horizontal
