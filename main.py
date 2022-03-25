from ace.inputs import CommandLineInput
from ace.outputs import CommandLineOutput


def predict(text: str) -> str:
    """
    Predict the intent of the given text.

    returns: The predicted intent.
    """
    return "I do not understand."


def main() -> None:
    """
    The entry point of the program.
    """
    user_input = CommandLineInput("You:")
    ace_output = CommandLineOutput("ACE:")

    while True:
        prediction = predict(user_input.get())
        ace_output.broadcast(prediction)


if __name__ == "__main__":
    main()
