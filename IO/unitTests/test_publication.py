import pytest
import json

from knox_source_data_io.models.publication import Publication, Article, Paragraph


class TestPublication:
    article: Article
    publication: Publication

    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.article = Article()
        self.publication = Publication()

    def test_add_article_adds_article_given_article(self):
        article = Article()
        self.publication.add_article(article)
        assert self.publication.articles.__len__() == 1

    def test_add_article_does_not_add_article_given_string(self):
        self.publication.add_article("string")
        assert self.publication.articles.__len__() < 1

    def test_add_paragraph_adds_paragraph_given_paragraph(self):
        paragraph = Paragraph()
        self.article.add_paragraph(paragraph)
        assert self.article.paragraphs.__len__() == 1

    def test_add_paragraph_does_not_add_paragraph_given_string(self):
        self.article.add_paragraph("string")
        assert self.article.paragraphs.__len__() < 1

    def test_publication_to_json_gives_valid_json_on_call(self):
        output = self.publication.to_json()
        try:
            # Check to see if the output can parsed as JSON
            json.loads(output)
            assert True
        except ValueError:
            pytest.fail("Generated string is not valid JSON")

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """

