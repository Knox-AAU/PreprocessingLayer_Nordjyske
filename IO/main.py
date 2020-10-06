from models.article import *
from IOHandler import *


def print_hi(name):
    article = Article()
    article.title = "En god artikel"
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
        article.addParagraph(p)

    # print(article.paragraphs)

    # out = wrapper.toJSON()
    # Use a breakpoint in the code line below to debug your script.
    # print(out)  # Press ⌘F8 to toggle the breakpoint.

    handler = IOHandler(Generator(app="This app", version=1.0), "hest")
    handler.Export(article, "/Users/tlorentzen/Documents/GitHub/SW517e20/output.json")
    hest: Wrapper = handler.Import("/Users/tlorentzen/Documents/GitHub/SW517e20/output.json")

    # h = Wrapper(hest)

    print(hest.type)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
