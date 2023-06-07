from abc import ABC, abstractmethod

import toml
from colorama import Fore
from colorama import init as colorama_init

from ace.ai.models import IntentClassifierModel, IntentClassifierModelConfig
from ace.inputs import CommandLineInput, Input
from ace.intents import run_intent
from ace.outputs import CommandLineOutput, Output, SpeechOutput
from ace.utils import Logger

colorama_init(autoreset=True)

logger = Logger.from_toml(config_file_name="logs.toml", log_name="interfaces")


class Interface(ABC):  # pragma: no cover
    """
    A base class for all interfaces, which are the different ways to
    interact with ACE.

    ### Parameters:

    show_header (bool): (default: True)
        Whether to show the start information to the user.

    header (str): (default: "")
        The header to show to the user.

    ### Properties:

    config (dict):
        The configuration for the interface.

    intent_classifier (IntentClassifierModel):
        The intent classifier model.

    show_header (bool):
        Whether to show the start information to the user.

    header (str):
        The start information to show the user.

    input (Input):
        The input to the interface.

    outputs (list[Output]):
        The outputs to the interface.

    header_outputs (list[Output]):
        The output types to use for the header.

    ### Methods:

    run():
        Start the main loop of the interface.

    create_input():
        Method to create an input to the interface.

    create_outputs():
        Method to create outputs to the interface.

    show_header():
        Method to display the start information to the user.

    get_intent():
        Method to get the text from the user and determine the intent.
    """

    def __init__(self, show_header: bool, header: str = "") -> None:
        self._config = toml.load("config/main.toml")["interfaces"].get(
            self.__class__.__name__.lower(), {}
        )
        self._intent_classifier = self._create_intent_classifier()
        self._show_header = show_header
        self._header = header
        self._input = self.create_input()
        self._outputs = self.create_outputs()
        self._header_outputs = self.create_header_outputs()

    @property
    def config(self) -> dict:
        """
        The configuration for the interface.

        ### Returns: dict
            The configuration.
        """
        return self._config

    @property
    def intent_classifier(self) -> IntentClassifierModel:
        """
        The intent classifier model.

        ### Returns: IntentClassifierModel
            The intent classifier model.
        """
        return self._intent_classifier

    @property
    def show_header(self) -> bool:
        """
        Whether to show the start information to the user.

        ### Returns: bool
            Whether to show the start information to the user.
        """
        return self._show_header

    @property
    def header(self) -> str:
        """
        The start information to show the user.

        ### Returns: str
            The header.
        """
        return self._header

    @header.setter
    def header(self, header: str) -> None:
        """
        Set the start information to show to the user.

        ### Parameters:

        header (str):
            The header to show to the user.

        ### Returns: None
        """
        self._header = header

    @property
    def input(self) -> Input:
        """
        The input to the interface.

        ### Returns: Input
            The input.
        """
        return self._input

    @property
    def outputs(self) -> list[Output]:
        """
        The outputs to the interface.

        ### Returns: list[Output]
            The outputs.
        """
        return self._outputs

    @property
    def header_outputs(self) -> list[Output]:
        """
        The output types to use for the header.

        ### Returns: list[Output]
            The outputs.
        """
        return self._header_outputs

    @abstractmethod
    def run(self) -> None:
        """
        Start the main loop of the interface.

        ### Parameters: None

        ### Returns: None

        ### Raises: NotImplementedError
            If the method is not implemented in the child class.
        """
        raise NotImplementedError

    @abstractmethod
    def create_input(self) -> Input:
        """
        Method to create an input to the interface.

        ### Parameters: None

        ### Returns: Input
            The input.

        ### Raises: NotImplementedError

        """
        raise NotImplementedError

    @abstractmethod
    def create_outputs(self) -> list[Output]:
        """
        Method to create outputs to the interface.

        ### Parameters: None

        ### Returns: list[Output]
            The outputs.

        ### Raises: NotImplementedError
        """
        raise NotImplementedError

    @abstractmethod
    def create_header_outputs(self) -> list[Output]:
        """
        Method to create the outputs for the header.

        ### Parameters: None

        ### Returns: list[Output]
            The outputs.

        ### Raises: NotImplementedError
        """
        raise NotImplementedError

    @abstractmethod
    def display_header(self) -> None:
        """
        Method to display the header of the interface.

        ### Parameters: None

        ### Returns: None

        ### Raises: NotImplementedError
        """
        raise NotImplementedError

    @abstractmethod
    def get_intent(self) -> tuple[str, str]:
        """
        Method to get the text from the user and determine the intent.

        ### Parameters: None

        ### Returns: tuple[str, str]
            The intent and the text from the user.

        ### Raises: NotImplementedError
        """
        raise NotImplementedError

    def _create_intent_classifier(self) -> IntentClassifierModel:
        """
        Helper method to create an intent classifier model.

        ### Returns: IntentClassifierModel
            The intent classifier model.

        """
        with logger.log_context(
            "info",
            "Loading intent classifier model.",
            "Finished loading intent classifier model.",
        ):
            config = IntentClassifierModelConfig.from_toml()
            return IntentClassifierModel(config=config)


class CLI(Interface):
    """
    Interact with ACE through the command line.

    ### Parameters:

    show_header (bool): (default: True)
        Whether to show the start information to the user.

    header (str): (default: "")
        The start information to show the user.

    ### Methods:

    run():
        Start the main loop of the command line interface (CLI) to get the user input, predict
        and run the intent, and broadcast the output.
    """

    output_map = {
        "text": CommandLineOutput(f"{Fore.YELLOW}ACE:"),
        "speech": SpeechOutput(),
    }

    def __init__(self, show_header: bool, header: str = "") -> None:
        super().__init__(show_header=show_header, header=header)

    def create_input(self) -> Input:
        """
        Function to create an input object based on the input type.

        Default is the command line input.

        ### Parameters: None

        ### Returns: Input
            The input object.

        ### Raises: ValueError
            If the input type is invalid.

        """
        with logger.log_context(
            "info",
            "Loading input object.",
            "Finished loading input object.",
        ):
            input_map = {
                "text": CommandLineInput(f"{Fore.CYAN}You:"),
            }

            inputs = [
                input_map[input_type]
                for input_type in self._config["input"]
                if input_type
            ]

            return inputs[0] if len(inputs) == 1 else input_map["text"]

    def create_outputs(self) -> list[Output]:
        """
        Helper function to create an output object based on the output type.

        Default is the command line output.

        ### Parameters: None

        ### Returns: Output
            The output object.

        ### Raises: ValueError
            If the output type is invalid.

        """

        with logger.log_context(
            "info",
            "Loading output objects.",
            "Finished loading output objects.",
        ):
            outputs = [
                self.output_map[output_type]
                for output_type, use_output in self.config["outputs"].items()
                if use_output
            ]

            return outputs or [CommandLineOutput(f"{Fore.YELLOW}ACE:")]

    def create_header_outputs(self) -> list[Output]:
        """
        Helper function to create an output object based on the output type.

        Default is the command line output.

        ### Parameters: None

        ### Returns: Output
            The output object.

        ### Raises: ValueError
            If the output type is invalid.

        """

        with logger.log_context(
            "info",
            "Loading output objects.",
            "Finished loading output objects.",
        ):
            outputs = [
                self.output_map[output_type]
                for output_type, use_output in self.config["headers"].items()
                if use_output
            ]

            return outputs or [CommandLineOutput(f"{Fore.YELLOW}ACE:")]

    def run(self) -> None:  # pragma: no cover
        """
        Start the main loop of the CLI to get the user input, predict
        and run the intent, and broadcast the output.

        ### Parameters None

        ### Returns: None
        """
        self.display_header()

        while True:
            output = run_intent(*self.get_intent())

            for _output in self.outputs:
                _output.broadcast(output[0])

            if output[1]:
                break

    def display_header(self) -> None:
        """
        Method to display the start information to the user.

        ### Parameters: None

        ### Returns: None

        ### Raises: None
        """
        if self.show_header:
            for output in self.header_outputs:
                _prefix = output.prefix
                output.prefix = ""

                output.broadcast(self.header)

                output.prefix = _prefix

    def get_intent(self, *args, **kwargs) -> tuple[str, str]:
        """
        Method to get the text from the user and determine the intent.

        ### Parameters:

        *args, **kwargs:
            Arguments to pass to help get the input from the user.

        ### Returns: tuple[str, str]
            The intent and the text from the user.

        ### Raises: None
        """
        text = self.input.get()
        logger.log("info", f"Received input: {text}")

        intent = self.intent_classifier.predict(text)
        logger.log("info", f"Predicted intent: {intent}")

        return intent, text
