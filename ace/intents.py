import os
import platform
from collections import namedtuple
from typing import Callable

import ace.application as app
from ace.ai.models import NERModel, NERModelConfig
from ace.apis import WeatherAPI

DEGREES = "\N{DEGREE SIGN}"

app_factory = app.AppManagerFactory()
weather_api = WeatherAPI()
ner_model = NERModel(NERModelConfig.from_toml())

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

    code = manager.close(app_name)
    if code == 0:
        return f"Closing '{app_name}'..."
    elif code == -1:
        return f"I was unable to find the executable for '{app_name}'. Is it defined in the app config?"
    elif code == 128:
        return f"Sorry, I'm can't close '{app_name}'. Is it running?"
    else:
        return f"Sorry, I am having trouble closing '{app_name}'."


@_register(requires_text=True)
def current_weather(text: str) -> str:
    entities = ner_model.predict(text)
    location = next(
        (entity[0] for entity in entities if entity[1] == "GPE"),
        os.environ.get("ACE_LOCATION", None),
    )

    if response := weather_api.get_current_weather(location):  # type: ignore

        if response["code"] == "200":

            unit = f"{DEGREES}{response['temp']['units']}"

            return f"The weather in {response['location']} is {response['temp']['current']}{unit} and {response['condition']}."

        elif response["code"] == "401":
            return "The configured weather API key is invalid. Please check the 'ACE_WEATHER_KEY' environment variable."

        elif response["code"] == "404":
            return f"Couldn't find weather data for that location ({location}). Check the spelling and try again."

        elif response["code"] == "429":
            return "The configured weather API key has been used too many times. Please wait and try again."

    return "Sorry, I couldn't get the weather for you. Check your connection and try again."


@_register(requires_text=True)
def tomorrow_weather(text: str) -> str:
    entities = ner_model.predict(text)
    location = next(
        (entity[0] for entity in entities if entity[1] == "GPE"),
        os.environ.get("ACE_LOCATION", None),
    )

    if response := weather_api.get_tomorrow_weather(location):  # type: ignore

        if response["code"] == "200":

            unit = f"{DEGREES}{response['temp']['units']}"

            return f"The weather tomorrow in {response['location']} will be {response['temp']['value']}{unit} and {response['condition']}."

        elif response["code"] == "401":
            return "The configured weather API key is invalid. Please check the 'ACE_WEATHER_KEY' environment variable."

        elif response["code"] == "404":
            return f"Couldn't find weather data for that location ({location}). Check the spelling and try again."

        elif response["code"] == "429":
            return "The configured weather API key has been used too many times. Please wait and try again."

    return "Sorry, I couldn't get the weather for you. Check your connection and try again."


if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    pprint(intent_funcs)
