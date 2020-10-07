import json
import IOHandler


class Generator:
    """
    A class used to represent the application used to generate the wrapper

    ...

    Attributes
    ----------
    app : str
        the name of the application generating the json output
    version : float
        the application version
    generatedAt : str
        the date and time of generation
    """

    app: str
    version: float
    generated_at: str

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
        self.app = values.get("app")
        self.version = values.get("version")
        self.generated_at = values.get("generated_at", "")


class Wrapper:
    """
    A class used to represent a Wrapper

    ...

    Attributes
    ----------
    type : str
        the type of object wrapped
    schemaLocation : str
        the schema that the exported file comply with.
    schemaVersion : float
        the schema version
    generator : Generator
        the generator information object
    content :
        the object being exported
    """

    type: str
    schema_location: str
    schema_version: float
    generator: Generator
    content: object

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
        self.type = values.get("type", "")
        self.schema_location = values.get("schema_location", "")
        self.schema_version = values.get("schema_version", 0.0)
        self.generator = values.get("generator", Generator())
        self.content = values.get("content", None)

    def set_content(self, obj):
        """Set the object being exported

           sets the object being exported, this should be a valid object... Therefore the todo...
        """

        # TODO: Validate type (Maybe interface?)
        self.content = obj

    def to_json(self):
        """Converts the object to json string

        Properties are indented using 4 spaces.
        """

        return json.dumps(self, default=IOHandler.IOHandler.convert_to_dict,
                          sort_keys=False, indent=4)
