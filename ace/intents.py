import platform
from collections import namedtuple
from typing import Callable

import ace.application as app

app_factory = app.AppManagerFactory()

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


if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    pprint(intent_funcs)
