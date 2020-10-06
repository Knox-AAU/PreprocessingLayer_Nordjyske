from models.article import *
from IOHandler import *
import json


def print_hi(name):
    wrapper = Wrapper()
    wrapper.generator = Generator(app="This app", version=1.0)
    wrapper.schemaLocation = "https://google.dk"
    wrapper.schemaVersion = 1.0
    wrapper.type = Type.ARTICLE.value

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

    wrapper.setContent(article)

    out = wrapper.toJSON()
    # Use a breakpoint in the code line below to debug your script.
    print(out)  # Press ⌘F8 to toggle the breakpoint.

    handler = IOHandler(Generator(app="This app", version=1.0), "hest")
    handler.Export(wrapper, "/Users/tlorentzen/Documents/GitHub/SW517e20/output.json")
    hest = handler.Import("/Users/tlorentzen/Documents/GitHub/SW517e20/output.json")
    print(type(hest))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
