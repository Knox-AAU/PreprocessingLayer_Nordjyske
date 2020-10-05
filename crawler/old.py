# #from pgmagick import Image
#
# #img = Image('CB_TM432.jp2') # Input Image
# #img.write('CB_TM432.jpeg')  # Output Image
#
# import os
# import re
# import datetime
# import json
# import shutil
#
# pattern = re.compile("\d\d\d\d-\d\d-\d\d-\d\d")
#
# class Folder:
#     def __init__(self, directory,folder_name):
#         self.path = directory + "/" + folder_name
#         self.year = int(folder_name[0:4])
#         self.month = int(folder_name[5:7])
#         self.date = int(folder_name[8:10])
#
#
# def find_folders_recursively(directory):
#     print("Searching in "+directory)
#     dirs = next(os.walk(directory))[1]
#
#     found_folders = []
#
#     for cdir in dirs:
#         if re.match(pattern, cdir):
#             # Add to list to return
#             found_folders.append(Folder(directory,cdir))
#         else:
#             # extend recursively
#             found_folders.extend(find_folders_recursively(directory+"/"+cdir))
#     return found_folders
#
# # directory = '/srv/data/newsarchive_nobackup'
# # folders = find_folders_recursively(directory)
# # folders.sort(key=lambda folder: int(str(folder.year)+str(folder.month)+str(folder.date)))
#
# def output(folders):
#     data = []
#     for folder in folders:
#         data.append(folder.__dict__)
#     with open('folders.json', 'w') as f:
#         json.dump(data, f, indent=4)
#
# def load(path):
#     with open(path) as json_file:
#         data = json.load(json_file)
#     return data
#
#
# def find_file_not_brik_in_dir(directory):
#     files = next(os.walk(directory))[2]
#     for file in files:
#         if "brik" in file:
#             continue
#         if ".md5" in file:
#             continue
#         if ".jp2" in file:
#             return directory+"/"+file
#
# folders = load("./folders.json")
#
# years = []
#
# for folder in folders:
#     if folder['year'] not in years:
#         year = folder['year']
#         if year < 1963:
#             continue
#         file_to_save = find_file_not_brik_in_dir(folder['path'])
#         if file_to_save is None:
#             continue
#         years.append(year)
#         print("Dir" + folder['path'])
#         print("File to save: "+file_to_save)
#         print("Year: " + str(year))
#         print("Copying "+file_to_save+" to "+ "./years_2/"+str(year)+".jp2")
#         shutil.copyfile(file_to_save,"./years_2/"+str(year)+".jp2")
#
#
#
#
#
# # for folder in folders:
# #     print('['+folder.path+'] '+folder.year+'-'+folder.month+'-'+folder.date)\
#
#
#
#
