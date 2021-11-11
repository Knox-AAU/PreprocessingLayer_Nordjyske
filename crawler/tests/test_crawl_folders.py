from datetime import datetime, timezone
from queue import Queue
from unittest import mock

from crawler.crawl import Crawler


class PseudoDirEntry:
    def __init__(self, name, path, is_dir, stat):
        self.name = name
        self.path = path
        self._is_dir = is_dir
        self._stat = stat

    def is_dir(self):
        return self._is_dir

    def stat(self):
        return self._stat


@mock.patch("os.scandir")
@mock.patch.object(Crawler, "crawl_for_files_in_folders")
def test_crawl_folder_finds_target_dir(
    mock_crawl,
    mock_scandir,
):
    mock_scandir.side_effect = [
        [PseudoDirEntry("derp", "/derp/", True, None)],
        [PseudoDirEntry("2000-01-01-01", "/2000-01-01-01/", True, None)],
        [PseudoDirEntry("derp", "/derp/", False, None)],
    ]
    q = Queue()
    directory = ""

    crawler = Crawler()
    crawler.crawl_folders(
        q,
        directory,
        from_date=datetime(year=1000, month=1, day=1, tzinfo=timezone.utc),
        to_date=datetime(year=5000, month=1, day=1, tzinfo=timezone.utc),
    )

    mock_crawl.assert_called_once()


@mock.patch("os.scandir")
@mock.patch.object(Crawler, "crawl_for_files_in_folders")
def test_crawl_folder_finds_target_dir_in_daterange(
    mock_crawl,
    mock_scandir,
):
    mock_scandir.return_value = [
        PseudoDirEntry("1999-01-01-01", "/1999-01-01-01/", True, None),
        PseudoDirEntry("2000-02-01-01", "/2000-02-01-01/", True, None),
        PseudoDirEntry("2001-01-01-01", "/1999-01-01-01/", True, None),
    ]
    q = Queue()
    directory = ""

    crawler = Crawler()
    crawler.crawl_folders(
        q,
        directory,
        from_date=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc),
        to_date=datetime(year=2000, month=6, day=1, tzinfo=timezone.utc),
    )

    mock_crawl.assert_called_once()


@mock.patch("os.scandir")
@mock.patch.object(Crawler, "crawl_for_files_in_folders")
def test_crawl_folder_check_if_not_folder(
    mock_crawl,
    mock_scandir,
):
    mock_scandir.return_value = [
        PseudoDirEntry("1999-01-01-01", "/1999-01-01-01/", False, None),
        PseudoDirEntry("2000-02-01-01", "/2000-02-01-01/", False, None),
        PseudoDirEntry("2001-01-01-01", "/1999-01-01-01/", False, None),
    ]
    q = Queue()
    directory = ""

    crawler = Crawler()
    crawler.crawl_folders(
        q,
        directory,
        from_date=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc),
        to_date=datetime(year=2000, month=6, day=1, tzinfo=timezone.utc),
    )

    mock_crawl.assert_not_called()
