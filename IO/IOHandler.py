from models.wrapper import *
from os import path
import json
import importlib


class IOHandler:
    schema = ""
    generator = None

    def __init__(self, generator, schema):
        self.schema = schema
        if isinstance(generator, Generator):
            self.generator = generator

    def write_json(self, obj, filepath):
        # TODO: Validate path?
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
        if not path.exists(filepath):
            raise FileExistsError("File does not exist...")

        with open(filepath, 'r') as json_file:
            data = json.load(json_file)
            # TODO validate json against schema.

        obj = json.loads(json.dumps(data), object_hook=IOHandler.dict_to_obj)

        return obj



    # https://medium.com/python-pandemonium/json-the-python-way-91aac95d4041

    @staticmethod
    def convert_to_dict(obj):
        """

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
        """
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
