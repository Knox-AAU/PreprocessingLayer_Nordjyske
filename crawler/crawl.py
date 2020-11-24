import configparser
import os
import re
import xml
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

    def crawl_folders(self, q: Queue, directory, from_date, to_date):
        for entry in os.scandir(directory):
            if not entry.is_dir():
                continue
            # Let's check if the current dir is a target dir by matching to regexs
            matched_regex = next(filter(lambda regex: re.match(regex['compiled'], entry.name), self.regexs), None)
            if matched_regex is not None:
                # Current dir IS a target dir, append to list to return later.

                limits = matched_regex['limits']
                folder = Folder(entry.path,
                                int(entry.name[limits[0]:limits[1]]),
                                int(entry.name[limits[2]:limits[3]]),
                                int(entry.name[limits[4]:limits[5]]))
                if not (from_date <= folder.get_datetime() <= to_date):
                    # only consume if within date
                    continue
                self.__crawl_for_files_in_folders(folder, entry.path)
                print(f"Produced {entry.path}")
                q.put(folder)

            else:
                # Current dir is NOT a target dir. Let's search that dir for target-dirs.
                self.crawl_folders(q, entry.path, from_date, to_date)

    def __crawl_for_files_in_folders(self, folder, directory: str):
        for entry in os.scandir(directory):
            if not entry.is_dir():
                # entry is file
                if self.__is_string_in_list(entry.name, self.blacklist) or not \
                        self.__is_string_in_list(entry.name, self.whitelist):
                    continue

                if ".xml" in entry.name and self.__is_file_valid_nitf(entry.path):
                    folder.add_file(File(entry.path, FileType.NITF, name=entry.name))
                if ".jp2" in entry.name:
                    folder.add_file(File(entry.path, FileType.JP2, name=entry.name))

            else:
                # entry is folder, search recursively:
                self.__crawl_for_files_in_folders(folder, entry.path)

        folder.sort()

    @staticmethod
    def __is_file_valid_nitf(xml_path):
        """ Checks if the XML file given has the nitf:nitf tag

        :param xml_path: Path to the XML file
        :return: True or False, depending on whether it is a nitf file or not
        """
        try:
            xml_doc = minidom.parse(xml_path)

            if len(xml_doc.getElementsByTagName('nitf:nitf')) != 0:
                return True

        except xml.parsers.expat.ExpatError:
            return False

        return False

    @staticmethod
    def __is_string_in_list(string, checklist):
        """ Checks if the string contains any words in the list (useful for black- and whitelisting)

        :param string: String to be checked
        :param checklist: White- or blacklist from config file
        :return: True or False, depending on whether the string appears in the list
        """
        for listed_item in checklist:
            if listed_item in string:
                return True

        return False
