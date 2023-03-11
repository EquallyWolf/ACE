from abc import ABC, abstractmethod
from dataclasses import dataclass

from ace.utils import Logger

logger = Logger.from_toml(config_file_name="logs.toml", log_name="inputs")


@dataclass
class Input(ABC):
    """
    The base class for all types of inputs.

    Provides a common interface for interacting with the user
    via any source of input.

    Attributes
    ----------
    prompt: str
        The prompt to display to the user.
    """

    prompt: str = ""

    @abstractmethod
    def get(self) -> str:
        """
        Obtain the input from a user and return it as a string.
        """


class CommandLineInput(Input):
    """
    Class for retrieving input from the user via a command line.

    Attributes
    ----------
    prompt: str
        The prompt to display to the user.
    """

    def get(self) -> str:
        """
        Obtain the input from a user via the command line and
        return it as a string.

        returns: The input from the user.
        """
        logger.log("info", "Obtaining input from user via command line.")
        return input() if self._prompt_empty() else input(f"{self.prompt.rstrip()} ")

    def _prompt_empty(self) -> bool:
        """
        Determine if the prompt is empty.

        returns: True if the prompt is empty, False otherwise.
        """
        return not self.prompt or self.prompt.replace(" ", "") == ""
