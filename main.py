from ace.inputs import CommandLineInput
from ace.outputs import CommandLineOutput
from ace.net import IntentModel


def main() -> None:
    """
    The entry point of the program.
    """
    user_input = CommandLineInput("You:")
    ace_output = CommandLineOutput("ACE:")

    model = IntentModel()

    while True:

        match model.predict(user_input.get()):
            case "unknown":
                ace_output.broadcast("Sorry, I don't know what you mean.")
            case "greeting":
                ace_output.broadcast("Hello!")
            case "goodbye":
                ace_output.broadcast("Goodbye!")
                quit()


if __name__ == "__main__":
    main()
