from xml.dom import minidom
from datetime import datetime
import json
import codecs
import sys
import configparser


def merge(a, b, path=None):
    """ Used to merge objects together recursively
     :param path: Used to call the function recursively, do not specify at caller.
     :param a: Dictionary input #1
     :param b: Dictionary input #2
     :return: The merged dictionary
     """
    # https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries

    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def parse_header(header_element):
    """ Parses the header, and gathers the needed information from it.
    :param header_element: The XML-dom element for the header element in the NITF file.
    :return: A dictionary of the newly gathered information.
    """
    # https://www.w3schools.com/xml/dom_element.asp
    # We extract all elements from the XML file and call functions to extract the information from the elements
    _object = {}

    # Metadata contains type, byline, page number and nmId
    metaDataList = header_element.getElementsByTagName('nitf:meta')
    _object = merge(_object, parse_metadata(metaDataList))

    # Docdata contains publishment date
    docData = header_element.getElementsByTagName('nitf:docdata')[0]
    _object = merge(_object, parse_docdata(docData))

    # Pubdata contains publisher and publication
    pubData = header_element.getElementsByTagName('nitf:pubdata')[0]
    _object = merge(_object, parse_pubdata(pubData))

    return _object


def parse_metadata(metadatas):
    """ Returns needed information from metadata including by-line, page-number and id
    :param metadatas:
    :return:
    """
    config = configparser.ConfigParser()
    config.read('metadata-mapper.ini')

    _object = {'content': {}}

    _object['type'] = [metadata for metadata in metadatas if metadata.getAttribute("name") == config['metadata']['type']][0].getAttribute("content")

    _object['content']['byline'] = {}
    _object['content']['byline']['name'] = [metadata for metadata in metadatas if metadata.getAttribute("name") == config['metadata']['name']][0].getAttribute("content")
    _object['content']['byline']['email'] = [metadata for metadata in metadatas if metadata.getAttribute("name") == config['metadata']['email']][0].getAttribute("content")

    _object['content']['page'] = int([metadata for metadata in metadatas if metadata.getAttribute("name") == config['metadata']['page']][0].getAttribute("content"))

    _object['content']['nmId'] = [metadata for metadata in metadatas if metadata.getAttribute("name") == config['metadata']['nmid']][0].getAttribute("content")

    return _object


def parse_docdata(docdata):
    """ Returns needed information from docdata including release date
    :param docdata:
    :return:
    """
    _object = {'content': {}}

    _object['content']['publishedAt'] = docdata.getElementsByTagName('nitf:date.release')[0].getAttribute('norm')

    return _object


def parse_pubdata(pubdata):
    """ Returns needed information from pubdata including publisher
    :param pubdata:
    :return:
    """
    _object = {'content': {}}

    _object['content']['publisher'] = pubdata.getAttribute('name')
    _object['content']['publication'] = pubdata.getAttribute("position.section").split(",")[1]

    return _object


def parse_body_content(content):
    """ Returns needed information from body including all paragraphs, and subheaders
    :param content:
    :return:
    """
    _object = {'content': {'paragraphs': []}, }

    blocks = content.getElementsByTagName('nitf:block')
    for block in blocks:
        paragraphs = block.getElementsByTagName('nitf:p')
        for paragraph in paragraphs:
            if len(paragraph.childNodes) == 0:
                continue
            p_class = paragraph.getAttribute('class')
            p_text = paragraph.firstChild.nodeValue
            p_object = {'kind': 'paragraph', 'value': p_text}
            if p_class == "subheader":
                p_object['kind'] = "subheader"
            _object['content']['paragraphs'].append(p_object)
    return _object


def parse_body_head(head):
    """ Returns needed information from head including title and trompet
    :param head:
    :return:
    """
    _object = {'content': {}}

    _object['content']['title'] = head.getElementsByTagName('nitf:hl1')[0].firstChild.nodeValue

    hl2s = head.getElementsByTagName('nitf:hl2')
    if len(hl2s) > 0:
        _object['content']['trompet'] = hl2s[0].firstChild.nodeValue

    return _object

def parse_body(body_element):
    """Calls the needed methods to extract information from the body, and merges it into one object
    :param body_element:
    :return:
    """
    # https://www.w3schools.com/xml/dom_element.asp
    _object = {}
    # body head contains the header and trompet of an article
    _object = merge(_object, parse_body_head(body_element.getElementsByTagName("nitf:body.head")[0]))
    # body content contains the paragrapgs and subheaders
    _object = merge(_object, parse_body_content(body_element.getElementsByTagName("nitf:body.content")[0]))

    return _object


if __name__ == '__main__':
    args = sys.argv

    if len(args) > 3 or len(args) < 2:
        raise Exception('Provide one or two arguments, the path to read, and optionally the path to output json to.')
    path = args[1]
    output_path = None
    if len(args) == 3:
        output_path = args[2]


    _object = {'schemaLocation': 'http://iptc.org/std/NITF/2006-10-18/', 'schemaVersion': 1.0, 'generator': {
        "app": "The app",
        "version": "1.0.0",
        "generatedAt": datetime.now().isoformat(),

    }, "extractedFrom": [
            path
        ]
               }

    xmldoc = minidom.parse(path)
    itemlist = xmldoc.getElementsByTagName('nitf:nitf')

    headerElement = itemlist[0].getElementsByTagName('nitf:head')[0]
    _object = merge(_object, parse_header(headerElement))

    bodyElement = itemlist[0].getElementsByTagName('nitf:body')[0]
    _object = merge(_object, parse_body(bodyElement))

    print(_object)
    if output_path is not None:
        with codecs.open(output_path, 'w', encoding="utf-8") as outfile:
            json.dump(_object, outfile, indent=4, ensure_ascii=False)