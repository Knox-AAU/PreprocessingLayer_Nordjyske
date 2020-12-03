from alto_segment_lib.segment import Segment
from alto_segment_lib.segment import Line


class TestSegment:

    def test_compare_equal_segments(self):
        segment_one = Segment([200, 400, 400, 600])
        segment_two = Segment([200, 400, 400, 600])

        assert segment_one.compare(segment_two)

    def test_compare_unequal_segments(self):
        segment_one = Segment([200, 400, 400, 600])
        segment_two = Segment([200, 500, 400, 700])

        if not segment_one.compare(segment_two):
            assert True
        else:
            assert False

    def test_compare_on_none_segment_should_fail(self):
        segment_one = Segment([200, 400, 400, 600])

        if not segment_one.compare("string"):
            assert True
        else:
            assert False

    def test_between_x_coords_is_between(self):
        segment_one = Segment([200, 400, 400, 600])

        if segment_one.between_x_coordinates(300):
            assert True
        else:
            assert False

    def test_between_x_coords_not_between(self):
        segment_one = Segment([200, 400, 400, 600])

        if not segment_one.between_x_coordinates(405):
            assert True
        else:
            assert False

    def test_between_y_coords_is_between(self):
        segment_one = Segment([200, 400, 400, 600])

        if segment_one.between_y_coordinates(500):
            assert True
        else:
            assert False

    def test_between_y_coords_not_between(self):
        segment_one = Segment([200, 400, 400, 600])

        if not segment_one.between_y_coordinates(350):
            assert True
        else:
            assert False

    def test_width_instance_of_int(self):
        segment = Segment([200, 400, 400, 600])

        if isinstance(segment.width(), int):
            assert True
        else:
            assert False

    def test_width_success(self):
        segment = Segment([200, 400, 400, 600])
        actual_width = 200

        if segment.width() == actual_width:
            assert True
        else:
            assert False

    def test_width_failed(self):
        segment = Segment([200, 400, 400, 600])

        if segment.width() == 300:
            assert False
        else:
            assert True

    def test_height_instance_of_int(self):
        segment = Segment([200, 400, 400, 600])

        if isinstance(segment.height(), int):
            assert True
        else:
            assert False

    def test_height_success(self):
        segment = Segment([200, 400, 400, 600])
        actual_height = 200

        if segment.height() == actual_height:
            assert True
        else:
            assert False

    def test_height_failed(self):
        segment = Segment([200, 400, 400, 600])

        if segment.height() == 300:
            assert False
        else:
            assert True



class TestLine:

    def test_width_instance_of_int(self):
        line = Line([20, 30, 80, 50])

        if isinstance(line.width(), int):
            assert True
        else:
            assert False

    def test_width_success(self):
        line = Line([20, 30, 80, 50])
        actual_width = 60

        if line.width() == actual_width:
            assert True
        else:
            assert False

    def test_width_failed(self):
        line = Line([20, 30, 80, 50])

        if line.width() == 100:
            assert False
        else:
            assert True

    def test_height_instance_of_int(self):
        line = Line([20, 30, 80, 50])

        if isinstance(line.height(), int):
            assert True
        else:
            assert False

    def test_height_success(self):
        line = Line([20, 30, 80, 50])
        actual_height = 20

        if line.height() == actual_height:
            assert True
        else:
            assert False

    def test_height_failed(self):
        line = Line([20, 30, 80, 50])

        if line.height() == 74:
            assert False
        else:
            assert True
