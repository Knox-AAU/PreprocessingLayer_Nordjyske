from xml.dom import minidom
import configparser
from knox_source_data_io.models.publication import Publication, Article, Paragraph

from pathlib import Path

class NitfParser:
    """
    Used to parse NITF files to JSON.
    """
    def __init__(self):
        self.publication = Publication()
        self.article = Article()

    def __parse_header(self, header_element):
        """
        Parses the header, and gathers the needed information from it.

        @param header_element: The XML-dom element for the header element in the NITF file.
        @return: A dictionary of the newly gathered information.
        """
        # https://www.w3schools.com/xml/dom_element.asp
        # We extract all elements from the XML file and call functions to extract the information from the elements
        # Metadata contains type, byline, page number and nmId
        meta_data_list = header_element.getElementsByTagName('nitf:meta')
        self.__parse_metadata(meta_data_list)

        # Docdata contains publishing date
        doc_data = header_element.getElementsByTagName('nitf:docdata')[0]
        self.__parse_doc_data(doc_data)

        # Pub_data contains publisher and publication
        pub_data = header_element.getElementsByTagName('nitf:pubdata')[0]
        self.__parse_pub_data(pub_data)

    def __parse_metadata(self, metadata):
        """
        Adds the information from the metadata element to the related attributes, including by-line, page-number and id.

        @param metadata: metadata elements to parse.
        @return: void.
        """

        # The config file had some problem when running on windows
        # Below is a workaround, that works on both Linux and Windows
        HERE = Path(__file__).parent.resolve()
        CONFIG_PATH = HERE / '../metadata-mapper.ini'

        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)

        # get name attribute
        byline = {'name': None, 'email': None}

        data = [data for data in metadata if
                data.getAttribute("name") == config['metadata']['name']]
        if len(data) != 0:
            byline['name'] = data[0].getAttribute('content')

        # get email attribute
        data = [data for data in metadata if
                data.getAttribute("name") == config['metadata']['email']]
        if len(data) != 0:
            byline['email'] = data[0].getAttribute('content')

        # add name and email
        if byline['name'] is not None:
            self.article.add_byline(byline['name'], byline['email'])

        # get page attribute
        data = [data for data in metadata if
                data.getAttribute("name") == config['metadata']['page']]
        if len(data) != 0:
            self.article.page = int(data[0].getAttribute('content'))

        # get nmid attribute
        data = [data for data in metadata if
                data.getAttribute("name") == config['metadata']['nmid']]
        if len(data) != 0:
            if data[0].getAttribute('content') != "noid":
                self.article.id = data[0].getAttribute('content')
            else:
                self.article.id = None

    @staticmethod
    def sanitize_spaces(a: str) -> str:
        """
        Splits a string by any whitespace, then joins by normal spaces, to remove double-spaces, tabs, newlines etc.

        @param a: string to sanitize.
        @return: the sanitized string.
        """
        if a is None:
            return a
        return " ".join(a.split())

    def __parse_doc_data(self, doc_data):
        """
        Sets the needed information from docdata including release date.

        @param doc_data: the data to retrieve the desired data from.
        @return: void.
        """
        temp = doc_data.getElementsByTagName('nitf:date.release')[0].getAttribute('norm')
        if len(temp) != 0:
            self.publication.published_at = temp
            self.article.published_at = self.publication.published_at

    def __parse_pub_data(self, pub_data):
        """
        Returns needed information from pub_data including publisher.

        @param pub_data: the publication data to parse.
        """
        temp = pub_data.getAttribute('name')
        if len(temp) != 0:
            self.publication.publisher = temp
            self.article.publisher = temp

        temp = pub_data.getAttribute("position.section")
        if len(temp) != 0:
            self.publication.publication = temp.split(",")[1]
            self.article.publication = self.publication.publication

    def __parse_body_content(self, content):
        """
        Adds the information retrieved from the body to the article attribute, including all paragraphs and subheaders.

        @param content: the content to parse.
        @return: void.
        """
        blocks = content.getElementsByTagName('nitf:block')
        for block in blocks:
            paragraphs = block.getElementsByTagName('nitf:p')
            for paragraph in paragraphs:
                if len(paragraph.childNodes) == 0:
                    continue
                p = Paragraph()
                p.kind = "paragraph"
                paragraph_kind = paragraph.getAttribute('class')
                if paragraph_kind != "":
                    p.kind = paragraph_kind

                p.value = NitfParser.sanitize_spaces(
                    NitfParser.__get_text_recursive_xmldom(paragraph).strip())

                self.article.add_paragraph(p)

    @staticmethod
    def __get_text_recursive_xmldom(element) -> str:
        """
        Get the text from an element and all its children recursively.

        @param element: the element to extract the text from.
        @return: the accumulated text as a string.
        """
        accumulated = ""
        for child in element.childNodes:
            if child.nodeValue is not None:
                accumulated += f"{child.nodeValue} "
            else:
                accumulated += f"{NitfParser.__get_text_recursive_xmldom(child)} "

        return accumulated

    def __parse_body_head(self, head):
        """
        Adds information from head to the article attribute, including title and trompet as paragraphs.

        @param head: the head element to extract information from.
        @return: void.
        """
        subheaders = []
        hl1s = head.getElementsByTagName('nitf:hl1')
        if len(hl1s) > 0:
            self.article.headline = NitfParser.sanitize_spaces(hl1s[0].firstChild.nodeValue)
            subheaders.extend(hl1s[1:])
        hl2s = head.getElementsByTagName('nitf:hl2')
        subheaders.extend(hl2s)

        for subheader in subheaders:
            p = Paragraph()
            p.kind = "subheader"
            p.value = NitfParser.sanitize_spaces(
                NitfParser.__get_text_recursive_xmldom(subheader).strip()
            )
            self.article.add_paragraph(p)

    def __parse_body(self, body_element):
        """
        Calls the needed methods to extract information from the body, merges it into one object,
        and adds it to the relevant attributes.
        Based on the code at: https://www.w3schools.com/xml/dom_element.asp.

        @param body_element: the body element to extract data from.
        @return: void.
        """

        # body head contains the header and lead of an article
        self.__parse_body_head(body_element.getElementsByTagName("nitf:body.head")[0])
        # body content contains the paragraphs and subheaders
        self.__parse_body_content(body_element.getElementsByTagName("nitf:body.content")[0])

    def parse(self, article_path):
        """
        Parses NITF files found at the specified path.

        @param article_path: path to the article (in NITF format) to parse.
        @return: the generated Publication.
        """
        self.article = Article()
        self.article.add_extracted_from(article_path)
        xml_doc = minidom.parse(article_path)
        item_list = xml_doc.getElementsByTagName('nitf:nitf')

        header_element = item_list[0].getElementsByTagName('nitf:head')[0]

        self.__parse_header(header_element)

        body_elements = item_list[0].getElementsByTagName('nitf:body')

        if len(body_elements) != 0:
            self.__parse_body(body_elements[0])
        self.publication.add_article(self.article)

        return self.publication

    def parse_file(self, file):
        """
        Parses a file based on the path of the file.

        @param file: file to parse.
        @return: the generated Publication.
        """
        return self.parse(file.path)
