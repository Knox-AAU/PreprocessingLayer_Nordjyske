import codecs
import configparser
import multiprocessing
import os
import re
import json
import xml
from joblib import Parallel, delayed
from datetime import datetime, timezone
from os import path
from xml.dom import minidom
from knox_source_data_io.io_handler import IOHandler, Generator

from initial_ocr.teseract_module import TesseractModule
from nitf_parser.parser import NitfParser


class Crawler:
    config = configparser.ConfigParser()
    config.read('config.ini')

    def _init__(self):
        pass

    def run_crawler(self, arg_object):
        """ Runs the crawler for all specified file formats and call their respected modules
        :param arg_object: Object that stores the program arguments
        """

        folders = self.__manage_folder_cache(arg_object)
        folders = self.__check_and_filter_dates(arg_object, folders)

        # Loops through all the folders in the path and their respective files.
        for folder in folders:
            found_publications = []
            files = self.__find_relevant_files_in_directory(folder['path'])

            self.__process_files(files, found_publications, folder)

            # Export all found publications to JSON
            self.__save_to_json(arg_object.output_folder, found_publications)

    def __process_files(self, files, found_publications, folder):
        """
        Process multiples files in parallel to utilize all cores of system.
        :param files: The list of file paths to process
        :param found_publications: The array of which to add publications to.
        :param folder: The folder currently being processed
        """
        pubs = Parallel(
            n_jobs=multiprocessing.cpu_count(), prefer="threads")(
            delayed(self.__process_file)(file, folder)
            for file in files)
        for pub in pubs:
            self.__add_publication_if_new_or_add_articles_to_already_found_publication(
                found_publications,
                pub)

    @staticmethod
    def __process_file(file, folder):
        """
        This method is called to process an input file.
        :param file: The file path to be processed
        :param folder: The folder currently being searched in.
        :return: Publication matching the processed file.
        """
        print(f"Processing {file}...")

        if ".jp2" in file:
            tesseract_module = TesseractModule()
            pub = tesseract_module.run_tesseract_on_image(file)
            pub.published_at = datetime(tzinfo=timezone.utc, year=folder['year'],
                                        month=folder['month'],
                                        day=folder['day']).isoformat()
            return pub

        # Checks if it is a .xml file. if true, the parser for .nitf parser is called
        if ".xml" in file:
            return NitfParser().parse(file)

        return None

    def __manage_folder_cache(self, arg_object):
        """ If clear cache arg is given, the cache is cleared. If not the folders are loaded
        :param arg_object:
        :return: Returns the found folders
        """
        if arg_object.clearcache or not path.exists(self.config['structure']['cache_file']):
            print(
                "Could not find cache, or clear cache flag was enabled..")
            # Recalculate folders.json
            folders = self.__find_folders_recursively(arg_object.path)

            if len(folders) == 0:
                raise Exception("No files found in the input folder")

            # Sorts the folders after year,month, date
            folders.sort(key=lambda folder: self.__date_to_int(folder))
            self.__save_cache_file(folders, self.config['structure']['cache_file'])
        else:
            # Load folders from folders.json
            folders = self.__load_from_json(self.config['structure']['cache_file'])

        return folders

    def __check_and_filter_dates(self, arg_object, folders):
        """ Set arg_object to and from dates and verifies them. Filter the folders by date

        :param arg_object: Object that represents the program arguments
        :param folders: The folders to sort
        :return: Sorted folders
        """
        # If a to-date is present, we set to-date to last element
        if not hasattr(arg_object, "to_date"):
            # from = folders
            arg_object.to_date = folders[-1]

        # If a from-date is present, we set from-date to first element
        if not hasattr(arg_object, "from_date"):
            # From = folders[0]
            arg_object.from_date = folders[0]

        # Checks if the to date is after the from date
        int_from_date = self.__date_to_int(arg_object.from_date)
        int_to_date = self.__date_to_int(arg_object.to_date)
        if int_from_date > int_to_date:
            raise Exception("The to-date is before the from-date.")

        # Filter folders by dates
        to_date = self.__date_to_int(arg_object.to_date)
        from_date = self.__date_to_int(arg_object.from_date)
        folders = [folder for folder in folders if
                   from_date <= self.__date_to_int(folder) <= to_date]

        return folders

    def __find_folders_recursively(self, directory):
        """ Recursive function that finds all the dire that contains the wanted files

        :param directory:
        :return: Folder that has been found
        """
        print("Searching in " + directory)

        # Finds all sub directories in the directory
        dirs = next(os.walk(directory))[1]

        found_folders = []

        # Gets regex from config file that matches the target dirs name
        pattern_strings = self.config['structure']['final-folder-regex'].split(",")
        pattern_strings = [x.split("|") for x in pattern_strings]

        regexs = [
            {
                'compiled': re.compile(pattern_string[0]),
                'original': pattern_string[0],
                'limits': [int(y) for y in pattern_string[1:7]]
                # 6 because there are three sets of base and bounds
            }

            for pattern_string in pattern_strings]

        for curr_dir in dirs:
            # Let's check if the current dir is a target dir by matching to regexs
            filtered_regexs = filter(lambda regex: re.match(regex['compiled'], curr_dir), regexs)
            matched_regex = next(filtered_regexs, None)
            if matched_regex is not None:
                # Current dir IS a target dir, append to list to return later.
                limits = matched_regex['limits']
                found_folders.append(
                    {
                        'path': directory + "/" + curr_dir,
                        'year': int(curr_dir[limits[0]:limits[1]]),
                        'month': int(curr_dir[limits[2]:limits[3]]),
                        'day': int(curr_dir[limits[4]:limits[5]])
                    }
                )
            else:
                # Current dir is NOT a target dir. Let's search that dir for target-dirs.
                found_folders.extend(self.__find_folders_recursively(directory + "/" + curr_dir))

        return found_folders

    def __find_relevant_files_in_directory(self, directory):
        """ Finds all files in a directory and checks them again the file type
        white and blacklist.

        :param directory: Path to directory
        :return: All found files that isn't in the blacklist/whitelist
        """

        files = self.__find_all_files_recursively(directory)
        blacklist = self.config['structure']['blacklist'].split(",")
        whitelist = self.config['structure']['whitelist'].split(",")

        # Checks whether the file should be appended, by using config white- and blacklist
        found_files = []
        for file in files:
            if self.__is_string_in_list(file, blacklist) or not self.__is_string_in_list(file,
                                                                                         whitelist):
                continue

            if ".xml" in file:
                if self.__is_file_valid_nitf(directory + "/" + file):
                    found_files.append(directory + "/" + file)

            else:
                found_files.append(directory + "/" + file)

        return found_files

    def __find_all_files_recursively(self, directory):
        """ Recursively finds all files in a directory

        :param directory: Path to directory
        :return: List of found files
        """
        print(f"Searching directory {directory} for files..")
        walk = next(os.walk(directory))
        files = walk[2]  # Gets files from specified directory
        for walking_dir in walk[1]:  # Goes through all directories from the found directories

            # Calls method recursively to get sub directories
            found_files = self.__find_all_files_recursively(directory + "/" + walking_dir)

            for file in found_files:
                files.append(walking_dir + "/" + file)
        return files

    @staticmethod
    def __date_to_int(date):
        """ Converts a dictionary with attributes year, month and date to an int.
        Useful for comparing dates/sorting.

        :param date: Object that has year, month, and date properties
        :return: An int that represents the objects date
        """
        return int(str(date['year']) + str(date['month']).zfill(2) + str(date['day']).zfill(2))

    @staticmethod
    def __add_publication_if_new_or_add_articles_to_already_found_publication(found_publications,
                                                                              input_pub):
        """ Adds input_pub to found_publications if it is not already present,
        else adds the articles of input_pub to the matching publication in found_publications

        :param found_publications: A list of publications that have already been found
        (will be altered to reflect the effect of the method)
        :param input_pub: The publication containing articles to be added
        :return:
        """
        # Ensures that articles with no paragraphs are not added to the publications
        if len(input_pub.articles[0].paragraphs) == 0:
            return

        # Get reference to the publication that has already been added to the found publications
        # (returns 'None' if no match is found)
        matching_publication_in_publications_found = next(
            (pub for pub in found_publications if pub.publication in found_publications), None)

        # Check if the publication is not part of the found publications
        # If it is, add it as a new publication
        # Else, add its article to the already added publication
        if matching_publication_in_publications_found is None:
            found_publications.append(input_pub)
        else:
            matching_publication_in_publications_found.add_article(input_pub.articles[0])

    @staticmethod
    def __save_to_json(folder, publications):
        """ Saves the publications as JSON files in the given folder

        :param folder: The destination folder
        :param publications: A list of publications that should be saved
        :return:
        """
        for pub in publications:
            handler = IOHandler(
                Generator(app="This app", version=1.0, generated_at=datetime.now().isoformat()),
                "http://iptc.org/std/NITF/2006-10-18/")
            filename = os.path.join(
                folder,
                f'{datetime.strptime(pub.published_at, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d")}'
                f'_{Crawler.__sanitize(pub.publication)}.json')

            with open(filename, 'w', encoding="utf-8") as outfile:
                handler.write_json(pub, outfile)

    @staticmethod
    def __sanitize(string):
        """ Handles all the sanitation of the string

        :param string:
        :return: Sanitized string
        """
        without_special_chars = ''.join([a for a in string.lower() if a.isalnum()])
        without_danish_letters = ''.join(
            [Crawler.__map_from_danish(a) for a in without_special_chars])
        return without_danish_letters

    @staticmethod
    def __map_from_danish(char):
        """ Maps 'æ' to 'ae', 'ø' to 'oe', and 'å' to 'aa'

        :param char:
        :return: The converted char as a string or the given char if not 'æ', 'ø', or 'å'
        """
        if char == 'æ':
            return "ae"
        if char == "ø":
            return "oe"
        if char == "å":
            return "aa"
        return char

    @staticmethod
    def __load_from_json(filename):
        """ Loads a json file and returns its data

        :param filename: JSON file to be loaded
        :return: Data from json file
        """
        with open(filename) as json_file:
            data = json.load(json_file)

        return data

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

    @staticmethod
    def __save_cache_file(folders, file_name):
        """ Dumps all files from a folder
        :param folders: Folders with files to dump
        :param file_name: Output filename
        """
        with codecs.open(file_name, 'w', encoding="utf-8") as outfile:
            json.dump(folders, outfile, indent=4, ensure_ascii=False)  # 4 is standard indent
