import os
import platform

import tomli
import windowsapps

from ace.inputs import CommandLineInput
from ace.net import IntentModel
from ace.outputs import CommandLineOutput, Output


def main() -> None:
    """
    The entry point of the program.
    """
    user_input = CommandLineInput("You:")
    ace_output = CommandLineOutput("ACE:")

    model = IntentModel()

    while True:

        text = user_input.get()

        match model.predict(text):
            case "unknown":
                unknown(ace_output)
            case "greeting":
                greeting(ace_output)
            case "goodbye":
                goodbye(ace_output)
            case "open_app":
                open_app(ace_output, text)


def unknown(output: Output) -> None:
    output.broadcast("Sorry, I don't know what you mean.")


def greeting(output: Output) -> None:
    output.broadcast("Hello!")


def goodbye(output: Output) -> None:
    output.broadcast("Goodbye!")
    quit()


def open_app(output: Output, text: str) -> None:
    app_name = " ".join(text.split(" ")[1:])

    with open(os.path.join("config", "apps.toml"), "rb") as f:
        app_data = tomli.load(f)

    for app_id, aliases in app_data["aliases"].items():
        if app_name in aliases:
            app_name = app_id
            break

    match platform.system().lower():
        case "windows":
            try:
                windowsapps.open_app(app_name)
                output.broadcast(f"Opening '{app_name}'...")
            except FileNotFoundError:
                output.broadcast(f"Sorry, I can't open '{app_name}'. Is it installed?")
        case _:
            output.broadcast(
                f"Sorry, I don't know how to open '{app_name}' on this platform."
            )


if __name__ == "__main__":
    main()
