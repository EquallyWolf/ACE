"""
Welcome to the ACE program!
----------------------------

ACE, the Artificial Consciousness Engine, is a digital assistant.

It is designed to help you with your daily tasks and keep you in
the loop with your life and the world.

#### Classes: None

#### Functions:

main:
    This is the main function of the ACE program. It is responsible for
    initializing the input and output objects, loading the intent classifier
    model, and running the main loop.
"""

from ace.utils import Logger

logger = Logger.from_toml(config_file_name="logs.toml", log_name="main")

with logger.log_context(
    "info",
    "Importing modules in 'ace.py'",
    "Finished importing modules.",
):

    import sys

    import toml
    from colorama import Fore
    from colorama import init as colorama_init

    from ace.ai.models import IntentClassifierModel, IntentClassifierModelConfig
    from ace.inputs import CommandLineInput, Input
    from ace.intents import run_intent
    from ace.outputs import CommandLineOutput, Output, SpeechOutput

colorama_init(autoreset=True)


def main() -> None:
    """
    This is the main function of the ACE program. It is responsible for
    initializing the input and output objects, loading the intent classifier
    model, and running the main loop.

    #### Parameters: None

    #### Returns: None

    #### Raises: None
    """

    inputs, outputs = _create_io_objects()

    model = _load_intent_model()

    logger.log("info", "Starting main loop.")
    while True:

        text = _get_input(inputs[0])
        logger.log("info", f"Received input: {text}")

        intent = model.predict(text)
        logger.log("info", f"Predicted intent: {intent}")

        output = run_intent(intent, text)
        for ace_output in outputs:
            ace_output.broadcast(output[0])

        if output[1]:
            break

    logger.log("info", f"Exited ACE successfully with intent: {intent}")

    sys.exit("Exiting ACE...")


def _create_io_objects() -> tuple[list[Input], list[Output]]:
    """
    Create the input and output objects for the ACE program.

    #### Parameters: None

    #### Returns: tuple[list[Input], list[Output]]
        A tuple containing a list of input objects and a list of output objects.

    #### Raises: None
    """
    with logger.log_context(
        "info",
        "Loading pronunciations.",
        "Finished loading pronunciations.",
    ):
        pronunciations = toml.load("config/diction.toml")["pronunciations"]

    with logger.log_context(
        "info",
        "Loading input and output objects.",
        "Finished loading input and output objects.",
    ):
        inputs = [CommandLineInput(f"{Fore.CYAN}You:")]
        outputs = [
            CommandLineOutput(f"{Fore.YELLOW}ACE:"),
            SpeechOutput(pronunciation=pronunciations),
        ]

    return inputs, outputs  # type: ignore


def _load_intent_model() -> IntentClassifierModel:
    with logger.log_context(
        "info",
        "Loading intent classifier model.",
        "Finished loading intent classifier model.",
    ):
        return IntentClassifierModel(IntentClassifierModelConfig.from_toml())


def _get_input(input: Input) -> str:
    """
    Get input from the user.

    #### Parameters:

    input: Input
        The input object to use to obtain input from the user.

    #### Returns: str
        The input from the user.

    #### Raises: None
    """
    try:
        return input.get()
    except EOFError:
        return ""


if __name__ == "__main__":
    try:
        logger.log("info", "Starting ACE.")
        main()

    except KeyboardInterrupt:
        print(f"{Fore.RESET}")
        logger.log("info", "Exited ACE with keyboard interrupt.", exc_info=True)

    except Exception as e:
        print(f"{Fore.RESET}")
        logger.log(
            "critical",
            f"Exited ACE with exception: {e.__class__.__name__}.",
            exc_info=True,
        )
        raise e
