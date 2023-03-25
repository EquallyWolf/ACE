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

ace_logger = Logger.from_toml(config_file_name="logs.toml", log_name="main")


def main(logger: Logger) -> None:
    """
    This is the main function of the ACE program. It is responsible for
    initializing the input and output objects, loading the intent classifier
    model, and running the main loop.

    #### Parameters:

    logger: Logger
        The logger object to use for logging.

    #### Returns: None

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
        user_input = CommandLineInput(f"{Fore.CYAN}You:")
        ace_outputs = [
            CommandLineOutput(f"{Fore.YELLOW}ACE:"),
            SpeechOutput(pronunciation=pronunciations),
        ]

    with logger.log_context(
        "info",
        "Loading intent classifier model.",
        "Finished loading intent classifier model.",
    ):
        model = IntentClassifierModel(IntentClassifierModelConfig.from_toml())

    logger.log("info", "Starting main loop.")
    while True:

        try:
            text = user_input.get()
        except EOFError:
            text = ""

        logger.log("info", f"Received input: {text}")

        intent = model.predict(text)
        logger.log("info", f"Predicted intent: {intent}")

        output = run_intent(intent, text)
        for ace_output in ace_outputs:
            ace_output.broadcast(output[0])

        if output[1]:
            break

    logger.log("info", f"Exited ACE successfully with intent: {intent}")

    sys.exit("Exiting ACE...")


if __name__ == "__main__":

    with ace_logger.log_context(
        "info",
        "Importing modules in 'ace.py'",
        "Finished importing modules.",
    ):

        import sys

        import toml
        from colorama import Fore
        from colorama import init as colorama_init

        from ace.ai.models import IntentClassifierModel, IntentClassifierModelConfig
        from ace.inputs import CommandLineInput
        from ace.intents import run_intent
        from ace.outputs import CommandLineOutput, SpeechOutput

    colorama_init(autoreset=True)

    try:
        ace_logger.log("info", "Starting ACE.")
        main(ace_logger)

    except KeyboardInterrupt:
        print(f"{Fore.RESET}")
        ace_logger.log("info", "Exited ACE with keyboard interrupt.", exc_info=True)

    except Exception as e:
        print(f"{Fore.RESET}")
        ace_logger.log(
            "critical",
            f"Exited ACE with exception: {e.__class__.__name__}.",
            exc_info=True,
        )
        raise e
