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


def test_broadcast_command_line_output_with_prefix(capsys):
    # Create a CommandLineOutput object
    text_output = CommandLineOutput("ACE")
    assert text_output.prefix == "ACE"

    # Mock display output as "ACE: Hello World"
    text_output.broadcast("Hello World")
    assert capsys.readouterr().out == "ACE: Hello World\n"


def test_broadcast_command_line_output_without_prefix(capsys):
    # Create a CommandLineOutput object
    text_output = CommandLineOutput()
    assert text_output.prefix is None

    # Mock display output as "Hello World"
    text_output.broadcast("Hello World")
    assert capsys.readouterr().out == "Hello World\n"
