from alto_segment_lib.segment import Segment
from alto_segment_lib.segment_helper import SegmentHelper
from alto_segment_lib.segment_grouper import SegmentGrouper
import statistics


def add_segment(segments: list, coordinates: list, lines, seg_type: str):
    segment = Segment(coordinates)
    segment.lines = lines
    segment.type = seg_type
    segments.append(segment)


class RepairSegments:

    def __init__(self, segments, threshold: int = 10):
        self.__segments = segments
        self.__threshold = threshold
        self.__new_segments = []
        self.__median_paragraph_width = 0
        self.__analyze_coordinates()

    def __analyze_coordinates(self):
        all_para = []
        for segment in self.__segments:
            all_para.append(segment.x2 - segment.x1)
        self.__median_paragraph_width = statistics.median(all_para)

    def repair_rows(self):
        return_segments = self.__segments.copy()
        thresh_within = 5

        # Iterates through all segments and all other segments
        for segment in self.__segments:
            for subsegment in self.__segments:
                if not segment.compare(subsegment):
                    thresh_close_to = subsegment.width() * 0.05
                    if subsegment in return_segments:
                        subsegment_index = return_segments.index(subsegment)
                    else:
                        continue
                    # Checks if the subsegment is entirely within the segment
                    if segment.between_y_coordinates(subsegment.y1 + thresh_within) \
                            and segment.between_y_coordinates(subsegment.y2 - thresh_within) \
                            and segment.between_x_coordinates(subsegment.x1 + thresh_within) \
                            and segment.between_x_coordinates(subsegment.x2 - thresh_within):
                        return_segments.remove(subsegment)
                    # Checks if subsegment's x-coords are close to segment
                    elif segment.between_x_coordinates(subsegment.x1 + thresh_close_to) \
                            and segment.between_x_coordinates(subsegment.x2 - thresh_close_to):
                        # Checks if the upper y-coordinate for subsegment is withing segment
                        if segment.between_y_coordinates(subsegment.y1):
                            # Move y-coordinate to be beside segment
                            return_segments[subsegment_index].y1 = segment.y2
                        # Checks if the lower y-coordinate for subsegment is within segment
                        elif segment.between_y_coordinates(subsegment.y2):
                            # Move y-coordinate to be beside segment
                            return_segments[subsegment_index].y2 = segment.y1

        return return_segments.copy()

    def get_median_column_width(self):
        return self.__median_paragraph_width

    def merge_segments(self, segments: list):
        grouper = SegmentGrouper()
        segments_ordered = grouper.order_segments_by_x1_y1(segments)

        sub_segment_list = segments_ordered.copy()

        already_merged = []
        merge_distance_threshold = 200  # in px
        merged_segments = []

        for segment in segments_ordered:
            if segment in already_merged:
                continue

            # segment_center = segment.get_center()
            lower_left_circle_x = segment.x1
            lower_left_circle_y = segment.y2
            lower_right_circle_x = segment.x2
            lower_right_circle_y = segment.y2
            segment_width = segment.width()
            sub_segment_list.remove(segment)

            for sub_segment in sub_segment_list:

                # Skip segments that are not in same column
                if sub_segment in merged_segments or sub_segment.x2 < segment.x1 or sub_segment.x1 > segment.x1 or sub_segment.x1 > segment.x1 or sub_segment.y2 < segment.y2:
                    continue

                sub_segment_width = sub_segment.width()
                merged = False

                # Check left first
                #if SegmentHelper.inside_box([segment.x1 - merge_distance_threshold, segment.y1 - merge_distance_threshold, segment.x2 + merge_distance_threshold, segment.y2 + merge_distance_threshold], sub_segment.x1, sub_segment.y1):
                if SegmentHelper.distance_between_coordinates(lower_left_circle_x, lower_left_circle_y, sub_segment.x1, sub_segment.y1) <= merge_distance_threshold:
                #if SegmentHelper.isInsideCircle(, merge_distance_threshold, sub_segment.x1, sub_segment.y1):

                    if segment_width > sub_segment_width:
                        ghost_box = [sub_segment.x2, sub_segment.y1, segment.x2, sub_segment.y2]
                    elif segment_width < sub_segment_width:
                        ghost_box = [segment.x2, segment.y1, sub_segment.x2, segment.y2]
                    else:
                        ghost_box = None

                    # Fill empty space
                    conflicting_segment = False

                    if ghost_box is not None:
                        for other_segment in segments:
                            if SegmentHelper.inside_box(ghost_box, other_segment.x1, other_segment.y1):
                                conflicting_segment = True
                                break

                    if not conflicting_segment:
                        segment.y2 = max(segment.y2, sub_segment.y2)
                        segment.x2 = max(segment.x2, sub_segment.x2)
                        segment.x1 = min(segment.x1, sub_segment.x1)
                        segment.y1 = min(segment.y1, sub_segment.y1)
                        lower_right_circle_y = segment.y2
                        merged = True

                # Check right after
                # if merged is False and SegmentHelper.isInsideCircle(lower_right_circle_x, lower_right_circle_y, merge_distance_threshold, sub_segment.x2, sub_segment.y1):
                #     segment.y2 = sub_segment.y2
                #     merged = True

                if merged:
                    already_merged.append(sub_segment)

            merged_segments.append(segment)

        return merged_segments


