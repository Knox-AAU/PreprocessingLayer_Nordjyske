from io import StringIO

import pytest

from IOHandler import *
from models.article import Article


class TestIOHandler:
    handler: IOHandler

    def setup_method(self, method):
        self.handler = IOHandler(Generator(app="This app", version=1.0), None)

    def test_write_json_returns_valid_json(self):
        content_obj = Article()

        outfile = StringIO()
        self.handler.write_json(content_obj, outfile)

        outfile.seek(0)
        output_content = outfile.read()
        try:
            json.loads(output_content)
            assert True
        except ValueError:
            pytest.fail("Generated string is not valid JSON")

    def test_read_json_fails_due_to_file_not_existing(self):
        try:
            with open("/this/path/does/not/exist/and/will/cause/the/test/to/fail", 'r') as json_file:
                self.handler.read_json(json_file)
            assert False
        except OSError as e:
            assert True

    def test_convert_to_dict(self):
        assert False

    def test_dict_to_obj(self):
        assert False
#response = requests.get("https://knox.libdom.net/schema/article.schema.json")
#schema = response.json()