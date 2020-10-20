import configparser

import pytesseract
from PIL import Image
from publication import Article, Paragraph, Publication

class TesseractModule:
    confidence_index = 0
    word_index = 1

    def run_tesseract_on_image(self, file_path, language='dan', tesseract_path=None):
        """ Finds image from path, runs tesseract and returns words and confidence scores
        :param tesseract_path: Path to tesseract, if not in system PATH.
        :param file_path: The image that tesseract runs
        :param language: The language of the image text
        :return: A matrix with the word and the corresponding confidence score
        """
        if tesseract_path is not None:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        try:
            image = self.__load_file(file_path)
        except FileNotFoundError:
            raise Exception("The image was not found in the path: " + file_path)
        arr_all_data = pytesseract.image_to_data(image, lang=language, config="--psm 4")
        data_matrix = self.__tess_output_str_to_matrix(arr_all_data)
        data_matrix = self.__save_conf_and_text(data_matrix)
        data_matrix = self.__remove_hyphens(data_matrix)
        data_matrix = self.__merge_matrix_into_paragraphs(data_matrix)
        # return data_matrix
        return self.__convert_matrix_to_publication(data_matrix, file_path)

    def __convert_matrix_to_publication(self, paragraph_matrix, file_path):
        """ Converts the output matrix (List of paragraphs) into an article
       :param paragraph_matrix: List of paragraphs
       :return: An article
       """

        # Load the config file to get default publication name
        config = configparser.ConfigParser()
        config.read('publication_default.ini')

        # Generate new publication and set the publication name to the default
        pub = Publication()
        pub.publication = config['publication']['name']

        article = Article()
        for row in paragraph_matrix:
            p = Paragraph()
            p.kind = "paragraph"
            p.value = row[1]
            article.add_paragraph(p)
        article.confidence = self.__get_average_conf_from_matrix(paragraph_matrix)
        article.extracted_from = file_path

        pub.add_article(article)

        return pub

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
        """ Converts Tesseract's output string to a matrix
        :param tesseract_str: The string that is to be converted
        :return: A matrix
        """
        # Split the string into newlines, then split by tabs.
        return [x.split('\t') for x in tesseract_str.split('\n')]

    @staticmethod
    def __save_conf_and_text(data_matrix):
        """ Only saves the confidence score and the word
        :param data_matrix: The matrix with all information from tesseract
        :return: Matrix without redundant information
        """
        new_matrix = []

        for index in range(len(data_matrix) - 1):
            # 'index == 0' contains the header with the column names
            if index == 0:
                continue
            sub_list = [data_matrix[index][10], data_matrix[index][11]]
            new_matrix.append(sub_list)
        return new_matrix

    def __remove_hyphens(self, data_matrix):
        """ Removes all the hyphens that are between two words on different lines
        :param data_matrix: The matrix containing the words
        :return: A matrix with the hyphens before new-line removed
        """
        length = len(data_matrix)
        remove_index = []

        for index in range(length):
            word = data_matrix[index][self.word_index]
            if word.endswith("-"):
                try:
                    # Merges the two words, while removing the hyphen
                    # 'index + 2' is the index of the word on the next line
                    data_matrix[index][self.word_index] = self.__replace_last(word, "-",
                                                                              data_matrix[index + 2][self.word_index])
                    # Takes the average of the confidence score for the two words
                    data_matrix[index][self.confidence_index] = (int(data_matrix[index][self.confidence_index]) +
                                                                 int(data_matrix[index + 2][self.confidence_index])) / 2
                    remove_index.append(index + 2)
                except IndexError:
                    break
        for index in range(len(remove_index)):
            data_matrix.remove(data_matrix[remove_index[index] - index])

        return data_matrix

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
            conf = int(data_matrix[index][self.confidence_index])

            if 0 <= conf <= 100:
                temp_list.append(word)
                conf_num += conf
            # Checks if the next two items are in bound
            # Gets their confidence scores or sets them to '-1' to indicate whitespace
            if index < length - 2:
                conf_next_word = int(data_matrix[index + 1][self.confidence_index])
                conf_next_next_word = int(data_matrix[index + 2][self.confidence_index])
            else:
                conf_next_word = -1
                conf_next_next_word = -1
            # '-1' is the value that is given if there is whitespace
            if (word.endswith(".") or "Af" in temp_list) and conf_next_word == -1 and conf_next_next_word == -1:
                conf_num /= len(temp_list)
                paragraph = paragraph.join(temp_list)
                temp_list = [conf_num, paragraph]
                new_matrix.append(temp_list)

                temp_list = []
                conf_num = 0
                paragraph = " "
        return new_matrix

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
            print(data_matrix[index][self.word_index])
        print()

    def __get_average_conf_from_matrix(self, data_matrix):
        """ Gets the average of the confidence score
        :param data_matrix: The matrix containing the confidence score
        :return: A float with the average confidence score
        """
        length = len(data_matrix)

        if length == 0:
            return 0

        num = 0

        for index in range(length):
            temp_num = int(data_matrix[index][self.confidence_index])
            if 0 <= temp_num <= 100:
                num += temp_num
        return num / length
