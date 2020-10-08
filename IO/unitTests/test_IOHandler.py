from io import StringIO

import pytest

from knox_source_data_io.IOHandler import *
from knox_source_data_io.models.article import Article, Byline


class TestIOHandler:
    handler: IOHandler

    def setup_method(self, method):
        self.handler = IOHandler(Generator(app="This app", version=1.0), "Schema")

    def test_write_json_returns_valid_json_given_model_subclass(self):
        content_obj = Article()

        # Create StringIO object to store the output of the method
        outfile = StringIO()

        # Call method
        self.handler.write_json(content_obj, outfile)

        # Read the output
        outfile.seek(0)
        output_content = outfile.read()

        try:
            # Check to see if the output can parsed as JSON
            json.loads(output_content)
        except ValueError:
            pytest.fail("Generated string is not valid JSON")

        assert True

    def test_read_json_fails_due_to_file_not_existing(self):
        try:
            with open("/this/path/does/not/exist/and/will/cause/the/test/to/fail", 'r') as json_file:
                self.handler.read_json(json_file)
            assert False
        except OSError as e:
            assert True

    def test_convert_to_dict_adds_all_variables_from_the_obj_to_the_dict(self):
        article = Article()
        output = IOHandler.convert_obj_to_dict(article)

        # Check if all attributes are represented in the dictionary
        attributes = vars(article)
        for attribute in attributes:
            if attribute not in output:
                pytest.fail(f"The dictionary does not contain the attribute: {str(attribute)}")

        assert True

    def test_convert_to_dict_adds_class_reference_to_dict(self):
        article = Article()
        output = IOHandler.convert_obj_to_dict(article)

        if output.get("__class__") != article.__class__.__name__:
            pytest.fail(f"The dictionary does not contain reference to originating class")

    def test_convert_to_dict_adds_module_reference_to_dict(self):
        article = Article()
        output = IOHandler.convert_obj_to_dict(article)

        if output.get("__module__") != article.__module__:
            pytest.fail(f"The dictionary does not contain reference to originating module")

        assert True

    def test_dict_to_obj_receives_dict_with_class_and_returns_obj_of_class(self):
        article = Article()
        article.headline = "En god artikel"
        article.subhead = ""
        article.lead = ""
        article.byline = Byline(name="Thomas", email="thomas@tlorentzen.net")
        article.extracted_from.append("Some file")
        article.confidence = 1.0
        article.id = 0
        article.page = 0

        dict = article.__dict__
        dict["__class__"] = "Article"
        dict["__module__"] = "knox_source_data_io.models.article"

        output = IOHandler.convert_dict_to_obj(dict)
        if not isinstance(output, Article):
            pytest.fail("The output is not of the given type")
        assert True

    def test_dict_to_obj_receives_dict_without_class_and_returns_the_same_dictionary(self):
        article = Article()
        article.headline = "En god artikel"
        article.subhead = ""
        article.lead = ""
        article.byline = Byline(name="Thomas", email="thomas@tlorentzen.net")
        article.extracted_from.append("Some file")
        article.confidence = 1.0
        article.id = 0
        article.page = 0
        dictionary = article.__dict__

        output = IOHandler.convert_dict_to_obj(dictionary)

        assert output == dictionary

    def test_dict_to_obj_receives_dict_with_class_and_returns_obj_with_same_variables(self):
        article = Article()
        article.headline = "En god artikel"
        article.subhead = ""
        article.lead = ""
        article.byline = Byline(name="Thomas", email="thomas@tlorentzen.net")
        article.extracted_from.append("Some file")
        article.confidence = 1.0
        article.id = 0
        article.page = 0

        dict = article.__dict__
        dict["__class__"] = "Article"
        dict["__module__"] = "knox_source_data_io.models.article"

        output = IOHandler.convert_dict_to_obj(dict)
        for var in dict.keys():
            if not hasattr(output, var):
                pytest.fail("The output is not of the given type")

        assert True
#response = requests.get("https://knox.libdom.net/schema/article.schema.json")
#schema = response.json()