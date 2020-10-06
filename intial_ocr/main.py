import cv2
import numpy as np
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"/usr/local/Cellar/tesseract/4.1.1/bin/tesseract"


def load_file(path):
    """ Loads a .jp2 file from a given path
    :param path: The path of the file
    :return: The file in RGB format
    """
    if path is None:
        return None
    img = Image.open(path).convert("RGB")
    return img


def run_tesseract_on_image(img, language='dan'):
    """ Runs tesseract and returns todo:beskrivelse
    :param img: The image that tesseract runs
    :param language: The language of the image text
    :return:todo:beskrivelse
    """
    if img is None:
        return None
    arr_all_data = pytesseract.image_to_data(img, lang=language)
    list = conf_str_to_matrix(arr_all_data)
    print(list[5][11] + ' | ' + list[5][10])


"""
    lines = arr_all_data.split('\n')
    list = []

    for item in lines:
        subl = []
        for num in item.split('\t'):
            subl.append(num)
        list.append(subl)

    print(list[5][11] + ' | ' + list[5][10])
    """


def conf_str_to_matrix(line):
    """ Converts a string to a matrix
    :param line: The string that is to be converted
    :return: a matrix
    """

    # Splits the string into an array containing rows
    rows = line.split('\n')
    columns = []

    # Splits the array into a matrix containing the columns
    for item in rows:
        subList = []
        for num in item.split('\t'):
            subList.append(num)
        columns.append(subList)

    print(columns[5][11] + ' | ' + columns[5][10])
    return columns


# img5 = Image.open("1988.jp2", "RGB")
img4 = Image.open("testImages/1988.jp2").convert("RGB")
img5 = cv2.imread("testImages/test2.jpg")

run_tesseract_on_image(img5, 'dan')

# text = pytesseract.image_to_string(img5, lang='dan')
text = pytesseract.image_to_data(img5, lang='eng')
# text = pytesseract.image_to_data(img, lang='dan')
# print(text)

# cv2.imshow("Img", img)
cv2.waitKey(0)
