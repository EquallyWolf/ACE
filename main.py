import sys

from colorama import Fore, init as colorama_init

from ace import intents
from ace.inputs import CommandLineInput
from ace.net import IntentModel
from ace.outputs import CommandLineOutput

colorama_init(autoreset=True)


def main() -> None:
    """
    The entry point of the program.
    """
    user_input = CommandLineInput(f"{Fore.CYAN}You:")
    ace_output = CommandLineOutput(f"{Fore.YELLOW}ACE:")

    model = IntentModel()

    while True:

        text = user_input.get()

        match model.predict(text):
            case "unknown":
                ace_output.broadcast(intents.unknown())
            case "greeting":
                ace_output.broadcast(intents.greeting())
            case "goodbye":
                ace_output.broadcast(intents.goodbye())
                sys.exit("Exiting...")
            case "open_app":
                ace_output.broadcast(intents.open_app(text))
            case "close_app":
                ace_output.broadcast(intents.close_app(text))


if __name__ == "__main__":
    main()
