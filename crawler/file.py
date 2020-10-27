from crawler.file_types import FileType


class File:
    def __init__(self, path: str, name: str, filetype: FileType):
        self.path = path
        self.name = name
        self.associations = []
        self.type = filetype

    def add_associated_file(self, file):
        self.associations.append(file)
