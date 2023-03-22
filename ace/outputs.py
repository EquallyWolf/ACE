"""
Contains functionality for providing output to the user via any source of output.

#### Classes:

Output:
    The base class for all types of outputs.

CommandLineOutput:
    An output object that provides output to the command line.

SpeechOutput:
    An output object that provides output via speech.

#### Functions: None
"""
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union

import pyttsx3

from ace.utils import Logger

logger = Logger.from_toml(config_file_name="logs.toml", log_name="outputs")

speech_engine = pyttsx3.init()
speech_engine.setProperty("rate", 170)
speech_engine.setProperty("voice", speech_engine.getProperty("voices")[0].id)


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


@dataclass
class SpeechOutput(Output):
    """
    Provides output to the user via speech.

    #### Parameters:

    prefix: str
        The prefix to display before the output.
        (Not used in this class.)

    pronunciation: dict[str, str]
        A dictionary of words to replace with their pronunciation.

    #### Methods:

    broadcast(message: str) -> None
        Send a message to the user via speech.
    """

    pronunciation: Union[dict[str, str], None] = None

    def broadcast(self, message: str) -> None:
        """
        Send a message to the user via speech.

        #### Parameters:

        message: str
            The message to send to the user.

        pronunciation: dict[str, str]
            A dictionary of words to replace with their pronunciation.

        #### Returns: None

        #### Raises: None
        """
        message = self._format_pronunciation(message)

        speech_engine.say(message)

        speech_engine.startLoop(False)
        speech_engine.iterate()

        logger.log("info", f"Sent speech output: {message}")

        speech_engine.endLoop()

    def _format_pronunciation(self, message: str) -> str:
        """
        Helper method to format the pronunciation of certain words.

        #### Parameters:

        message: str
            The message to format.

        #### Returns: str

        #### Raises: None
        """
        if not self.pronunciation:
            return message

        for word, pronunciation in self.pronunciation.items():
            message = re.sub(
                rf"\b{word}\b",
                pronunciation,
                message,
                flags=re.IGNORECASE,
            )

        return message
