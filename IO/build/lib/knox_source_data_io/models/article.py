import json

from knox_source_data_io.models.model import Model


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


class Article(Model):
    """
    A class used to represent an Article

    ...

    Attributes
    ----------
    id : int
        the article id (default 0)
    title : str
        the article title
    trompet : str
        the article trompet (default "")
    byline : Byline
        the article byline
    paragraphs : list
        a list of paragraph elements
    confidence : float
        a confidence score, describing the confidence of correct data (default 1.0)
    publisher : str
        the publisher
    publishedAt : str
        the article publish date
    publication : str
        the magazine/newspaper where it was published
    extractedFrom : list
        a list of path to source files
    page : int
        the page number where the article was found (default 0)

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    """

    id: int
    headline: str
    subhead: str
    byline: Byline
    lead: str
    paragraphs: list
    confidence: float
    publisher: str
    published_at: str
    publication: str
    extracted_from: list
    page: int

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
        self.extracted_from = values.get("extracted_from", [])
        self.confidence = values.get("confidence", 1.0)
        self.publisher = values.get("publisher", "")
        self.published_at = values.get("published_at", "")
        self.publication = values.get("publication", "")
        self.page = values.get("page", 0)
        self.id = values.get("id", 0)
        self.headline = values.get("title", "")
        self.subhead = values.get("subhead", "")
        self.byline = values.get("byline", Byline())
        self.lead = values.get("lead", "")
        self.paragraphs = values.get("paragraphs", [])

    def add_paragraph(self, paragraph: Paragraph):
        """Add a paragraph the the article

        It simply adds a paragraph to the list of paragraphs on the article.

        Parameters
        ----------
        paragraph : Paragraph
            an instance of Paragraph containing the required properties.
        """
        if type(paragraph) == Paragraph:
            self.paragraphs.append(paragraph)

    def to_json(self):
        """Converts the object to json string

        Properties are sorted and indented using 4 spaces.
        """

        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

