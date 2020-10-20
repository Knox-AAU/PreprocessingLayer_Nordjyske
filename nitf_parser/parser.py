from datetime import datetime
from xml.dom import minidom
import configparser
from crawler.publication import *


class NitfParser:
    publication = Publication()
    article = Article()

    def __init__(self):
        pass

    def __parse_header(self, header_element):
        """ Parses the header, and gathers the needed information from it.
        :param header_element: The XML-dom element for the header element in the NITF file.
        :return: A dictionary of the newly gathered information.
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
        """ Returns needed information from metadata including by-line, page-number and id
        :param metadata:
        :return:
        """
        config = configparser.ConfigParser()
        config.read('metadata-mapper.ini')

        # get name attribute
        data = [data for data in metadata if data.getAttribute("name") == config['metadata']['name']]
        byline = {'name': {},
                  'email': {}
                  }

        if len(data) != 0:
            byline['name'] = data[0].getAttribute('content')

        # get email attribute
        data = [data for data in metadata if data.getAttribute("name") == config['metadata']['email']]
        if len(data) != 0:
            byline['email'] = data[0].getAttribute('content')

        # add name and email
        self.article.byline = Byline(byline)

        # get page attribute
        data = [data for data in metadata if data.getAttribute("name") == config['metadata']['page']]
        if len(data) != 0:
            self.article.page = data[0].getAttribute('content')

        # get nmid attribute
        data = [data for data in metadata if data.getAttribute("name") == config['metadata']['nmid']]
        if len(data) != 0:
            self.article.id = data[0].getAttribute('content')

    def __parse_doc_data(self, doc_data):
        """ Returns needed information from docdata including release date
        :param doc_data:
        :return:
        """
        temp = doc_data.getElementsByTagName('nitf:date.release')[0].getAttribute('norm')
        if len(temp) != 0:
            self.publication.published_at = temp
            self.article.published_at = self.publication.published_at

    def __parse_pub_data(self, pub_data):
        """ Returns needed information from pub_data including publisher
        :param pub_data:
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
        """ Returns needed information from body including all paragraphs and subheaders
        :param content:
        :return:
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
                if paragraph_kind is not "":
                    p.kind = paragraph_kind

                p.value = paragraph.firstChild.nodeValue
                self.article.add_paragraph(p)

    def __parse_body_head(self, head):
        """ Returns needed information from head including title and trompet
        :param head:
        :return:
        """
        hl1s = head.getElementsByTagName('nitf:hl1')
        if len(hl1s) > 0:
            self.article.headline = hl1s[0].firstChild.nodeValue

        hl2s = head.getElementsByTagName('nitf:hl2')
        if len(hl2s) > 0:
            # todo tjek op om det er korrekt
            self.article.lead = hl2s[0].firstChild.nodeValue

    def __parse_body(self, body_element):
        """Calls the needed methods to extract information from the body, and merges it into one object
        :param body_element:
        :return:
        """
        # https://www.w3schools.com/xml/dom_element.asp

        # body head contains the header and lead of an article
        self.__parse_body_head(body_element.getElementsByTagName("nitf:body.head")[0])
        # body content contains the paragraphs and subheaders
        self.__parse_body_content(body_element.getElementsByTagName("nitf:body.content")[0])

    def parse(self, article_path):
        self.article = Article()

        xml_doc = minidom.parse(article_path)
        item_list = xml_doc.getElementsByTagName('nitf:nitf')

        header_element = item_list[0].getElementsByTagName('nitf:head')[0]

        self.__parse_header(header_element)

        body_elements = item_list[0].getElementsByTagName('nitf:body')

        if len(body_elements) != 0:
            self.__parse_body(body_elements[0])

        return self.article
