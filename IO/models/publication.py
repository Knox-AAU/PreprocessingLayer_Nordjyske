import json
from models.article import *

class Byline:
    """
    A class used to represent a Byline

    ...

    Attributes
    ----------
    name : str
        the author name (default "")
    email : str, optional
        the author email (default "")
    """

    name: str
    email: str

    def __init__(self, values: dict = None, **kwargs):
        values = values if values is not None else kwargs
        self.name = values.get('name')
        self.email = values.get('email', None)


class Paragraph:
    """
    A class used to represent a Paragraph

    ...

    Attributes
    ----------
    kind : str
        the type of paragraph
    value : str
        the paragraph
    """

    kind: str
    value: str

    def __init__(self, values: dict = None, **kwargs):
        """
        Parameters
        ----------
        values : dict
            The class values in dict format (default None)
        kwargs :
            The class values as kwargs arguments
        """

        values = values if values is not None else kwargs
        self.kind = values.get("kind", "")
        self.value = values.get("value", "")


class Article:
    """
    A class used to represent an Article

    ...

    Attributes
    ----------


    publishedAt : str
        the article publish date
    publication : str
        the magazine/newspaper where it was published
    publisher : str
        the publisher
    pages : int
        the total number of pages
    articles : list
        a list of articles

    Methods
    -------
    add_article(sound=None)
        Prints the animals name and what sound it makes
    """

    publication: str
    published_at: str
    publisher: str
    pages: int
    articles: list

    def __init__(self, values: dict = None, **kwargs):
        """
        Parameters
        ----------
        values : dict
            The class values in dict format (default None)
        kwargs :
            The class values as kwargs arguments
        """

        values = values if values is not None else kwargs
        self.publisher = values.get("publisher", "")
        self.published_at = values.get("published_at", "")
        self.publication = values.get("publication", "")
        self.pages = values.get("pages", 0)
        self.articles = values.get("articles", [])

    def add_article(self, article: Article):
        """Add a article the publication

        It simply adds a article to the list of articles on the publication.

        Parameters
        ----------
        article : Article
            an instance of Paragraph containing the required properties.
        """

        self.articles.append(article)

    def to_json(self):
        """Converts the object to json string

        Properties are sorted and indented using 4 spaces.
        """

        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
