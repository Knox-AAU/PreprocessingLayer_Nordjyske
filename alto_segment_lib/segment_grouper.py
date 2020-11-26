import statistics
from os import environ
from alto_segment_lib.segment import Segment, Line, SegmentGroup, SegmentType
from alto_segment_lib.segment_group_handler import SegmentGroupHandler
from alto_segment_lib.segment_helper import SegmentHelper
from alto_segment_lib.line_extractor.extractor import LineExtractor
environ["OPENCV_IO_ENABLE_JASPER"] = "true"


class SegmentGrouper:

    def group_segments_in_order(self, headers_in: list[Segment], paragraphs_in: list[Segment], lines_in: list[Line]):
        segments = paragraphs_in.copy()
        segments.extend(headers_in)

        bounds = SegmentHelper.get_content_bounds(segments)

        # remove all lines in the first and last 10% of the page height
        line_bound = (bounds[3] * 0.1)

        # Convert all lines to segments
        lines = [element for element, element in enumerate(lines_in) if
                 element.is_horizontal() and line_bound < element.y1 < (bounds[3] - line_bound)]

        for line in lines:
            length = line.width()
            # We shorten all lines by 5% in both ends to prevent column overlap
            line.x1 = line.x1 * 1.05
            line.x2 = line.x2 * 0.95
            segments.append(self.__convert_line_to_segment(line))

        # segments = [element for element, element in enumerate(segments) if
        #            line_bound < element.y1 < (bounds[3] - line_bound)]

        # Sort headers and paragraphs by lowest x, lowest y.
        segments = self.__order_segments_by_x1_y1(segments)

        segments_to_check = segments.copy()
        group_handler = SegmentGroupHandler()
        previous_lowest_y = 0

        for segment in segments:
            # Skip all segments that should not be checked
            if segment not in segments_to_check:
                continue

            if segment.type == SegmentType.heading:
                # End the current group, if the encountered header is beneath the previous segment
                if segment.y1 > previous_lowest_y:
                    group_handler.end_group()

                # Start a new group and add all lines of the header to the article
                group_handler.start_group()
                group_handler.add_segment(segment)
            elif segment.type == SegmentType.line:
                self.__finish_article_based_on_line(group_handler, segment, segments_to_check)
            else:
                group_handler.add_segment(segment)

            previous_lowest_y = segment.y2

            # Remove the segment
            segments_to_check.remove(segment)

        group_handler.finalize()
        return group_handler.groups

    def __finish_article_based_on_line(self, group_handler: SegmentGroupHandler, line: Segment,
                                       segments_to_check: list[Segment]):
        # The ghost_header is used as a line to only handled articles within the bound of it and the encountered line
        # ghost_header = group_handler.get_header_segment()

        # The line is used to limit the article
        splitting_line = line
        segments_added: list[Segment] = []

        # Get a new list of segments starting from the segment following the line, to avoid handling the line
        following_segments = iter(segments_to_check)
        next(following_segments)

        for seg in following_segments:
            if seg.type == SegmentType.line or seg.y1 > splitting_line.y2:
                # We encountered another line or the segment is below the line
                continue

            if splitting_line.x1 > seg.get_center()[0] or seg.get_center()[0] > splitting_line.x2:
                # The segment is to the right of the line
                break

            if seg.type == SegmentType.heading:
                # A header has been encountered above the line
                group_handler.end_group()
                group_handler.start_group()
                group_handler.add_segment(seg)
                continue

            # The segment is above the line and within the x1 and x2 coordinates of the line
            group_handler.add_segment(seg)
            segments_added.append(seg)

        [segments_to_check.remove(seg) for seg in segments_added]

    def __convert_line_to_segment(self, line):
        segment = Segment()
        segment.type = SegmentType.line
        segment.x1 = line.x1
        segment.x2 = line.x2
        segment.y1 = line.y1
        segment.y2 = line.y2
        return segment

    def __order_segments_by_x1_y1(self, segments: list[Segment]):
        # Group segments by x1, if segment.x1 is within range of the first element of an existing group, else create new group
        # Run through each group and sort by y1
        # Merge groups into collective list
        segments_grouped = []

        # Go through each segment
        for segment in segments:
            segment_added = False
            threshold = segment.get_center()[0] / 2

            # Find the associated group
            for segment_group in segments_grouped:
                # If group found, add segment and move on to next segment
                if abs(segment_group[0].x1 - segment.x1) < threshold:
                    segment_group.append(segment)
                    segment_added = True
                    break

            # If group not found, add new group with segment
            if not segment_added:
                segments_grouped.append([segment])

        # Order each group by y1
        segments_grouped = [sorted(group, key=lambda s: s.y1) for group in segments_grouped]

        # Return the segments as a 1-dimensional list
        return [segment for group in segments_grouped for segment in group]
