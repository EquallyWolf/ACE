import pytest
import tomli
from ace import __version__
from ace.outputs import CommandLineOutput


def test_version():
    with open("pyproject.toml", "rb") as f:
        assert __version__ == tomli.load(f)["tool"]["poetry"]["version"]


@pytest.mark.parametrize(
    "prefix,message,expected",
    [
        ("ACE:", "Hello", "ACE: Hello\n"),
        ("", "Hello", "Hello\n"),
        (None, "Hello", "Hello\n"),
        ("", "", "\n"),
        (">", "Hello world!", "> Hello world!\n"),
        ("  ", "Spaces are trimmed", "Spaces are trimmed\n"),
    ],
)
def test_broadcast_command_line_output(prefix, message, expected, capsys):
    text_output = CommandLineOutput(prefix)
    text_output.broadcast(message)

    assert capsys.readouterr().out == expected
