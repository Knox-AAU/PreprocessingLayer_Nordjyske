from datetime import datetime
import json


class Byline:
    name = ""
    email = ""

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name')
        self.email = kwargs.get('email', None)


class Paragraph:
    kind = ""
    value = ""

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class Article:
    extractedFrom = []
    confidence = 1.0
    publisher = ""
    publishedAt = ""
    publication = ""
    page = 0

    id = 0
    title = ""
    trompet = ""
    byline = Byline
    paragraphs = []

    def addParagraph(self, paragraph):
        if isinstance(paragraph, Paragraph):
            self.paragraphs.append(paragraph)

    def getParagraphs(self):
        return self.paragraphs

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=True)
