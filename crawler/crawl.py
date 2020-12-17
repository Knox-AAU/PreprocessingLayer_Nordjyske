import configparser
import os
import re
import xml
from datetime import datetime
from queue import Queue
from xml.dom import minidom
from crawler.file import File
from crawler.file_types import FileType
from crawler.folder import Folder


class Crawler:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        pattern_strings = config['structure']['final-folder-regex'].split(",")
        pattern_strings = [x.split("|") for x in pattern_strings]
        self.regexs = [
            {
                'compiled': re.compile(pattern_string[0]),
                'original': pattern_string[0],
                'limits': [int(y) for y in pattern_string[1:7]]
                # 6 because there are three sets of base and bounds
            }

            for pattern_string in pattern_strings]
        self.blacklist = config['structure']['blacklist'].split(",")
        self.whitelist = config['structure']['whitelist'].split(",")

    def crawl_folders(self, q: Queue, directory: str, from_date: datetime, to_date: datetime):
        """
        Crawl a directory recursively to find target directories, configured by the config file.
        Will only find files in a defined interval of dates.
        @param q: The queue to add directories to
        @param directory: The current folder path to search in
        @param from_date: The interval from_date
        @param to_date: The interval to_date
        """
        for entry in os.scandir(directory):
            if not entry.is_dir():
                continue
            # Let's check if the current dir is a target dir by matching to regexs
            matched_regex = next(
                filter(lambda regex: re.match(regex['compiled'], entry.name), self.regexs), None)
            if matched_regex is not None:
                # Current dir IS a target dir, append to list to return later.

                limits = matched_regex['limits']
                folder = Folder(entry.path,
                                int(entry.name[limits[0]:limits[1]]),
                                int(entry.name[limits[2]:limits[3]]),
                                int(entry.name[limits[4]:limits[5]]))

                if not (
                        (from_date if from_date is not None else datetime.min) <=
                        folder.get_datetime() <=
                        (to_date if to_date is not None else datetime.max)
                ):
                    # only consume if within date
                    continue
                self.crawl_for_files_in_folders(folder, entry.path)
                print(f"Produced {entry.path}")
                q.put(folder)

            else:
                # Current dir is NOT a target dir. Let's search that dir for target-dirs.
                self.crawl_folders(q, entry.path, from_date, to_date)

    def crawl_for_files_in_folders(self, folder, directory: str):
        """
        Finds valid files in a folder and adds it to a folder type.
        @param folder: The folder to add the found files to.
        @param directory: The path to search
        """
        for entry in os.scandir(directory):
            if not entry.is_dir():
                # entry is file
                if self.is_string_in_list(entry.name, self.blacklist) or not \
                        self.is_string_in_list(entry.name, self.whitelist):
                    continue

                if ".xml" in entry.name and self.is_file_valid_nitf(entry.path):
                    folder.add_file(File(entry.path, FileType.NITF, name=entry.name))
                if ".jp2" in entry.name:
                    folder.add_file(File(entry.path, FileType.JP2, name=entry.name))

            else:
                # entry is folder, search recursively:
                self.crawl_for_files_in_folders(folder, entry.path)

        folder.sort()

    @staticmethod
    def is_file_valid_nitf(xml_path) -> bool:
        """
        Determines if a given file_path is a valid NITF file.
        @param xml_path:
        @return: bool
        """
        try:
            xml_doc = minidom.parse(xml_path)

            if len(xml_doc.getElementsByTagName('nitf:nitf')) != 0:
                return True

        except xml.parsers.expat.ExpatError:
            return False

        return False

    @staticmethod
    def is_string_in_list(string, checklist):
        """ Checks if the string contains any words in the list (useful for black- and whitelisting)

        :param string: String to be checked
        :param checklist: White- or blacklist from config file
        :return: True or False, depending on whether the string appears in the list
        """
        for listed_item in checklist:
            if listed_item in string:
                return True

        return False
