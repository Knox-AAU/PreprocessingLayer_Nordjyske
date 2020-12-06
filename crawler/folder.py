from datetime import datetime, timezone


class Folder:
    def __init__(self, path, year, month, day):
        self.path = path
        self.year = year
        self.month = month
        self.day = day
        self.files = []

    def add_file(self, file):
        file.folder = self
        self.files.append(file)

    def get_datetime(self):
        return datetime(year=self.year, month=self.month, day=self.day, tzinfo=timezone.utc)

    def sort(self):
        self.files.sort(key=lambda x: x.name)
