import codecs
import configparser
import os
import re
import json
from datetime import datetime
from os import path
from xml.dom import minidom

from knox_source_data_io.io_handler import IOHandler, Generator
from initial_ocr.teseract_module import TesseractModule
from nitf_parser.parser import NitfParser


class Crawler:
    config = configparser.ConfigParser()
    config.read('config.ini')
    nitf_parser = NitfParser()
    tesseract_module = TesseractModule()

    def _init__(self):
        pass

    def run_crawler(self, arg_object):
        """ Runs the crawler for all specified file formats and call their respected modules
        :param arg_object: object that stores the program arguments
        """

        folders = self.__manage_folder_cache(arg_object)
        folders = self.__check_and_filter_dates(arg_object, folders)



        # loops through all the folders in the path and their respective files.
        for folder in folders:
            publications_found = []
            files = self.__find_relevant_files_in_directory(folder['path'])
            for file in files:
                # checks if it is a .jp2 file. if true, the ocr is called
                # if ".jp2" in file:
                #     publication.add_article(self.tesseract_module.run_tesseract_on_image(file))
                # # checks if it is a .xml file. if true, the parser for .nitf parser is called
                if ".xml" in file:
                    print(f"Parsing {file}...")
                    publication_in_nitf = self.nitf_parser.parse(file)
                    extracted_matches = [publication for publication in
                                         publications_found if
                                         publication.publication == publication_in_nitf.publication]
                    if len(extracted_matches) == 0:
                        publications_found.append(publication_in_nitf)
                    else:
                        extracted_matches[0].add_article(publication_in_nitf.articles[0])
            self.__save_to_json(arg_object.output_folder, publications_found)

    def __manage_folder_cache(self, arg_object):
        """ If clear cache arg is given, the cache is cleared. If not the folders are loaded
        :param arg_object:
        :return: returns the found folders
        """
        if arg_object.clearcache or not path.exists(self.config['structure']['cache_file']):
            print("Could not find cache, or clear cache flag was enabled.. Searching file structure..")
            # recalculate folders.json
            folders = self.__find_folders_recursively(arg_object.path)

            if len(folders) == 0:
                raise Exception("No files found in the input folder")

            # sorts the folders after year,month, date
            folders.sort(key=lambda folder: self.__date_to_int(folder))
            self.__save_cache_file(folders, self.config['structure']['cache_file'])
        else:
            # load folders from folders.json
            folders = self.__load_from_json(self.config['structure']['cache_file'])

        return folders

    def __check_and_filter_dates(self, arg_object, folders):
        """ Set arg_object to and from dates and verifies them. Filter the folders by date

        :param arg_object: object that represents the program arguments
        :param folders: the folders to sort
        :return: sorted folders
        """
        # if a to-date is present, we set to-date to last element
        if not hasattr(arg_object, "to_date"):
            # from = folders
            arg_object.to_date = folders[-1]

        # if a from-date is present, we set from-date to first element
        if not hasattr(arg_object, "from_date"):
            # from = folders[0]
            arg_object.from_date = folders[0]

        # checks if the to date is after the from date
        int_from_date = self.__date_to_int(arg_object.from_date)
        int_to_date = self.__date_to_int(arg_object.to_date)
        if int_from_date > int_to_date:
            raise Exception("The to-date is before the from-date.")

        # filter folders by dates
        to_date = self.__date_to_int(arg_object.to_date)
        from_date = self.__date_to_int(arg_object.from_date)
        folders = [folder for folder in folders if from_date <= self.__date_to_int(folder) <= to_date]

        return folders

    @staticmethod
    def __date_to_int(a):
        """ converts a dictionary with attributes year, month and date to an int, useful for comparing dates/sorting.

        :param a: object that has year, month, and date properties
        :return: an int that represents the objects date
        """
        return int(str(a['year']) + str(a['month']).zfill(2) + str(a['date']).zfill(2))

    def __find_folders_recursively(self, directory):
        """ recursive function that finds all the dire that contains the wanted files

        :param directory:
        :return: folder that has been found
        """
        print("Searching in " + directory)

        #  finds all sub directories in the directory
        dirs = next(os.walk(directory))[1]

        found_folders = []

        # gets regex from config file that matches the target dirs name
        pattern_strings = self.config['structure']['final-folder-regex'].split(",")
        pattern_strings = [x.split("|") for x in pattern_strings]

        regexs = [
            {
                'compiled': re.compile(pattern_string[0]),
                'original': pattern_string[0],
                'limits': [int(y) for y in pattern_string[1:7]]  # 6 because there are three sets of base and bounds
            }

            for pattern_string in pattern_strings]

        for curr_dir in dirs:
            # let's check if the current dir is a target dir by matching to regexs
            filtered_regexs = filter(lambda regex: re.match(regex['compiled'], curr_dir), regexs)
            matched_regex = next(filtered_regexs, None)
            if matched_regex is not None:
                # current dir IS a target dir, append to list to return later.
                limits = matched_regex['limits']
                found_folders.append(
                    {
                        'path': directory + "/" + curr_dir,
                        'year': int(curr_dir[limits[0]:limits[1]]),
                        'month': int(curr_dir[limits[2]:limits[3]]),
                        'date': int(curr_dir[limits[4]:limits[5]])
                    }
                )
            else:
                # current dir is NOT a target dir. Let's search that dir for target-dirs.
                found_folders.extend(self.__find_folders_recursively(directory + "/" + curr_dir))
        return found_folders

    @staticmethod
    def __save_to_json(folder, publications):
        for index,publication in publications:
            handler = IOHandler(Generator(app="This app", version=1.0, generated_at=datetime.now().isoformat()),
                                "http://iptc.org/std/NITF/2006-10-18/")
            filename = os.path.join(folder, f'{publication.published_at}_{publication.publication}.json')

            with open(filename, 'w') as outfile:
                handler.write_json(publication, outfile)

    @staticmethod
    def __load_from_json(filename):
        """Loads a json file and returns its data

        :param filename: json file to be loaded
        :return: data from json file
        """
        with open(filename) as json_file:
            data = json.load(json_file)
        return data

    def __find_relevant_files_in_directory(self, directory):
        """Finds all files in a directory and checks them again the file type
        white and blacklist.

        :param directory: path to directory
        :return: all found files that isn't in the blacklist/whitelist
        """

        files = self.__find_all_files_recursively(directory)
        blacklist = self.config['structure']['blacklist'].split(",")
        whitelist = self.config['structure']['whitelist'].split(",")
        # checks whether the file should be appended, by using config white- and blacklist
        found_files = []
        for file in files:
            if self.__is_string_in_list(file, blacklist) or not self.__is_string_in_list(file, whitelist):
                continue
            if ".xml" in file:
                if self.__is_file_valid_nitf(directory + "/" + file):
                    found_files.append(directory + "/" + file)
            else:
                found_files.append(directory + "/" + file)
            # Add new file-formats here!
        return found_files

    def __find_all_files_recursively(self, directory):
        """Recursively finds all files in a directory

        :param directory: path to directory
        :return: list of found files
        """
        print(f"Searching directory {directory} for files..")
        walk = next(os.walk(directory))
        files = walk[2]  # gets files from specified directory
        for walking_dir in walk[1]:  # goes through all directories from the found directories
            # calls method recursively to get sub directories
            found_files = self.__find_all_files_recursively(directory + "/" + walking_dir)
            for file in found_files:
                files.append(walking_dir + "/" + file)
        return files

    @staticmethod
    def __is_file_valid_nitf(xml_path):
        """Checks if the XML file given has the nitf:nitf tag

        :param xml_path: path to the XML file
        :return: true or false, depending on whether it's a nitf file or not
        """
        xml_doc = minidom.parse(xml_path)
        if len(xml_doc.getElementsByTagName('nitf:nitf')) != 0:
            # todo file is nitf, lets check if it is a valid article.
            return True
        return False

    @staticmethod
    def __is_string_in_list(string, checklist):
        """Checks if the string contains any words in the list (useful for black- and whitelisting)

        :param string: string to be checked
        :param checklist: white- or blacklist from config file
        :return: true or false, depending on whether the string appears in the list
        """
        for listed_item in checklist:
            if listed_item in string:
                return True
        return False

    @staticmethod
    def __save_cache_file(folders, file_name):
        """ Dumps all files from a folder
        :param folders: folders with files to dump
        :param file_name: output filename
        """
        with codecs.open(file_name, 'w', encoding="utf-8") as outfile:
            json.dump(folders, outfile, indent=4, ensure_ascii=False)  # 4 is standard indent
