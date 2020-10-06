import cv2
import pytesseract
from PIL import Image


class TesseractModule:
    def __init__(self, tesseract_exe_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe_path

    def run_tesseract_on_image(self, path, language='dan'):
        """ Finds image from path, runs tesseract and returns words and confidence scores
        :param path: The image that tesseract runs
        :param language: The language of the image text
        :return: A matrix with the word and the corresponding confidence score
        """
        if path is None:
            raise TypeError
        try:
            image = self.__load_file(path)
            arr_all_data = pytesseract.image_to_data(image, lang=language)
            data_matrix = self.__tess_output_str_to_matrix(arr_all_data)
            data_matrix = self.__save_conf_and_text(data_matrix)
            data_matrix = self.__remove_hyphens(data_matrix)
            return data_matrix
        except FileNotFoundError:
            print("The image was not found in the path: " + path)
            return None

    @staticmethod
    def __load_file(path):
        """ Loads a .jp2 file from a given path
        :param path: The path of the file
        :return: The file in RGB format
        """
        img = Image.open(path).convert("L")
        return img

    @staticmethod
    def __tess_output_str_to_matrix(tesseract_str):
        """ Converts a string to a matrix
        :param tesseract_str: The string that is to be converted
        :return: A matrix
        """

        # Splits the string into an array containing rows
        rows = tesseract_str.split('\n')
        columns = []

        # Splits the array into a matrix containing the columns
        for item in rows:
            sub_list = []
            for num in item.split('\t'):
                sub_list.append(num)
            columns.append(sub_list)

        return columns

    @staticmethod
    def __save_conf_and_text(data_matrix):
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

    def __remove_hyphens(self, data_matrix):
        """ Removes all the hyphens that are between two words on different lines
        :param data_matrix: The matrix containing the words
        :return: A matrix with the hyphens before new-line removed
        """
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
                data_matrix[index][1] = self.__replace_last(word, "-", data_matrix[index + 1][1])
                data_matrix[index][0] = (int(data_matrix[index][0]) + int(data_matrix[index + 1][0])) / 2
                word_replaced = True

        for index in range(len(remove_index)):
            data_matrix.remove(data_matrix[remove_index[index] - index])

        return data_matrix

    @staticmethod
    def __replace_last(word, old_char, new_char):
        """ Replaces the last occurrence of old_char with new_char
        :param word: The word to be changed
        :param old_char: The character to be removed
        :param new_char: The character/string to replace old_char
        :return: A word containing the replaced word
        """
        head, _sep, tail = word.rpartition(old_char)
        return head + new_char + tail

    @staticmethod
    def __print_text_from_matrix(data_matrix):
        """ Prints the text from the matrix
        :param data_matrix: The matrix containing the words
        """
        length = len(data_matrix)

        for index in range(length):
            print(data_matrix[index][1], end=' ')
        print()

    @staticmethod
    def __get_average_conf_from_matrix(data_matrix):
        """ Gets the average of the confidence score
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

    def debug_prints(self, data_matrix):
        """ Used to debug the output. todo: Delete before release
        :param data_matrix: The matrix containing confidence score and words
        """
        self.__print_text_from_matrix(data_matrix)
        average_conf = self.__get_average_conf_from_matrix(data_matrix)
        print(average_conf)
        cv2.waitKey(0)


# todo: delete
tesseract_module = TesseractModule(r"/usr/local/Cellar/tesseract/4.1.1/bin/tesseract")
path1 = "testImages/1988.jp2"
path2 = "testImages/2017.jpg"
path3 = "testImages/udsnit2.png"

# todo: indsæt nedenstående i crawler.py
try:
    matrix = tesseract_module.run_tesseract_on_image(path3, "dan")
    # tesseract_module.debug_prints(matrix)
except TypeError:
    print("No image path was given")
