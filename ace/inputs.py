"""
Contains functionality for interacting with the user via any source of input.

#### Classes:

Input:
    The base class for all types of inputs.

CommandLineInput:
    An input object that obtains input from the command line.

#### Functions: None
"""

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

    #### Parameters:

    prompt: str
        The prompt to display to the user.

    #### Methods:

    get() -> str
        Obtain the input from a user and return it as a string.
    """

    prompt: str = ""

    @abstractmethod
    def get(self) -> str:
        """
        Obtain the input from a user and return it as a string.

        #### Parameters: None

        #### Returns: str
            The input from the user.
        """


class CommandLineInput(Input):
    """
    An input object that obtains input from the command line.

    #### Parameters:

    prompt: str
        The prompt to display to the user.

    #### Methods:

    get() -> str
        Obtain the input from a user via the command line and
        return it as a string.
    """

    def get(self) -> str:
        """
        Obtain the input from a user via the command line and
        return it as a string.

        #### Parameters: None

        #### Returns: str
            The input from the user.
        """
        logger.log("info", "Obtaining input from user via command line.")
        return input() if self._prompt_empty() else input(f"{self.prompt.rstrip()} ")

    def _prompt_empty(self) -> bool:
        """
        Helper method to determine if the prompt is empty.

        #### Parameters: None

        #### Returns: bool
            True if the prompt is empty, False otherwise.
        """
        return not self.prompt or self.prompt.replace(" ", "") == ""
