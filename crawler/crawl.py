import configparser
import os
import re
import json
from os import path
from pprint import pprint
from xml.dom import minidom
from nitf_parser.main import parse

config = configparser.ConfigParser()
config.read('config.ini')


def run_crawler(arg_object):
    """ Runs the crawler for all specified file formats and call their respected modules
    :param arg_object: object that stores the program arguments
    """
    if arg_object.clearcache or not path.exists(config['structure']['cache_file']):
        # recalculate folders.json
        folders = find_folders_recursively(arg_object.path)
        # Sorts the folders after year,month, date
        folders.sort(key=lambda folder: int(str(folder.year) + str(folder.month).zfill(2) + str(folder.date).zfill(2)))
        output(folders, config['structure']['cache_file'])
    else:
        # load folders from folders.json
        folders = load(config['structure']['cache_file'])

    # if a toDate is present, we set toDate to last element
    if not hasattr(arg_object, "toDate"):
        # from = folders
        arg_object.toDate = folders[-1]

    # if a fromDate is present, we set toDate to first element
    if not hasattr(arg_object, "fromDate"):
        # from = folders[0]
        arg_object.fromDate = folders[0]

    # checks if the to date is after the from date
    pprint(arg_object)
    int_from_date = date_to_int(arg_object.fromDate)
    int_to_date = date_to_int(arg_object.toDate)
    if int_from_date > int_to_date:
        raise Exception("The to-date is before the from-date.")

    # Filter folders by dates
    toDate = date_to_int(arg_object.toDate)
    fromDate = date_to_int(arg_object.fromDate)
    folders = [folder for folder in folders if fromDate < date_to_int(folder) < toDate]

    # Loops through all the folders in the path and their respective files.
    for folder in folders:
        files = find_relevant_files_in_directory(folder['path'])
        output_this_folder = []
        for file in files:
            # checks if it is a .jp2 file. if true, the ocr is called
            if ".jp2" in file:
                # todo call module for tesseract
                print("Tesseract not implemented yet.")
            # checks if it is a .xml file. if true, the parser for .nitf parser is called
            if ".xml" in file:
                output_this_folder.append(parse(f"{file}"))
        output(output_this_folder, f"output.json")


def date_to_int(a):
    """ Simply converts string to int
    :param a: object that has year, month, and date properties
    :return:
    """
    return int(str(a['year']) + str(a['month']).zfill(2) + str(a['date']).zfill(2))


def find_folders_recursively(directory):
    """

    :param directory:
    :return:
    """
    print("Searching in "+directory)
    dirs = next(os.walk(directory))[1]

    found_folders = []

    pattern_strings = config['structure']['final-folder-regex'].split(",")
    regexs = []
    for pattern_string in pattern_strings:
        print(pattern_string)
        regexs.append(re.compile(pattern_string))
    for cdir in dirs:
        for regex in regexs:
            if re.match(regex, cdir):
                # Add to list to return
                found_folders.append(
                    {
                        'path': directory + "/" + cdir,
                        'year': int(cdir[0:4]),
                        'month': int(cdir[5:7]),
                        'date': int(cdir[8:10])
                    }
                )
            else:
                # extend recursively
                found_folders.extend(find_folders_recursively(directory+"/"+cdir))
    return found_folders


def output(folders, file_name):
    """ Dumps all files from a folder
    :param folders:
    :param file_name:
    """
    with open(file_name, 'w') as f:
        json.dump(folders, f, indent=4)


def load(directory):
    """Loads a json file and returns its data

    :param directory: json file to be loaded
    :return: data from json file
    """
    with open(directory) as json_file:
        data = json.load(json_file)
    return data


def find_relevant_files_in_directory(directory):
    """Finds all files in a directory and checks them again the file type
    white and blacklist.

    :param directory: path to directory
    :return: all found files that isn't in the blacklist/whitelist
    """
    found_files = []
    #Fetch
    files = find_all_files_recursively(directory)
    pprint(files)
    blacklist = config['structure']['blacklist'].split(",")
    whitelist = config['structure']['whitelist'].split(",")
    # checks whether the file should be appended, by using config white- and blacklist
    for file in files:
        if is_file_in_list(file, blacklist):
            continue
        if not is_file_in_list(file, whitelist):
            continue
        if ".xml" in file:
            if is_file_valid_nitf(directory+"/"+file):
                found_files.append(directory + "/" + file)
        else:
            found_files.append(directory + "/" + file)

        # Add new file-formats here!

    return found_files


def find_all_files_recursively(directory):
    """Recursivly finds all files in a directory

    :param directory:
    :return:
    """
    print(f"Searching directory {directory} for files..")
    walk = next(os.walk(directory))
    files = walk[2]
    for walking_dir in walk[1]:
        found_files = find_all_files_recursively(directory + "/" + walking_dir)
        for file in found_files:
            files.append(walking_dir+"/"+file)
    return files


def is_file_valid_nitf(xml_path):
    """Checks if the XML file given has the nitf:nitf tag

    :param xml_path: path to the XML file
    :return: true or false, depending if its a nitf file or not
    """
    xml_doc = minidom.parse(xml_path)
    if len(xml_doc.getElementsByTagName('nitf:nitf')) != 0:
        # file is nitf, lets check if it is a valid article. todo
        return True
    return False


def is_file_in_list(file, checklist):
    """Checks if the file type is in the checklist (black- or whitelist)

    :param file: file to be checked
    :param checklist: white- or blacklist from config file
    :return:
    """
    for listed_item in checklist:
        if listed_item in file:
            return True
    return False

