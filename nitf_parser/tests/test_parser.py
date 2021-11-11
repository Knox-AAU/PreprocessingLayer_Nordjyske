from nitf_parser.parser import NitfParser


def test_sanitize_spaces_none():
    # noinspection PyTypeChecker
    assert NitfParser.sanitize_spaces(None) is None


def test_sanitize_spaces_spaces():
    assert (
        NitfParser.sanitize_spaces(
            "   hello this is a    string with iregular    spaces."
        )
        == "hello this is a string with iregular spaces."
    )


def test_sanitize_spaces_newline():
    assert (
        NitfParser.sanitize_spaces("\n\nhello\nthis\n\nis\na\n\n\nstring")
        == "hello this is a string"
    )


def test_sanitize_spaces_return():
    assert (
        NitfParser.sanitize_spaces("\rhello\r\r\rthis\ris\r\ra\rstring")
        == "hello this is a string"
    )


def test_sanitize_spaces_tabs():
    assert (
        NitfParser.sanitize_spaces("\t\thello\tthis\tis\ta\t\tstring")
        == "hello this is a string"
    )


def test_sanitize_spaces_mixed():
    assert (
        NitfParser.sanitize_spaces(
            "   hello this\t is\n\r\t a   \t string with \niregular    spaces."
        )
        == "hello this is a string with iregular spaces."
    )
