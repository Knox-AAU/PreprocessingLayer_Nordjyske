import os
from datetime import datetime

from knox_source_data_io.io_handler import IOHandler, Generator


def save_to_json(folder, publications):
    """ Saves the publications as JSON files in the given folder

    :param folder: The destination folder
    :param publications: A list of publications that should be saved
    :return:
    """
    publications = __merge(publications)

    for pub in publications:
        handler = IOHandler(
            Generator(app="This app", version=1.0, generated_at=datetime.now().isoformat()),
            "http://iptc.org/std/NITF/2006-10-18/")
        filename = os.path.join(
            folder,
            f'{datetime.strptime(pub.published_at, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d")}'
            f'_{__sanitize(pub.publication)}.json')

        with open(filename, 'w', encoding="utf-8") as outfile:
            handler.write_json(pub, outfile)


def __sanitize(string):
    """ Handles all the sanitation of the string

    :param string:
    :return: Sanitized string
    """
    without_special_chars = ''.join([a for a in string.lower() if a.isalnum()])
    without_danish_letters = ''.join(
        [__map_from_danish(a) for a in without_special_chars])
    return without_danish_letters


def __map_from_danish(char):
    """ Maps 'æ' to 'ae', 'ø' to 'oe', and 'å' to 'aa'

    :param char:
    :return: The converted char as a string or the given char if not 'æ', 'ø', or 'å'
    """
    if char == 'æ':
        return "ae"
    if char == "ø":
        return "oe"
    if char == "å":
        return "aa"
    return char


def __merge(publications):
    found_publications = []
    for pub in publications:
        __add_publication_if_new_or_add_articles_to_already_found_publication(found_publications, pub)
    return found_publications


def __add_publication_if_new_or_add_articles_to_already_found_publication(found_publications,
                                                                          input_pub):
    """ Adds input_pub to found_publications if it is not already present,
    else adds the articles of input_pub to the matching publication in found_publications

    :param found_publications: A list of publications that have already been found
    (will be altered to reflect the effect of the method)
    :param input_pub: The publication containing articles to be added
    :return:
    """
    # Ensures that articles with no paragraphs are not added to the publications
    if len(input_pub.articles[0].paragraphs) == 0:
        return

    # Get reference to the publication that has already been added to the found publications
    # (returns 'None' if no match is found)
    matching_publication_in_publications_found = next(
        (pub for pub in found_publications
         if pub.publication == input_pub.publication
         ), None)

    # Check if the publication is not part of the found publications
    # If it is, add it as a new publication
    # Else, add its article to the already added publication
    if matching_publication_in_publications_found is None:
        found_publications.append(input_pub)
    else:
        matching_publication_in_publications_found.add_article(input_pub.articles[0])
