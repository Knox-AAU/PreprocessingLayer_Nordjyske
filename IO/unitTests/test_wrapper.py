import json
import pytest
from knox_source_data_io.models.publication import Publication
from knox_source_data_io.models.wrapper import Wrapper


class TestWrapper:
    wrapper: Wrapper

    def setup_method(self, method):
        self.wrapper = Wrapper()

    def test_sets_content_to_given_publication(self):
        publication = Publication()
        self.wrapper.set_content(publication)
        assert self.wrapper.content == publication

    def test_set_content_does_not_set_content_given_string(self):
        self.wrapper.set_content("string")
        assert self.wrapper.content is None

    def test_to_json_gives_valid_json_on_call(self):
        output = self.wrapper.to_json()
        try:
            json.loads(output)
            assert True
        except ValueError:
            pytest.fail("Generated string is not valid JSON")
