from IO.models.article import *
from jsonschema import validate
import requests, json


class TestArticle:
    article: Article

    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.article = Article()

    def test_add_paragraph_gives_article_with_paragraph_on_paragraph(self):
        paragraph = Paragraph()
        self.article.add_paragraph(paragraph)
        assert self.article.paragraphs.__len__() == 1

    def test_add_paragraph_gives_article_without_paragraph_on_string(self):
        self.article.add_paragraph("string")
        assert self.article.paragraphs.__len__() < 1

    def test_to_json_gives_json_complying_with_schema_on_call(self):
        output = self.article.to_json()
        response = requests.get("https://knox.libdom.net/schema/article.schema.json")
        schema = response.json()
        assert validate(output, schema)
