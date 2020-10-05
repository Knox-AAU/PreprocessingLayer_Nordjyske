from os import path
import json
from types import SimpleNamespace
from models.wrapper import *


class IOHandler:
    schema = ""
    generator = None

    def __init__(self, generator, schema):
        self.schema = schema

        if isinstance(generator, Generator):
            self.generator = generator

    #@staticmethod
    def Import(self, the_type, filepath):
        if not path.exists(filepath):
            raise FileExistsError("File does not exist...")

        with open(filepath, 'r') as json_file:
            data = json.load(json_file)
            # TODO validate json against schema.

        try:
            obj_dict = json.loads(data)
            the_object = the_type(**obj_dict)
        except:
            raise Exception("Could not deserialize json...")

        return the_object

    def Export(self, obj, filepath):

        #if not path.isdir(filepath):
        #    raise IsADirectoryError("Not a directory...")

        wrapper = Wrapper()
        wrapper.generator = self.generator
        wrapper.schemaLocation = self.schema
        wrapper.type = Type.ARTICLE.value
        wrapper.setContent(obj)
        data = wrapper.toJSON()

        try:
            with open(filepath, 'w') as outfile:
                outfile.write(data)
            return True
        except OSError:
            raise Exception("Error writing json...")
