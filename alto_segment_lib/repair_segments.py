from typing import List

from alto_segment_lib.segment import Segment
from alto_segment_lib.segment_grouper import SegmentGrouper
from alto_segment_lib.segment_helper import SegmentHelper
import configparser
import statistics


class RepairSegments:
    """
    todo documentation and possibly rework
    """
    def __init__(self, segments, threshold: int = None):
        config = configparser.ConfigParser()
        config.read('config.ini')

        if threshold is None:
            self.__threshold = int(config['page_segmentation']['repair_segments_threshold'])
        else:
            self.__threshold = threshold

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
        """
        todo this needs documentation and possibly rework
        @return:
        """
        return_segments = self.__segments.copy()
        thresh_within = 5

        # Iterates through all segments and all other segments
        for segment in self.__segments:
            for subsegment in self.__segments:
                if not segment == subsegment:
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

        return return_segments


def add_segment(segments: list, coordinates: list, lines, seg_type: str):
    segment = Segment(coordinates)
    segment.lines = lines
    segment.type = seg_type
    segments.append(segment)


def merge_segments(segments: List[Segment]) -> List[Segment]:
    """
    Merges segments into bigger chunks based on distance

    @type segments: List of segments
    @return list[Segment]
    """
    grouper = SegmentGrouper()
    segments_ordered = grouper.order_segments_by_x1_y1(segments)
    sub_segment_list = segments_ordered.copy()
    already_merged = []
    merged_segments = []
    merge_distance_threshold = 50  # in px

    for segment in segments_ordered:
        if segment in already_merged:
            continue

        skip_segment = False

        for merged_segment in merged_segments:
            # Adding one since some segments are starting at exactly same y as parent
            if SegmentHelper.inside_box([merged_segment.x1, merged_segment.y1, merged_segment.x2, merged_segment.y2], segment.x1, segment.y1+1):
                skip_segment = True
                break

        if skip_segment:
            continue

        segment_width = segment.width()
        sub_segment_list.remove(segment)

        for sub_segment in sub_segment_list:

            sub_segment_width = sub_segment.width()
            merged = False

            # Check from current segments lower left corner if any segments are within threshold distance.
            if SegmentHelper.distance_between_coordinates(segment.x1, segment.y2, sub_segment.x1, sub_segment.y1) <= merge_distance_threshold:

                # Generate coordinates equal to the empty space on the right or left, to check if
                # we will overlap existing elements by merging
                if segment_width > sub_segment_width:
                    ghost_box = [sub_segment.x2, sub_segment.y1, segment.x2, sub_segment.y2]
                elif segment_width < sub_segment_width:
                    ghost_box = [segment.x2, segment.y1, sub_segment.x2, segment.y2]
                else:
                    # It is possibel that the segment and sub_segment have same lenght then dont
                    # check for conflicts.
                    ghost_box = None

                conflicting_segments = False

                # Check for intersecting segments
                if ghost_box is not None:
                    for other_segment in segments:
                        if SegmentHelper.inside_box(ghost_box, other_segment.x1, other_segment.y1):
                            conflicting_segments = True
                            break

                if not conflicting_segments:
                    segment.x1 = min(segment.x1, sub_segment.x1)
                    segment.y1 = min(segment.y1, sub_segment.y1)
                    segment.x2 = max(segment.x2, sub_segment.x2)
                    segment.y2 = max(segment.y2, sub_segment.y2)
                    merged = True

            if merged:
                already_merged.append(sub_segment)

        merged_segments.append(segment)

    return merged_segments
