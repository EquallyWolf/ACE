from ace.inputs import CommandLineInput
from ace.outputs import CommandLineOutput


def predict(text: str) -> str:
    """
    Predict the intent of the given text.

    returns: The predicted intent.
    """
    return "unknown"


def main() -> None:
    """
    The entry point of the program.
    """
    user_input = CommandLineInput("You:")
    ace_output = CommandLineOutput("ACE:")

    while True:
        prediction = predict(user_input.get())

        match prediction:
            case "unknown":
                ace_output.broadcast("Sorry, I don't know what you mean.")


if __name__ == "__main__":
    main()
