import json


class Byline:
    name: str = ""
    email: str = ""

    def __init__(self, values: dict = None, **kwargs):
        values = values if values is not None else kwargs
        self.name = values.get('name')
        self.email = values.get('email', None)


class Paragraph:
    kind: str = ""
    value: str = ""

    def __init__(self, values: dict = None, **kwargs):
        values = values if values is not None else kwargs
        self.kind = values.get("kind", "")
        self.value = values.get("value", "")


class Article:
    extractedFrom: list = []
    confidence: float = 1.0
    publisher: str = ""
    publishedAt: str = ""
    publication: str = ""
    page: int = 0

    id: int = 0
    title: str = ""
    trompet: str = ""
    byline: Byline = Byline
    paragraphs: list = []

    def __init__(self, values: dict = None, **kwargs):
        values = values if values is not None else kwargs
        self.extractedFrom = values.get("extractedFrom", [])
        self.confidence = values.get("confidence", 1.0)
        self.publisher = values.get("publisher", "")
        self.publishedAt = values.get("publishedAt", "")
        self.publication = values.get("publication", "")
        self.page = values.get("page", 0)
        self.id = values.get("id", 0)
        self.title = values.get("title", "")
        self.trompet = values.get("trompet", "")
        self.byline = values.get("byline", Byline)
        self.paragraphs = values.get("paragraphs", [])

    def addParagraph(self, paragraph):
        if isinstance(paragraph, Paragraph):
            self.paragraphs.append(paragraph)

    def getParagraphs(self):
        return self.paragraphs

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
