from io import StringIO

import tomli
from ace import __version__
from ace.inputs import CommandLineInput
from ace.outputs import CommandLineOutput


def test_version():
    with open("pyproject.toml", "rb") as f:
        assert __version__ == tomli.load(f)["tool"]["poetry"]["version"]


def test_get_command_line_input_with_prompt(monkeypatch):
    # Create a CommandLineInput object with a prompt
    text_input = CommandLineInput("Enter your name:")
    assert text_input.prompt == "Enter your name:"

    # Mock user input to return "John Doe"
    monkeypatch.setattr("sys.stdin", StringIO("John Doe"))
    assert isinstance(text_input.get(), str), "Should return a string"


def test_get_command_line_input_without_prompt(monkeypatch):
    # Create a CommandLineInput object without a prompt
    text_input = CommandLineInput()
    assert text_input.prompt == ""

    # Mock user input to return "John Doe"
    monkeypatch.setattr("sys.stdin", StringIO("John Doe"))
    assert isinstance(text_input.get(), str), "Should return a string"


def test_broadcast_command_line_output_with_prefix():
    # Create a CommandLineOutput object
    text_output = CommandLineOutput("ACE")
    assert text_output.prefix == "ACE"
