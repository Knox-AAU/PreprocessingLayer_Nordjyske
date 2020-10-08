import codecs

from IO.knox_source_data_io.models.wrapper import *
from os import path
import importlib
import json


class IOHandler:
    """
    A class used to handle IO

    ...

    Attributes
    ----------
    schema : str
        path to schema used
    generator : Generator
        a object containing information about the generator.
    """

    schema: str
    generator: Generator

    def __init__(self, generator: Generator, schema: str):
        self.schema = schema
        self.generator = generator

    def write_json(self, obj: Model, outfile, file_name):
        """Reads an json file and converts into a object

        Parameters
        ----------
        outfile
        obj : object
            the object to export
        filepath : str
            the path to the json file to write.

        Raises
        ------
        ValueError
            If the obj is not a subclass of Model
        OSError
            If write the json file fails
        """

        if not issubclass(type(obj), Model):
            raise ValueError("Object need to be a subclass of Model...")

        # TODO: Validate path? Code below is for writing multiple files to directory
        # if not path.isdir(filepath):
        #    raise IsADirectoryError("Not a directory...")

        wrapper = Wrapper()
        wrapper.generator = self.generator
        wrapper.schema_location = self.schema
        wrapper.type = "article"
        wrapper.set_content(obj)
        data = wrapper.to_json()

        try:
            with codecs.open(file_name, 'w', encoding="utf-8") as outfile:
                outfile.write(data)
            return True
        except OSError:
            raise Exception("Error writing json...")

    @staticmethod
    def read_json(json_file):
        """Reads an json file and converts into a object

        It converts the input json to the corresponding objects based on the added __class__ and __module__ properties
        injected into the exported json.

        Parameters
        ----------
        json_file : file
            the path to the json file to read.

        Raises
        ------
        FileExistsError
            If no file is found at the path.
        """

        if not path.exists(json_file.name):
            raise FileExistsError("File does not exist...")

        try:
            data = json.load(json_file)
            # TODO validate json against schema.
            # response = requests.get("https://knox.libdom.net/schema/article.schema.json")
            # schema = response.json()

            the_obj = json.loads(json.dumps(data), object_hook=IOHandler.convert_dict_to_obj)
        except OSError:
            raise OSError("Failed to read file...")
        # TODO: Add more except for json loads

        return the_obj

    @staticmethod
    def convert_obj_to_dict(obj):
        """Convert an object to dict adding required json properties

        Source: https://medium.com/python-pandemonium/json-the-python-way-91aac95d4041

        A function takes in a custom object and returns a dictionary representation of the object.
        This dict representation includes meta data such as the object's module and class names.
        """

        #  Populate the dictionary with object meta data
        obj_dict = {
            "__class__": obj.__class__.__name__,
            "__module__": obj.__module__
        }

        #  Populate the dictionary with object properties
        obj_dict.update(obj.__dict__)

        return obj_dict

    @staticmethod
    def convert_dict_to_obj(our_dict):
        """Convert dict to json removing the added class properties

        Source: https://medium.com/python-pandemonium/json-the-python-way-91aac95d4041

        Function that takes in a dict and returns a custom object associated with the dict.
        This function makes use of the "__module__" and "__class__" metadata in the dictionary
        to know which object type to create.
        """
        if "__class__" in our_dict:
            # Pop ensures we remove metadata from the dict to leave only the instance arguments
            class_name = our_dict.pop("__class__")

            # Get the module name from the dict and import it
            module_name = our_dict.pop("__module__")

            # We use the built in __import__ function since the module name is not yet known at runtime
            module = importlib.import_module(module_name)

            # Get the class from the module
            class_ = getattr(module, class_name)

            # Use dictionary unpacking to initialize the object
            obj = class_(**our_dict)
        else:
            obj = our_dict
        return obj
