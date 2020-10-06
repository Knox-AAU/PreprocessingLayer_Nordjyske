from models.wrapper import *
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

    schema = ""
    generator = None

    def __init__(self, generator, schema):
        self.schema = schema
        if isinstance(generator, Generator):
            self.generator = generator

    def write_json(self, obj, filepath):
        """Reads an json file and converts into a object

        Parameters
        ----------
        obj : object
            the object to export
        filepath : str
            the path to the json file to write.

        Raises
        ------
        OSError
            If write the json file fails
        """

        # TODO: Validate path? Code below is for writing multiple files to directory
        # if not path.isdir(filepath):
        #    raise IsADirectoryError("Not a directory...")

        wrapper = Wrapper()
        wrapper.generator = self.generator
        wrapper.schemaLocation = self.schema
        wrapper.type = "article"
        wrapper.set_content(obj)
        data = wrapper.to_json()

        try:
            with open(filepath, 'w') as outfile:
                outfile.write(data)
            return True
        except OSError:
            raise Exception("Error writing json...")

    @staticmethod
    def read_json(filepath):
        """Reads an json file and converts into a object

        It converts the input json to the corresponding objects based on the added __class__ and __module__ properties
        injected into the exported json.

        Parameters
        ----------
        filepath : str
            the path to the json file to read.

        Raises
        ------
        FileExistsError
            If no file is found at the path.
        """

        if not path.exists(filepath):
            raise FileExistsError("File does not exist...")

        try:
            with open(filepath, 'r') as json_file:
                data = json.load(json_file)
                # TODO validate json against schema.

            the_obj = json.loads(json.dumps(data), object_hook=IOHandler.dict_to_obj)
        except OSError:
            raise OSError("Failed to read file...")
        # TODO: Add more except for json loads

        return the_obj

    @staticmethod
    def convert_to_dict(obj):
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
    def dict_to_obj(our_dict):
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
