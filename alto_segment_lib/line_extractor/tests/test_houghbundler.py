from alto_segment_lib.segment import Line
from alto_segment_lib.line_extractor.hough_bundler import HoughBundler


def test_split_lines_into_horizontal_and_vertical():
    # arrange
    lines = [
        Line([0, 1, 0, 0]),  # vertical
        Line([1, 0, 0, 0]),  # horizontal
        Line([1, 1, 0, 0]),  # 45
        Line([2031, -3412, 35, -200]),  # random ass angle
    ]

    # act
    lines_x, lines_y = HoughBundler().split_lines_into_horizontal_and_vertical(lines)

    # assert
    assert lines[0] in lines_y
    assert lines[1] in lines_x
    assert lines[2] in lines_y
    assert lines[3] in lines_y


def test_vertical_merge_group_into_line():
    # arrange
    # 3 vertical lines:
    lines = [
        Line([10, 0, 11, 15]),
        Line([14, 21, 16, 51]),
        Line([13, 20, 13, 40]),
    ]

    # act
    line_result = HoughBundler().merge_group_into_line(lines)

    # assert
    assert line_result == Line([10, 0, 16, 51])


def test_horizontal_merge_group_into_line():
    # arrange
    # 3 vertical lines:
    lines = [
        Line([0, 10, 15, 11]),
        Line([21, 14, 51, 16]),
        Line([20, 13, 40, 13]),
    ]

    # act
    line_result = HoughBundler().merge_group_into_line(lines)

    # assert
    assert line_result == Line([0, 10, 51, 16])


def test_single_line_merge_group_into_line():
    # arrange
    lines = [Line([0, 1, 0, 0])]

    # act
    line_result = HoughBundler().merge_group_into_line(lines)

    # assert
    assert line_result == Line([0, 1, 0, 0])


def test_simple_distance_point_to_line():
    # arrange
    line = Line([0, 0, 0, 10])
    point = [5, 5]

    # act
    result = HoughBundler().distance_point_to_line(point, line)

    # assert
    assert result == 5


def test_closest_to_corner_distance_point_to_line():
    # arrange
    line = Line([0, 0, 0, 10])
    point_a = [5, -5]
    point_b = [5, 15]

    # act
    result_a = HoughBundler().distance_point_to_line(point_a, line)
    result_b = HoughBundler().distance_point_to_line(point_b, line)

    # assert
    assert abs(result_a - 7.07) < 0.01
    assert abs(result_b - 7.07) < 0.01


def test_small_line_distance_point_to_line():
    # arrange
    line = Line([0, 0, 0, 0])
    point_a = [100, 100]

    # act
    result_a = HoughBundler().distance_point_to_line(point_a, line)

    # assert
    assert result_a == 9999


def test_distance_in_limit_check_is_line_different():
    # arrange
    groups = [[Line([0, 0, 0, 10])]]
    line = Line([0, 11, 0, 21])

    hb = HoughBundler()
    hb.max_angle_to_merge = 0
    hb.max_distance_to_merge = 2

    # act
    result = hb.check_is_line_different(line, groups)

    # assert
    assert not result


def test_distance_out_of_limit_check_is_line_different():
    # arrange
    groups = [[Line([0, 0, 0, 10])]]
    line = Line([0, 15, 0, 22])

    hb = HoughBundler()
    hb.max_angle_to_merge = 0
    hb.max_distance_to_merge = 2

    # act
    result = hb.check_is_line_different(line, groups)

    # assert
    assert result


def test_angle_in_limit_check_is_line_different():
    # arrange
    groups = [[Line([0, 0, 0, 10])]]
    line = Line([0, 0, 2, 90])

    hb = HoughBundler()
    hb.max_angle_to_merge = 5
    hb.max_distance_to_merge = 0

    # act
    result = hb.check_is_line_different(line, groups)

    # assert
    assert not result


def test_angle_out_of_limit_check_is_line_different():
    # arrange
    groups = [[Line([0, 0, 0, 10])]]
    line = Line([0, 0, 8, 90])

    hb = HoughBundler()
    hb.max_angle_to_merge = 5
    hb.max_distance_to_merge = 0

    # act
    result = hb.check_is_line_different(line, groups)

    # assert
    assert result
