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
    """ Runs tesseract and returns word and confidence score
    :param img: The image that tesseract runs
    :param language: The language of the image text
    :return: A matrix with the word and the corresponding confidence score
    """
    if img is None:
        return None
    arr_all_data = pytesseract.image_to_data(img, lang=language)
    data_matrix = conf_str_to_matrix(arr_all_data)
    data_matrix = save_conf_and_text(data_matrix)
    data_matrix = remove_hyphens(data_matrix)

    return data_matrix


def conf_str_to_matrix(line):
    """ Converts a string to a matrix
    :param line: The string that is to be converted
    :return: A matrix
    """

    # Splits the string into an array containing rows
    rows = line.split('\n')
    columns = []

    # Splits the array into a matrix containing the columns
    for item in rows:
        sub_list = []
        for num in item.split('\t'):
            sub_list.append(num)
        columns.append(sub_list)

    return columns


def save_conf_and_text(data_matrix):
    """ Only saves the confidence score and the word
    :param data_matrix: The matrix with all information from tesseract
    :return: Matrix without redundant information
    """
    length = len(data_matrix) - 1
    new_matrix = []

    for index in range(length):
        sub_list = []
        # index == 0 contains the header
        if data_matrix[index][10] == "-1" or index == 0:
            continue
        sub_list.append(data_matrix[index][10])
        sub_list.append(data_matrix[index][11])
        new_matrix.append(sub_list)
    return new_matrix


def print_text_from_matrix(data_matrix):
    """ Prints the text from the matrix
    :param data_matrix: The matrix containing the words
    """
    length = len(data_matrix)

    for index in range(length):
        print(data_matrix[index][1], end=' ')
    print()


def get_average_conf_from_matrix(data_matrix):
    """ Gets the avergae of the confidence score
    :param data_matrix: The matrix containing the confidence score
    :return: A float with the average confidence score
    """
    length = len(data_matrix)
    num = 0

    for index in range(length):
        temp_num = int(data_matrix[index][0])
        if 0 <= temp_num <= 100:
            num += temp_num
    return num / length


def remove_hyphens(data_matrix):
    """ Removes all the hyphens that are between the words
    :param data_matrix:
    :return:
    """

    # Gør så den kun fjerner sidste bindestreg og ikke alle
    length = len(data_matrix)
    word_replaced = False
    remove_index = []

    for index in range(length):
        word = data_matrix[index][1]
        if word_replaced:
            remove_index.append(index)
            word_replaced = False
            continue
        if word.endswith("-"):
            data_matrix[index][1] = word.replace("-", data_matrix[index + 1][1])
            word_replaced = True

    for index in range(len(remove_index)):
        data_matrix.remove(data_matrix[remove_index[index] - index])
    return data_matrix


def debug_prints(data_matrix):
    print_text_from_matrix(data_matrix)
    average_conf = get_average_conf_from_matrix(data_matrix)
    print(average_conf)


img4 = Image.open("testImages/1988.jp2").convert("RGB")
img5 = Image.open("testImages/test2.jpg")

# matrix = run_tesseract_on_image(img5, 'eng')
ocr_matrix = run_tesseract_on_image(img4, 'dan')
debug_prints(ocr_matrix)

# text = pytesseract.image_to_string(img5, lang='dan')
# text = pytesseract.image_to_data(img5, lang='eng')
# text = pytesseract.image_to_data(img, lang='dan')
# print(text)

# cv2.imshow("Img", img)
cv2.waitKey(0)
