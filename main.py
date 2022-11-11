import sys

from colorama import Fore
from colorama import init as colorama_init

from ace.ai.models import IntentClassifierModel, IntentClassifierModelConfig
from ace.inputs import CommandLineInput
from ace.intents import run_intent
from ace.outputs import CommandLineOutput

colorama_init(autoreset=True)


def main() -> None:
    user_input = CommandLineInput(f"{Fore.CYAN}You:")
    ace_output = CommandLineOutput(f"{Fore.YELLOW}ACE:")

    model = IntentClassifierModel(IntentClassifierModelConfig.from_toml())

    while True:

        text = user_input.get()

        output = run_intent(model.predict(text), text)
        ace_output.broadcast(output[0])

        if output[1]:
            sys.exit("Exiting...")


if __name__ == "__main__":
    main()
