import requests


class TestIOHandler:
    def test_write_json(self):
        response = requests.get("https://knox.libdom.net/schema/article.schema.json")
        schema = response.json()
        assert False

    def test_read_json(self):
        assert False

    def test_convert_to_dict(self):
        assert False

    def test_dict_to_obj(self):
        assert False
