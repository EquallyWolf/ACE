from ace.inputs import CommandLineInput
from ace.outputs import CommandLineOutput


def main() -> None:
    """
    The entry point of the program.
    """
    user_input = CommandLineInput("You:")
    ace_output = CommandLineOutput("ACE:")

    while True:
        ace_output.broadcast(f"You said '{user_input.get()}'")


if __name__ == "__main__":
    main()
