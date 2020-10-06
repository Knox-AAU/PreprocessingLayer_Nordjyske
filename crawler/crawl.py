#from pgmagick import Image

#img = Image('CB_TM432.jp2') # Input Image
#img.write('CB_TM432.jpeg')  # Output Image
import configparser
import os
import re
import datetime
import json
import shutil
from os import path
from pprint import pprint
from xml.dom import minidom
from nitf_parser.main import parse

config = configparser.ConfigParser()
config.read('config.ini')


def run_crawler(arg_object):
    if arg_object.clearcache or not path.exists(config['structure']['cache_file']):
        # recalculate folders.json
        folders = find_folders_recursively(arg_object.path)
        #Sorts the folders after year,month, date
        folders.sort(key=lambda folder: int(str(folder.year) + str(folder.month).zfill(2) + str(folder.date).zfill(2)))
        output(folders, config['structure']['cache_file'])
    else:
        # load folders from folders.json
        folders = load(config['structure']['cache_file'])

    # now we know the folders
    if not hasattr(arg_object, "toDate"):
        # from = folders
        arg_object.toDate = folders[-1]

    if not hasattr(arg_object, "fromDate"):
        # from = folders[0]
        arg_object.fromDate = folders[0]

    #if arg_object.fromDate > arg_object.toDate:
        #todo giv besked om at input er fucked

    print(arg_object)

    # Filter folders by dates
    toDate = string_to_int(arg_object.toDate)
    fromDate = string_to_int(arg_object.fromDate)
    folders = [folder for folder in folders if fromDate < string_to_int(folder) < toDate]

    output(folders, "test.json")

    folders = [arg_object.path] #todo for testing, remove this
    for folder in folders:
        files = find_relevant_files_in_directory(folder)

        output_this_folder = []
        for file in files:
            if ".jp2" in file:
                #todo call module tesseract shit
                print("Tesseract not implemented yet.")
                #output_this_folder.append({"implement": "none"})
            if ".xml" in file:
                output_this_folder.append(parse(f"{file}"))
        output(output_this_folder, f"hej.json")


def string_to_int(a):
    return int(str(a['year']) + str(a['month']).zfill(2) + str(a['date']).zfill(2))


def find_folders_recursively(directory):
    print("Searching in "+directory)
    dirs = next(os.walk(directory))[1]

    found_folders = []

    pattern = re.compile(config['structure']['final-folder-regex'])
    for cdir in dirs:
        if re.match(pattern, cdir):
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
    with open(file_name, 'w') as f:
        json.dump(folders, f, indent=4)


def load(directory):
    with open(directory) as json_file:
        data = json.load(json_file)
    return data


def find_relevant_files_in_directory(directory):
    found_files = []
    files = find_all_files_recursively(directory)
    pprint(files)
    blacklist = config['structure']['blacklist'].split(",")
    whitelist = config['structure']['whitelist'].split(",")
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
    walk = next(os.walk(directory))
    files = walk[2]
    for walking_dir in walk[1]:
        found_files = find_all_files_recursively(directory + "/" + walking_dir)
        for file in found_files:
            files.append(walking_dir+"/"+file)
    return files


def is_file_valid_nitf(xml_path):
    xml_doc = minidom.parse(xml_path)
    if len(xml_doc.getElementsByTagName('nitf:nitf')) != 0:
        # file is nitf, lets check if it is a valid article. todo
        return True
    return False


def is_file_in_list(file, checklist):
    for listed_item in checklist:
        if listed_item in file:
            return True
    return False

