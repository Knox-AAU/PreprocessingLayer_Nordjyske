class Folder:
    def __init__(self, path, year, month, day):
        self.path = path
        self.year = year
        self.month = month
        self.day = day
        self.files = []

    def add_file(self, file):
        self.files.append(file)
