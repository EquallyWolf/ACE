from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import StringIO
from ace import __version__
import tomli


@dataclass
class Input(ABC):
    prompt: str = ""

    @abstractmethod
    def get(self) -> str:
        """Return an input from the user as a string, given a prompt."""
        pass


class TextInput(Input):
    def get(self) -> str:
        return input(f"{self.prompt} ")


def test_version():
    with open("pyproject.toml", "rb") as f:
        assert __version__ == tomli.load(f)["tool"]["poetry"]["version"]


def test_get_text_input_with_prompt(monkeypatch):
    text_input = TextInput("Enter your name:")
    assert text_input.prompt == "Enter your name:"
    monkeypatch.setattr("sys.stdin", StringIO("John Doe"))
    assert isinstance(text_input.get(), str), "Should return a string"


def test_get_text_input_without_prompt(monkeypatch):
    text_input = TextInput()
    assert text_input.prompt == ""
    monkeypatch.setattr("sys.stdin", StringIO("John Doe"))
    assert isinstance(text_input.get(), str), "Should return a string"
