from io import StringIO

import tomli
from ace import __version__
from ace.inputs import TextInput


def test_version():
    with open("pyproject.toml", "rb") as f:
        assert __version__ == tomli.load(f)["tool"]["poetry"]["version"]


def test_get_text_input_with_prompt(monkeypatch):
    # Create a TextInput object with a prompt
    text_input = TextInput("Enter your name:")
    assert text_input.prompt == "Enter your name:"

    # Mock user input to return "John Doe"
    monkeypatch.setattr("sys.stdin", StringIO("John Doe"))
    assert isinstance(text_input.get(), str), "Should return a string"


def test_get_text_input_without_prompt(monkeypatch):
    # Create a TextInput object without a prompt
    text_input = TextInput()
    assert text_input.prompt == ""

    # Mock user input to return "John Doe"
    monkeypatch.setattr("sys.stdin", StringIO("John Doe"))
    assert isinstance(text_input.get(), str), "Should return a string"
