import pandas as pd
import json
import os
import tkinter as tk
from abc import ABC, abstractmethod
from typing import Union

import customtkinter as ctk
import toml
from colorama import Fore
from colorama import init as colorama_init

from ace import __version__
from ace.ai.models import IntentClassifierModel, IntentClassifierModelConfig
from ace.inputs import CommandLineInput, Input
from ace.intents import run_intent
from ace.outputs import CommandLineOutput, Output, SpeechOutput
from ace.utils import Logger

colorama_init(autoreset=True)

logger = Logger.from_toml(config_file_name="logs.toml", log_name="interfaces")

COLOUR_SCHEMES = toml.load("config/main.toml")["colour_schemes"]


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
    def input(self) -> Union[Input, tk.Entry, ctk.CTkEntry]:
        """
        The input to the interface.

        ### Returns: Input
            The input.
        """
        return self._input

    @input.setter
    def input(self) -> Union[Input, tk.Entry, ctk.CTkEntry]:
        """
        The input to the interface.

        ### Returns: Input
            The input.
        """
        return self._input

    @property
    def outputs(self) -> list[Union[Output, tk.Text, ctk.CTkTextbox]]:
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
    def create_input(self) -> Union[Input, tk.Entry, ctk.CTkEntry]:
        """
        Method to create an input to the interface.

        ### Parameters: None

        ### Returns: Input
            The input.

        ### Raises: NotImplementedError

        """
        raise NotImplementedError

    @abstractmethod
    def create_outputs(self) -> list[Union[Output, tk.Text, ctk.CTkTextbox]]:
        """
        Method to create outputs to the interface.

        ### Parameters: None

        ### Returns: list[Union[Output, tk.Text, ctk.CTkTextbox]]
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
                if type(_output) == Output:
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


class GUI(Interface):
    """
    Interact with ACE through a graphical user interface (GUI).

    ### Parameters:

    show_header (bool): (default: True)
        Whether to show the start information to the user.

    header (str): (default: "")
        The start information to show the user.

    ### Methods:

    run():
        Start the main loop of the GUI to get the user input, predict
        and run the intent, and broadcast the output.
    """

    def __init__(self, show_header: bool, header: str = "") -> None:
        super().__init__(show_header=show_header, header=header)
        self._setup()
        self._speech_output = SpeechOutput()

    @property
    def valid_input_types(self) -> list[str]:
        """
        The valid input types for the GUI.

        ### Returns: list[str]
            The valid input types.
        """
        return ["text"]

    @property
    def root(self) -> Union[tk.Tk, ctk.CTk]:
        """
        The root application object for the GUI.

        ### Returns: Union[tk.Tk, ctk.CTk]
            The application object.
        """
        return self._root

    @property
    def chat_box(self) -> Union[tk.Text, ctk.CTkTextbox, None]:
        """
        The chat box for the GUI.

        ### Returns: Union[tk.Text, ctk.CTkTextbox]
            The chat box.
        """
        return self._chat_box

    @property
    def user_input(self) -> Union[tk.Entry, ctk.CTkEntry, None]:
        """
        The user input for the GUI.

        ### Returns: Union[tk.Entry, ctk.CTkEntry]
            The user input.
        """
        return self._user_input

    @property
    def send_button(self) -> Union[tk.Button, ctk.CTkButton, None]:
        """
        The send button for the GUI.

        ### Returns: Union[tk.Button, ctk.CTkButton]
            The send button.
        """
        return self._send_button

    def create_root(self) -> None:
        """
        Create the main application object.

        ### Parameters: None

        ### Returns: None

        ### Raises: None
        """
        # Initialise the root object
        self._root = ctk.CTk()

        # Assign properties
        self._root.title("ACE - Artificial Conciousness Engine")
        self._root.geometry("400x500")
        self._root.resizable(width=False, height=False)

        # Change icon
        self._root.iconbitmap("assets/ACE.ico")

        # Bind keys
        self._root.bind("<Escape>", lambda _: self.root.destroy())

    def create_chat_box(self) -> None:
        """
        Create the chat box, which displays the conversation.

        ### Parameters: None

        ### Returns: None

        ### Raises: None
        """
        if self.config["outputs"]["text"]:
            self._chat_box = ctk.CTkTextbox(
                self.root,
                state=tk.DISABLED,
                wrap=tk.WORD,
            )
            self._chat_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            theme = COLOUR_SCHEMES.get(self.config["theme"], {})
            self._chat_box.tag_config("USER", foreground=theme.get("cyan", "cyan"))
            self._chat_box.tag_config("ACE", foreground=theme.get("yellow", "yellow"))
        else:
            self._chat_box = None

    def create_user_input(self) -> None:
        """
        Create the user input box, which allows the user to type in
        their message.

        ### Parameters: None

        ### Returns: None

        ### Raises: None
        """
        if self.config["input"]["text"]:
            self._user_input = ctk.CTkEntry(self.root)
            self._user_input.pack(fill=tk.X, padx=5, pady=5)
            self._user_input.insert(0, "Type here...")
            self._user_input.bind(
                "<FocusOut>",
                lambda _: self._user_input.insert(0, "Type here..."),  # type: ignore
            )
            self._user_input.bind(
                "<FocusIn>", lambda _: self._user_input.delete(0, tk.END)  # type: ignore
            )
            self._user_input.bind("<Return>", self._send_message)  # type: ignore
            self._input = self._user_input
        else:
            self._user_input = None

    def create_send_button(self) -> None:
        """
        Create the send button, which allows the user to send their
        message to get a response.

        ### Parameters: None

        ### Returns: None

        ### Raises: None
        """
        if self.config["input"]["text"]:
            self._send_button = ctk.CTkButton(
                self.root,
                text="Send",
                command=self._send_message,
            )
            self._send_button.pack(fill=tk.X, padx=5, pady=5)
        else:
            self._send_button = None
            self.root.geometry("400x80")

    def create_input(self) -> Union[Input, None]:
        """
        Not currently implemented for the GUI, as the input is
        created after the GUI is setup.
        """
        pass

    def create_outputs(self) -> Union[list[Output], None]:
        """
        Not currently implemented for the GUI, as the outputs are
        created after the GUI is setup.
        """
        pass

    def create_header_outputs(self) -> Union[list[Output], None]:
        """
        Not currently implemented for the GUI, as the header is
        displayed in the chat box.
        """
        pass

    def run(self) -> None:  # pragma: no cover
        """
        Start the main loop of the GUI to get the user input, predict
        and run the intent, and broadcast the output.
        """
        self.root.mainloop()
        logger.log("info", "Exited GUI.")

    def display_header(self) -> None:  # pragma: no cover
        """
        Method to display the start information to the user.

        ### Parameters: None

        ### Returns: None

        ### Raises: NotImplementedError
        """
        if self.show_header and self.config["headers"]["text"] and self.chat_box:
            self.chat_box.configure(state=tk.NORMAL)
            self.chat_box.insert(tk.END, f"{self.header}\n\n")
            self.chat_box.see(tk.END)
            self.chat_box.configure(state=tk.DISABLED)
            logger.log("info", f"Sent text output: {self.header}")

        if self.show_header and self.config["headers"]["speech"]:
            self._speech_output.broadcast(self.header)

    def get_intent(self, text: str) -> tuple[str, str]:
        """
        Method to get the text from the user and determine the intent.

        ### Parameters:

        text (str):
            The text from the user.

        ### Returns: tuple[str, str]
            The intent and the text from the user.

        ### Raises: NotImplementedError
        """
        logger.log("info", f"Received input: {text}")

        intent = self.intent_classifier.predict(text)
        logger.log("info", f"Predicted intent: {intent}")

        return intent, text

    def get_user_input(self, input_type: str = "text", prompt: str = "") -> str:
        """
        Obtain the input from a user via the provided input type,
        and return it as a string.

        #### Parameters:

        input_type (str): (default: "text")
            The type of input to obtain from the user.

        prompt (str): (default: "")
            The text that needs removing from the input.

        #### Returns: str
            The input from the user.

        #### Raises: ValueError
            If the input type is invalid.
        """
        if input_type not in self.valid_input_types:
            raise ValueError(
                f"Invalid input type: {input_type}. Valid input types are: {self.valid_input_types}"
            )
        if input_type == "text" and self.config["input"]["text"]:
            logger.log(
                "info", "Obtaining input from user via graphical user interface."
            )
            if self.user_input:
                return self.user_input.get().removeprefix(prompt)
        return ""

    def create_menu(self) -> None:
        """
        Create the menu bar.

        ### Parameters: None

        ### Returns: None

        ### Raises: None
        """
        # Create the menu bar object
        menu_bar = tk.Menu(self.root)

        # Need a menu with File and Help
        file_menu = tk.Menu(menu_bar, tearoff=0)
        save_menu = tk.Menu(file_menu, tearoff=0)
        help_menu = tk.Menu(menu_bar, tearoff=0)

        # Add the options to the menu
        save_menu.add_command(label="Text", command=lambda: self._save("txt"))
        save_menu.add_command(label="JSON", command=lambda: self._save("json"))
        save_menu.add_command(label="CSV", command=lambda: self._save("csv"))

        file_menu.add_cascade(label="Save", menu=save_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._close)

        help_menu.add_command(label="About", command=self._about)

        # Add the menus to the menu bar
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Add the menu bar to the root
        self.root.config(menu=menu_bar)

    def _setup(self) -> None:  # pragma: no cover
        """
        Helper method to create and place all widgets in the GUI, and
        set all the properties of the GUI.

        ### Parameters: None

        ### Returns: None

        ### Raises: None
        """

        with logger.log_context(
            "info",
            "Setting up GUI.",
            "Finished setting up GUI.",
        ):
            ctk.set_appearance_mode("system")

            # If the theme name json file exists then use that path,
            # else use the theme name as it is
            theme_file = f"assets/themes/{self.config['theme']}.json"
            ctk.set_default_color_theme(
                theme_file if os.path.exists(theme_file) else self.config["theme"]
            )

            self.create_root()

            self.create_menu()

            # Add the widgets
            self.create_chat_box()
            self.create_user_input()
            self.create_send_button()

            # Display the header
            self.root.after(500, self.display_header)

            # Focus on the user input
            if self.user_input:
                self.root.after(1000, self.user_input.focus_set)

    def _send_message(
        self, event: Union[tk.Event, None] = None
    ) -> None:  # pragma: no cover
        """
        Helper method to handle sending a message via the GUI.
        """
        logger.log("info", f"Sending message via event: {event}")
        self.send_button.configure(state=tk.DISABLED)  # type: ignore

        # Get the message from the user
        message = self.get_user_input("text", "You: ")

        self.user_input.delete(0, tk.END)  # type: ignore
        self.user_input.configure(state=tk.DISABLED)  # type: ignore
        self._broadcast_user_message(message)
        self.user_input.configure(state=tk.NORMAL)  # type: ignore

        # Wait and respond
        self.root.after(500, self._respond, event)
        self.send_button.configure(state=tk.NORMAL)  # type: ignore

    def _respond(self, event: Union[tk.Event, None] = None) -> None:  # pragma: no cover
        """
        Helper method to handle responding to a message via the GUI.
        """
        logger.log("info", f"Responding to message via event: {event}")
        chatbox_text = self.chat_box.get("1.0", tk.END)  # type: ignore
        messages = chatbox_text.split("\n\n")

        logger.log("debug", f"Messages: {messages}")
        message = messages[-2].replace("You: ", "")

        response = run_intent(*self.get_intent(message))
        self._broadcast_ace_message(response[0])

        if response[1]:
            self._close()

    def _broadcast_user_message(self, message: str) -> None:  # pragma: no cover
        """
        Helper method to show a message from the user in the GUI.

        ### Parameters:

        message (str):
            The message from the user.

        ### Returns: None

        ### Raises: None
        """
        if self.config["outputs"]["text"] and self.chat_box:
            self.chat_box.configure(state=tk.NORMAL)
            self.chat_box.insert(tk.END, f"You: {message}\n\n", tags="USER")  # type: ignore
            self.chat_box.see(tk.END)
            self.chat_box.configure(state=tk.DISABLED)
            logger.log("info", f"Sent text output: {message}")

    def _broadcast_ace_message(self, message: str) -> None:  # pragma: no cover
        """
        Helper method to show a message from ACE in the GUI.

        ### Parameters:

        message (str):
            The message from ACE.

        ### Returns: None

        ### Raises: None
        """
        if self.config["outputs"]["text"] and self.chat_box:
            self.chat_box.configure(state=tk.NORMAL)
            self.chat_box.insert(tk.END, f"ACE: {message}\n\n", tags="ACE")  # type: ignore
            self.chat_box.see(tk.END)
            self.chat_box.configure(state=tk.DISABLED)
            logger.log("info", f"Sent text output: {message}")

        if self.config["outputs"]["speech"]:
            self.root.after(50, self._speech_output.broadcast, message)

    def _close(self) -> None:  # pragma: no cover
        """
        Helper method to close the GUI.

        ### Parameters: None

        ### Returns: None

        ### Raises: None
        """
        if self.chat_box:
            self.chat_box.insert(tk.END, "Exiting...")
        self.root.after(1000, self.root.destroy)

    def _about(self) -> None:  # pragma: no cover
        """
        Helper method to show the about information.

        ### Parameters: None

        ### Returns: None

        ### Raises: None
        """
        about = "\n".join(
            [
                "ACE - Artificial Conciousness Engine\n",
                f"Version: {__version__}\n",
            ]
        )
        tk.messagebox.showinfo("About", about)  # type: ignore

    def _save(self, option: str = "txt") -> None:  # pragma: no cover
        """
        Helper method to save the conversation.

        ### Parameters:

        option (str): (default: "txt")
            The file type to save the conversation as.

        ### Returns: None

        ### Raises: None
        """
        if not self.chat_box:
            return
        message_dict = self._get_messages()

        file_types = {
            "txt": self._save_txt,
            "json": self._save_json,
            "csv": self._save_csv,
        }

        if file_name := tk.filedialog.asksaveasfilename(  # type: ignore
            filetypes=[(option.upper(), f".{option}")],
            defaultextension=f".{option}",
        ):
            file_types[option](file_name, message_dict)
            tk.messagebox.showinfo("Conversation Saved", f"Conversation saved to {file_name}")  # type: ignore

    def _get_messages(self):  # pragma: no cover
        """
        Helper method to get the messages from the chat box.

        ### Parameters: None

        ### Returns: dict[int, str]
            The dictionary of messages.

        ### Raises: None
        """
        message_dict = {
            idx: message.replace("\n", "")
            for idx, message in enumerate(self.chat_box.get("1.0", tk.END).split("\n\n"))  # type: ignore
            if message
        }

        # Remove empty lines
        for idx in list(message_dict.keys()):
            if not message_dict[idx]:
                message_dict.pop(idx)

        return message_dict

    def _save_txt(
        self, file_name: str, message_dict: dict[int, str]
    ) -> None:  # pragma: no cover
        """
        Helper method to save the conversation as a text file.

        ### Parameters:

        file_name (str):
            The name of the file to save the conversation to.

        message_dict (dict[int, str]):
            The dictionary of messages to save.

        ### Returns: None

        ### Raises: None
        """
        with open(file_name, "w") as f:
            f.write("\n\n".join(message_dict.values()))

    def _save_json(
        self, file_name: str, message_dict: dict[int, str]
    ) -> None:  # pragma: no cover
        """
        Helper method to save the conversation as a JSON file.

        ### Parameters:

        file_name (str):
            The name of the file to save the conversation to.

        message_dict (dict[int, str]):
            The dictionary of messages to save.

        ### Returns: None

        ### Raises: None
        """
        with open(file_name, "w") as f:
            json.dump(message_dict, f, indent=4)

    def _save_csv(
        self, file_name: str, message_dict: dict[int, str]
    ) -> None:  # pragma: no cover
        """
        Helper method to save the conversation as a CSV file.

        ### Parameters:

        file_name (str):
            The name of the file to save the conversation to.

        message_dict (dict[int, str]):
            The dictionary of messages to save.

        ### Returns: None

        ### Raises: None
        """
        df = pd.DataFrame.from_dict(message_dict, orient="index", columns=["message"])
        df.to_csv(file_name, index_label="idx", header=True)
