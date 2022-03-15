from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Input(ABC):
    prompt: str = ""

    @abstractmethod
    def get(self) -> str:
        """Return an input from the user as a string, given a prompt."""


class TextInput(Input):
    def get(self) -> str:
        return input(f"{self.prompt} ")
