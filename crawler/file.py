from crawler.file_types import FileType


class File:
    """
    Representation of a file within the Crawler.
    """

    def __init__(self, path: str, filetype: FileType, name: str = None):
        self.path = path
        self.name = name
        if name is None:
            self.name = path.split("/")[-1]
        self.associations = []
        self.type = filetype

    def add_associated_file(self, file):
        self.associations.append(file)
