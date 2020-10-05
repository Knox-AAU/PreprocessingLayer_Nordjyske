from enum import Enum
from datetime import datetime
import json


class Type(Enum):
    ARTICLE = "article"
    MANUAL = "manual"


class Generator:
    app = ""
    version = 0.0
    generatedAt = ""

    def __init__(self, *args, **kwargs):
        self.app = kwargs.get("app")
        self.version = kwargs.get("version")
        self.generatedAt = kwargs.get("generatedAt", None)


class Wrapper:
    type = Type
    schemaLocation = ""
    schemaVersion = 0.0
    generator = Generator
    content = None

    def setContent(self, obj):
        self.content = obj
        #t = type(obj)

        #if Type.__contains__(t):
        #    self.type = Type(t)
        #else:
        #    raise Exception("Content type not allowed")

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4, ensure_ascii=True)
