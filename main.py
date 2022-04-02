from ace.inputs import CommandLineInput
from ace.outputs import CommandLineOutput
from ace.net import predict


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
            case "greeting":
                ace_output.broadcast("Hello!")


if __name__ == "__main__":
    main()
