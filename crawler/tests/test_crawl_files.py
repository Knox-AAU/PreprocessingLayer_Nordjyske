from queue import Queue
from unittest import mock

from crawler.crawl import Crawler
from crawler.file_types import FileType
from crawler.folder import Folder
from crawler.tests.test_crawl_folders import PseudoDirEntry


@mock.patch("os.scandir")
@mock.patch.object(Crawler, "is_file_valid_nitf")
def test_crawl_files_nitf(mock_valid_nitf, mock_scandir, ):
    mock_valid_nitf.side_effect = [True, False]

    mock_scandir.side_effect = [
        [PseudoDirEntry("SomeNitfFile.xml", "SomeNitfFile.xmlPath", False, None)],
        [PseudoDirEntry("SomeInvalidNitfFile.xml", "SomeInvalidNitfFile.xmlPath", False, None)],
    ]
    q = Queue()
    directory = ""

    crawler = Crawler()
    folder = Folder("", 1, 1, 1)
    crawler.crawl_for_files_in_folders(folder, "")

    assert len(folder.files) == 1
    assert folder.files[0].name == "SomeNitfFile.xml"
    assert folder.files[0].type == FileType.NITF

@mock.patch("os.scandir")
def test_crawl_files_jp2(mock_scandir, ):

    mock_scandir.side_effect = [
        [PseudoDirEntry("SomeImageFile.jp2", "SomeNitfFile.xmlPath", False, None)],
        [PseudoDirEntry("SomeNotJp2File.txt", "SomeInvalidNitfFile.xmlPath", False, None)],
    ]

    crawler = Crawler()
    folder = Folder("", 1, 1, 1)
    crawler.crawl_for_files_in_folders(folder, "")

    assert len(folder.files) == 1
    assert folder.files[0].name == "SomeImageFile.jp2"
    assert folder.files[0].type == FileType.JP2

@mock.patch("os.scandir")
def test_crawl_files_recursive(mock_scandir):

    mock_scandir.side_effect = [
        [PseudoDirEntry("folder", "/folder/", True, None)],
        [PseudoDirEntry("SomeImageFile.jp2", "SomeNitfFile.xmlPath", False, None)],
    ]

    crawler = Crawler()
    folder = Folder("", 1, 1, 1)
    crawler.crawl_for_files_in_folders(folder, "")

    assert len(folder.files) == 1
    assert folder.files[0].name == "SomeImageFile.jp2"

@mock.patch("os.scandir")
def test_crawl_files_whitelist(mock_scandir):

    mock_scandir.return_value = [
        PseudoDirEntry("SomeTest.jp2", "", False, None),
        PseudoDirEntry("SomeImage.jp2", "", False, None),
        PseudoDirEntry("SomeFile.jp2", "", False, None),
    ]

    crawler = Crawler()

    crawler.whitelist = ["File","Test"]
    crawler.blacklist = []

    folder = Folder("", 1, 1, 1)
    crawler.crawl_for_files_in_folders(folder, "")

    assert len(folder.files) == 2
    assert next(filter(lambda file: file.name == "SomeTest.jp2", folder.files), None) is not None
    assert next(filter(lambda file: file.name == "SomeFile.jp2", folder.files), None) is not None

