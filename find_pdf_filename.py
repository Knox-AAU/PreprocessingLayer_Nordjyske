import os
import re

def find_pdf_filename(xml_name):
    """
    Finds the pdf name corresponding to a given xml filepath
    @param xml_name: path to a the xml file 
    """
    #removes path from string, only keeping filename
    name = os.path.basename(xml_name)
    base_path = __get_file_path(xml_name)
    regex_string = __str_to_regex_pattern(name)
    regex = re.compile(regex_string)
    result = []
    # Check all files in parent directory of XML file
    for filename in os.listdir(base_path):
        # if pdf matches regex based on the xml filename 
        if regex.match(filename):
            result.append(filename)
    return base_path+result[0]

def __str_to_regex_pattern(str):
    """
    Creates a regex string based on the xml file, in order to find matching pdf filename
    """
    str = str.replace("-", "_")

    #sometimes "forside" is misspelled as "forsidea", "forsidet"...
    #removes the last letter after forside to fix
    fix_forside_substr = re.compile("forside[a-zA-Z]")
    if len(re.findall(fix_forside_substr, str)):
        bad = re.findall(fix_forside_substr, str)
        str = str.replace(bad[0], "forside")
    
    filename_arr = str.split("_")
    filename_arr.pop()
    regex_str = "[-_]*".join(filename_arr)
    regex_str = regex_str + "\.pdf"
    return regex_str

def __get_file_path(str):
    '''
    Find path to file, by removing filename from str
    '''
    path = str.split("/")
    path.pop()
    path.pop()
    path = "/".join(path)+"/"
    return path
    
def __test():
    '''
    function to see if all xml files get a corresponding pdf file
    not propper test
    '''
    xml_files = []
    pdf_files = []
    path = "/home/aau/Desktop/test_findpdfname/2020-12-24/TabletXML"
    xml_re = re.compile(".*\.xml")
    for filename in os.listdir(path):
        if xml_re.match(filename):
            xml_files.append(path+"/"+filename)
    for x in xml_files:
        pdf_files.append(find_pdf_filename(x))
    print(f"Found pdf files for all xml files: {len(xml_files)==len(pdf_files)}")
    # for x, y in zip(xml_files, pdf_files):
    #     print(os.path.basename(x))
    #     print(y)

