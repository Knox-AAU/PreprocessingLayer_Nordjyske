import json

import pytest

from models.article import Article
from models.wrapper import Wrapper


class TestWrapper:
    wrapper: Wrapper

    def setup_method(self, method):
        self.wrapper = Wrapper()

    def test_sets_content_to_given_article(self):
        article = Article()
        self.wrapper.set_content(article)
        assert self.wrapper.content == article

    def test_does_not_set_content_given_string(self):
        self.wrapper.set_content("string")
        assert self.wrapper.content is None

    def test_to_json_gives_valid_json_on_call(self):
        output = self.wrapper.to_json()
        try:
            json.loads(output)
            assert True
        except ValueError:
            pytest.fail("Generated string is not valid JSON")
