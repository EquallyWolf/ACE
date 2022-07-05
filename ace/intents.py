import platform
import re
from collections import namedtuple
from typing import Callable

import ace.application as app
from ace.apis import WeatherAPI

DEGREES = "\N{DEGREE SIGN}"

app_factory = app.AppManagerFactory()
weather_api = WeatherAPI()

Intent = namedtuple("Intent", ["func", "should_exit", "requires_text"])
intent_funcs: dict[str, Intent] = {}


def _register(**kwargs) -> Callable:
    """
    A decorator that adds the function to the intent_funcs dictionary.

    ### **kwargs:

    should_exit: bool (default: False)
        Whether or not the application should exit after the intent is executed.

    requires_text: bool (default: False)
        Whether or not the intent requires text to be passed in.
    """

    def inner(func) -> Callable:
        intent_funcs[func.__name__] = Intent(
            func, kwargs.get("should_exit", False), kwargs.get("requires_text", False)
        )
        return func

    return inner


def run_intent(intent_name: str, *args, **kwargs) -> tuple[str, bool]:
    """
    Runs the function associated with the intent name.

    If the intent is not found, runs the default function "unknown".

    returns: tuple[str, bool]
        The response of the intent and whether or not the application should exit.
    """
    intent = intent_funcs.get(intent_name, "unknown")

    response = intent.func(*args, **kwargs) if intent.requires_text else intent.func()
    return response, intent.should_exit


@_register()
def unknown() -> str:
    return "Sorry, I don't know what you mean."


@_register()
def greeting() -> str:
    return "Hello!"


@_register(should_exit=True)
def goodbye() -> str:
    return "Goodbye!"


@_register(requires_text=True)
def open_app(text: str) -> str:
    app_name = " ".join(text.split(" ")[1:])

    current_platform = platform.system()

    try:
        manager = app_factory.create(current_platform)
    except KeyError:
        return f"Sorry, I don't know how to open apps on this platform ({current_platform})."

    try:
        manager.open(app_name)
        return f"Opening '{app_name}'..."
    except FileNotFoundError:
        return f"Sorry, I can't open '{app_name}'. Is it installed?"


@_register(requires_text=True)
def close_app(text: str) -> str:
    app_name = " ".join(text.split(" ")[1:])

    current_platform = platform.system()

    try:
        manager = app_factory.create(current_platform)
    except KeyError:
        return f"Sorry, I don't know how to close apps on this platform ({current_platform})."

    try:
        manager.close(app_name)
        return f"Closing '{app_name}'..."
    except FileNotFoundError:
        return f"Sorry, I can't close '{app_name}'. Is it running?"


@_register(requires_text=True)
def current_weather(text: str) -> str:
    stop_words = [
        "current weather in",
        "get current weather",
        "current weather conditions",
        "current weather",
        "get weather in",
        "weather in",
        " in ",
        " in",
        "in ",
    ]

    if response := weather_api.get_current_weather(
        re.sub("|".join(stop_words), "", text, flags=re.IGNORECASE).replace(" ", "")
    ):

        if response["code"] == "200":

            unit = f"{DEGREES}{response['temp']['units']}"

            return f"The weather in {response['location']} is {response['temp']['current']}{unit} and {response['condition']}."

        elif response["code"] == "401":
            return "The configured weather API key is invalid. Please check the 'ACE_WEATHER_KEY' environment variable."

        elif response["code"] == "404":
            return "Couldn't find that location. Check the spelling and try again."

        elif response["code"] == "429":
            return "The configured weather API key has been used too many times. Please wait and try again."

    return "Sorry, I couldn't get the weather for you. Check your connection and try again."


if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    pprint(intent_funcs)
