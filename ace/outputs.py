"""
Contains functionality for providing output to the user via any source of output.

#### Classes:

Output:
    The base class for all types of outputs.

CommandLineOutput:
    An output object that provides output to the command line.

#### Functions: None
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ace.utils import Logger

logger = Logger.from_toml(config_file_name="logs.toml", log_name="outputs")


@dataclass
class Output(ABC):
    """
    The base class for all types of outputs.

    Provides a common interface for providing output to the user
    via any source of output.

    #### Parameters:

    prefix: str
        The prefix to display before the output.

    #### Methods:

    broadcast(message: str) -> None
        Send a message to the user via the output.
    """

    prefix: str = None

    @abstractmethod
    def broadcast(self, message: str) -> None:
        """
        Send a message to the user via the output.
        """


class CommandLineOutput(Output):
    """
    Provides output to the command line.

    #### Parameters:

    prefix: str
        The prefix to display before the output.

    #### Methods:

    broadcast(message: str) -> None
        Send a message to the user via the command line.
    """

    def broadcast(self, message: str) -> None:
        """
        Send a message to the user via the command line.

        #### Parameters:

        message: str
            The message to send to the user.

        #### Returns: None

        #### Raises: None
        """
        if self._prefix_empty():
            print(message)
        else:
            print(f"{self.prefix.rstrip()} {message}")

        logger.log("info", f"Sent command line output: {message}")

    def _prefix_empty(self) -> bool:
        """
        Helper method to check if the prefix is empty or only contains whitespace.

        #### Parameters: None

        #### Returns: bool

        #### Raises: None
        """
        return not self.prefix or self.prefix.replace(" ", "") == ""
