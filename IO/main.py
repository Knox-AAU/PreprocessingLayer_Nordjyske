from knox_source_data_io.models.publication import *
from knox_source_data_io.IOHandler import *
import os


def print_hi(name):
    # Generate publication
    publication = Publication()
    publication.publisher = "Nordjyske Medie"
    publication.published_at = "Some time"
    publication.publication = "A newspaper"
    publication.pages = 0

    # Generate article
    article = Article()
    article.headline = "En god artikel"
    article.subhead = ""
    article.lead = ""
    article.byline = Byline(name="Thomas", email="thomas@tlorentzen.net")
    article.extracted_from.append("Some file")
    article.confidence = 1.0
    article.id = 0
    article.page = 0

    for x in range(10):
        p = Paragraph()
        p.kind = "paragraph"
        p.value = f'This is paragraph number {x}'
        article.add_paragraph(p)

    publication.add_article(article)

    # Generate
    handler = IOHandler(Generator(app="This app", version=1.0), "hest")
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'output.json')

    with open(filename, 'w') as outfile:
        handler.write_json(publication, outfile)
    with open(filename, 'r') as json_file:
        hest: Wrapper = handler.read_json(json_file)

    print(hest.type)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
