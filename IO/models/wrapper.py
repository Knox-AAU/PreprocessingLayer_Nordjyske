import json
import IOHandler


class Generator:
    app = ""
    version = 0.0
    generatedAt = ""

    def __init__(self, values: dict = None, **kwargs):
        values = values if values is not None else kwargs
        self.app = values.get("app")
        self.version = values.get("version")
        self.generatedAt = values.get("generatedAt", None)


class Wrapper:
    type: str = ""
    schemaLocation: str = ""
    schemaVersion: float = 0.0
    generator: Generator = Generator
    content = None

    def __init__(self, values: dict = None, **kwargs):
        values = values if values is not None else kwargs
        self.type = values.get("type", "")
        self.schemaLocation = values.get("schemaLocation", "")
        self.schemaVersion = values.get("schemaVersion", 0.0)
        self.generator = values.get("generator", Generator)
        self.content = values.get("content", None)

    def set_content(self, obj):
        # TODO: Validate type (Maybe interface?)
        self.content = obj

    def to_json(self):
        return json.dumps(self, default=IOHandler.IOHandler.convert_to_dict,
                          sort_keys=False, indent=4)
