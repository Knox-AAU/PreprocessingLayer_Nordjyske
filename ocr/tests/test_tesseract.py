from unittest import mock

from ocr.tesseract import TesseractModule


@mock.patch("pytesseract.image_to_data")
def test_tesseract_constructor(mock_pytesseract):
    mock_pytesseract.return_value = {"text": [], "conf": []}


@mock.patch("pytesseract.image_to_data")
def test_tesseract_conf_matches(mock_pytesseract):
    mock_pytesseract.return_value = {"text": ["hej", "dav"], "conf": [1, 0.5]}

    tm = TesseractModule(None)

    text_conf_matches = tm.text_conf_matches_from_tesseract_data()

    assert len(text_conf_matches) == 2
    assert text_conf_matches[0] == ["hej", 1]
    assert text_conf_matches[1] == ["dav", 0.5]


@mock.patch("pytesseract.image_to_data")
def test_tesseract_average_conf(mock_pytesseract):
    mock_pytesseract.return_value = {"conf": [100, 50, 0, 33, 65, 120, -1]}

    tm = TesseractModule(None)

    average_conf = tm.get_average_conf()

    assert average_conf == 49.6


@mock.patch("pytesseract.image_to_data")
def test_tesseract_average_conf_no(mock_pytesseract):
    mock_pytesseract.return_value = {"conf": []}

    tm = TesseractModule(None)

    average_conf = tm.get_average_conf()

    assert average_conf == 0


@mock.patch("pytesseract.image_to_data")
def test_tesseract_text(mock_pytesseract):
    mock_pytesseract.return_value = {
        "text": ["hej", "dav", "du"],
    }

    tm = TesseractModule(None)

    paragraphs = tm.to_paragraphs()

    assert len(paragraphs) == 1
    assert paragraphs[0].value == "hej dav du"


@mock.patch("pytesseract.image_to_data")
def test_tesseract_paragraphs_split(mock_pytesseract):
    mock_pytesseract.return_value = {
        "text": ["hej", "", "", "dav", "du"],
    }

    tm = TesseractModule(None)
    tm.data["text"] = ["", "", "", "", "hej", "", "", "dav", "du"]

    paragraphs = tm.to_paragraphs()

    assert len(paragraphs) == 2
    assert paragraphs[0].value == "hej"
    assert paragraphs[1].value == "dav du"
