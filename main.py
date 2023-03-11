from ace.utils import Logger

ace_logger = Logger.from_toml(config_file_name="logs.toml", log_name="main")


def main(logger: Logger) -> None:
    with logger.log_context(
        "info",
        "Loading input and output objects.",
        "Finished loading input and output objects.",
    ):
        user_input = CommandLineInput(f"{Fore.CYAN}You:")
        ace_output = CommandLineOutput(f"{Fore.YELLOW}ACE:")

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

        from colorama import Fore
        from colorama import init as colorama_init

        from ace.ai.models import IntentClassifierModel, IntentClassifierModelConfig
        from ace.inputs import CommandLineInput
        from ace.intents import run_intent
        from ace.outputs import CommandLineOutput

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
