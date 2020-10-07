from models.article import *
from IOHandler import *
import os


def print_hi(name):
    article = Article()
    article.headline = "En god artikel"
    article.subhead = ""
    article.lead = ""
    article.byline = Byline(name="Thomas", email="thomas@tlorentzen.net")
    article.extractedFrom.append("Some file")
    article.confidence = 1.0
    article.id = 6752342345
    article.page = 64
    article.publication = "Home made stuff"
    article.publisher = "Me"
    article.publishedAt = ""

    for x in range(10):
        p = Paragraph()
        p.kind = "paragraph"
        p.value = f'This is paragraph number {x}'
        article.add_paragraph(p)

    # print(article.paragraphs)

    # out = wrapper.toJSON()
    # Use a breakpoint in the code line below to debug your script.
    # print(out)  # Press ⌘F8 to toggle the breakpoint.

    handler = IOHandler(Generator(app="This app", version=1.0), "hest")
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'output.json')

    with open(filename, 'w') as outfile:
        handler.write_json(article, outfile)
    with open(filename, 'r') as json_file:
        hest: Wrapper = handler.read_json(json_file)

    # h = Wrapper(hest)

    print(hest.type)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

