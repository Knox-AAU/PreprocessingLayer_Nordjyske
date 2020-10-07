import cv2
import pytesseract
from PIL import Image


class TesseractModule:
    confidence_index = 0
    word_index = 1

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
            data_matrix = self.__merge_matrix_into_paragraphs(data_matrix)
            data_matrix = self.__remove_empty_words(data_matrix)
            # data_matrix = self.__dunno_du(data_matrix, ".")
            # data_matrix = self.__dunno_du(data_matrix, " ")
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
            if index == 0:
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
            word = data_matrix[index][self.word_index]
            if word_replaced:
                remove_index.append(index + 1)
                word_replaced = False
                continue
            if word.endswith("-"):
                try:
                    data_matrix[index][self.word_index] = self.__replace_last(word, "-", data_matrix[index + 2][self.word_index])
                    data_matrix[index][self.confidence_index] = \
                        (int(data_matrix[index][self.confidence_index]) + int(data_matrix[index + 2][self.confidence_index])) / 2
                    word_replaced = True
                except IndexError:
                    continue
        for index in range(len(remove_index)):
            data_matrix.remove(data_matrix[remove_index[index] - index])

        return data_matrix

    def __dunno_du(self, data_matrix, compare_str):
        """ Merges the words into sentences and returns a matrix of sentences
        :param data_matrix:
        :param compare_str:
        :return:
        """
        length = len(data_matrix)
        new_matrix = []
        temp_list = []
        sentence = " "
        conf_num = 0

        for index in range(length):
            conf_num += int(data_matrix[index][self.confidence_index])
            word = data_matrix[index][self.word_index]
            temp_list.append(word)
            if word.endswith(compare_str) or index == length - 1:
                # Gets average confidence score
                conf_num /= len(temp_list)
                sentence = sentence.join(temp_list)
                temp_list = [conf_num, sentence]
                new_matrix.append(temp_list)

                temp_list = []
                conf_num = 0
                sentence = " "
        return new_matrix

    def __merge_matrix_into_paragraphs(self, data_matrix):
        """ Merges the words into paragraphs and saves these in a matrix
        :param data_matrix: The matrix containing words and their confidence scores
        :return: A matrix containing paragraphs and their confidence score
        """
        length = len(data_matrix)
        new_matrix = []
        temp_list = []
        paragraph = " "
        conf_num = 0

        for index in range(length):
            word = data_matrix[index][self.word_index]
            temp_list.append(word)
            conf_num += self.__get_conf(int(data_matrix[index][self.confidence_index]))

            # Checks if the next two items are in bound
            # Gets their confidence scores or sets them to '-1' to indicate whitespace
            if index < length - 2:
                conf_next_word = int(data_matrix[index + 1][self.confidence_index])
                conf_next_next_word = int(data_matrix[index + 2][self.confidence_index])
            else:
                conf_next_word = -1
                conf_next_next_word = -1
            # '-1' is the value that is given if there is whitespace
            if word.endswith(".") and conf_next_word == -1 and conf_next_next_word == -1:
                conf_num /= len(temp_list)
                paragraph = paragraph.join(temp_list)
                temp_list = [conf_num, paragraph]
                new_matrix.append(temp_list)

                temp_list = []
                conf_num = 0
                paragraph = " "
        return new_matrix

    def __get_conf(self, conf):
        if conf <= 100 or conf >= 0:
            return conf
        else:
            return 0

    def __remove_empty_words(self, data_matrix):
        """ Removes empty words and unnecessary whitespace
        :param data_matrix: A matrix containing words and their confidence scores
        :return: A cleaned-up matrix
        """
        length = len(data_matrix)
        remove_index = []

        for index in range(length):
            conf = data_matrix[index][self.confidence_index]
            word = data_matrix[index][self.word_index]
            if conf > 100 or conf < 0:
                remove_index.append(index)
            elif "  " in word:
                word.replace("  ", " ")
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

    def __print_text_from_matrix(self, data_matrix):
        """ Prints the text from the matrix
        :param data_matrix: The matrix containing the words
        """
        length = len(data_matrix)

        for index in range(length):
            print(data_matrix[index][self.word_index], end=' ')
        print()

    def __get_average_conf_from_matrix(self, data_matrix):
        """ Gets the average of the confidence score
        :param data_matrix: The matrix containing the confidence score
        :return: A float with the average confidence score
        """
        length = len(data_matrix)
        num = 0

        for index in range(length):
            temp_num = int(data_matrix[index][self.confidence_index])
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
path4 = "testImages/1988_udsnit2.jp2"
path5 = "testImages/test2.jpg"

# todo: indsæt nedenstående i crawler.py
try:
    matrix = tesseract_module.run_tesseract_on_image(path4, "dan")
    print(matrix)
    # tesseract_module.debug_prints(matrix)
except TypeError:
    print("No image path was given")
