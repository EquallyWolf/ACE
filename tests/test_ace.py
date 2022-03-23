from io import StringIO

import pytest
import tomli
from ace import __version__
from ace.inputs import CommandLineInput
from ace.outputs import CommandLineOutput


def test_version():
    with open("pyproject.toml", "rb") as f:
        assert __version__ == tomli.load(f)["tool"]["poetry"]["version"]


@pytest.mark.parametrize(
    "prompt,expected",
    [
        ("Enter your name", "Enter your name "),
        ("Enter your age:", "Enter your age: "),
        ("Email>", "Email> "),
        ("", ""),
        ("  ", ""),
        (None, ""),
        ("1.  ", "1. "),
        ("Select menu number: ", "Select menu number: "),
    ],
)
def test_get_command_line_input(prompt, expected, monkeypatch, capsys):
    text_input = CommandLineInput(prompt)
    monkeypatch.setattr("sys.stdin", StringIO("ABC"))

    output = text_input.get()

    assert capsys.readouterr().out == expected
    assert isinstance(output, str), "Should return a string"


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
