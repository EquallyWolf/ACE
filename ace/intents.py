"""
This module provides the necessary functionality to interpret and execute
user intents.

#### Classes: None

#### Functions:

run_intent(intent_name: str, *args, **kwargs) -> tuple[str, bool]:
    Runs the function associated with the intent name.
"""

import os
import platform
from collections import namedtuple
from typing import Callable

import ace.application as app
from ace.ai.models import NERModel, NERModelConfig
from ace.apis import TodoAPI, WeatherAPI
from ace.utils import TextProcessor, Logger

DEGREES = "\N{DEGREE SIGN}"
ADD_TODO_PATTERNS = [
    r"add the task (?P<TASK_ITEM>.+) to my (todo|to-do|to do|task|tasks)",
    r"(add todo|add to-do|add to do|add task|add tasks) (?P<TASK_ITEM>.+) to (todo|to-do|to do|task|tasks)",
    r"add to my (todo|to-do|to do|task|tasks) list (?P<TASK_ITEM>.+)",
    r"add to my (todo|to-do|to do|task|tasks) (?P<TASK_ITEM>.+)",
    r"add to (todo|to-do|to do|task|tasks) list (?P<TASK_ITEM>.+)",
    r"add (?P<TASK_ITEM>.+) to my (todo|to-do|to do|task|tasks) list",
    r"add (?P<TASK_ITEM>.+) to the (todo|to-do|to do|task|tasks) list",
    r"add (?P<TASK_ITEM>.+) to my (todo|to-do|to do|task|tasks)",
    r"add (?P<TASK_ITEM>.+) to (todo|to-do|to do|task|tasks)",
]

logger = Logger.from_toml(config_file_name="logs.toml", log_name="intents")

app_factory = app.AppManagerFactory()
weather_api = WeatherAPI()
todo_api = TodoAPI()
ner_model = NERModel(NERModelConfig.from_toml())
text_processor = TextProcessor()

Intent = namedtuple("Intent", ["func", "should_exit", "requires_text"])
intent_funcs: dict[str, Intent] = {}


def _register(**kwargs) -> Callable:
    """
    A decorator that adds the function to the intent_funcs dictionary.

    #### Parameters:

    should_exit: bool
        Whether or not the application should exit after running the intent.

    requires_text: bool
        Whether or not the intent requires text to be passed to it.

    #### Returns: Callable
        The decorated function.

    #### Raises: None
    """

    def inner(func) -> Callable:
        intent_funcs[func.__name__] = Intent(
            func, kwargs.get("should_exit", False), kwargs.get("requires_text", False)
        )
        return func

    return inner


def run_intent(intent_name: str, *args, **kwargs) -> tuple[str, bool]:
    """
    Runs the function associated with the intent name. If the intent
    requires text, it will be passed as the first argument.

    #### Parameters:

    intent_name: str
        The name of the intent function to run. If the intent is not found,
        the `unknown` intent will be run.

    *args: Any
        Any additional arguments to pass to the intent function.

    **kwargs: Any
        Any additional keyword arguments to pass to the intent function.

    #### Returns: tuple[str, bool]
        A tuple containing the response from the intent function and
        whether or not the application should exit.

    #### Raises: None
    """
    intent = intent_funcs.get(intent_name, unknown)

    response = intent.func(*args, **kwargs) if intent.requires_text else intent.func()
    logger.log("debug", f"Intent - {intent_name} :: Returned - {response}")

    return response, intent.should_exit


@_register()
def unknown() -> str:
    """
    The default intent function. This is run when the intent name is not
    found in the intent_funcs dictionary or when the intent is below the
    confidence threshold.

    #### Parameters: None

    #### Returns: str
        The response to the user explaining that the user intent was not
        understood.

    #### Raises: None

    """
    return "Sorry, I don't know what you mean."


@_register()
def greeting() -> str:
    """
    Provides a greeting to the user.

    #### Parameters: None

    #### Returns: str
        A greeting to the user.
    """
    return "Hello!"


@_register(should_exit=True)
def goodbye() -> str:
    """
    Provides a goodbye message to the user.

    #### Parameters: None

    #### Returns: str
        A goodbye message to the user.

    #### Raises: None
    """
    return "Goodbye!"


@_register(requires_text=True)
def open_app(text: str) -> str:
    """
    Opens an application on the current platform.

    #### Parameters:

    text: str
        The text to parse for the application name.

    #### Returns: str
        A message to the user indicating the outcome of whether or not the
        application was opened.

    #### Raises: None
    """
    app_name = " ".join(text.split(" ")[1:])

    current_platform = platform.system()

    try:
        with logger.log_context(
            "debug",
            f"Creating app manager for '{current_platform}'",
            "App manager created.",
        ):
            manager = app_factory.create(current_platform)
    except KeyError:
        logger.log("debug", f"Platform '{current_platform}' not found in APP_CONFIG.")
        return f"Sorry, I don't know how to open apps on this platform ({current_platform})."

    try:
        manager.open(app_name)
        logger.log("debug", f"Opening '{app_name}'...")
        return f"Opening '{app_name}'..."
    except FileNotFoundError:
        logger.log("debug", f"App '{app_name}' not found.")
        return f"Sorry, I can't open '{app_name}'. Is it installed?"


@_register(requires_text=True)
def close_app(text: str) -> str:
    """
    Closes an application on the current platform.

    #### Parameters:

    text: str
        The text to parse for the application name.

    #### Returns: str
        A message to the user indicating the outcome of whether or not the
        application was closed.

    #### Raises: None
    """
    app_name = " ".join(text.split(" ")[1:])

    current_platform = platform.system()

    try:
        with logger.log_context(
            "debug",
            f"Creating app manager for '{current_platform}'",
            "App manager created.",
        ):
            manager = app_factory.create(current_platform)
    except KeyError:
        return f"Sorry, I don't know how to close apps on this platform ({current_platform})."

    code = manager.close(app_name)
    logger.log("debug", f"Close app returned code: {code}")
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
    """
    Gets the current weather for a given location.

    #### Parameters:

    text: str
        The text to parse for the location.

    #### Returns: str
        A message to the user containing the current weather for the given
        location.

    #### Raises: None
    """
    entities = ner_model.predict(text)
    logger.log("debug", f"Got entities: {entities}")

    location = next(
        (entity[0] for entity in entities if entity[1] == "GPE"),
        os.environ.get("ACE_LOCATION", None),
    )

    if response := weather_api.get_current_weather(location):  # type: ignore

        logger.log("debug", f"Got weather response: {response}")

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
    """
    Gets the weather for tomorrow for a given location.

    #### Parameters:

    text: str
        The text to parse for the location.

    #### Returns: str
        A message to the user containing the weather for tomorrow for the given
        location.

    #### Raises: None
    """
    entities = ner_model.predict(text)
    logger.log("debug", f"Got entities: {entities}")

    location = next(
        (entity[0] for entity in entities if entity[1] == "GPE"),
        os.environ.get("ACE_LOCATION", None),
    )

    if response := weather_api.get_tomorrow_weather(location):  # type: ignore

        logger.log("debug", f"Got weather response: {response}")

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


@_register()
def show_todo_list() -> str:
    """
    Gets the user's todo list for today.

    #### Parameters: None

    #### Returns: str
        A message to the user containing the user's todo list for today.

    #### Raises: None
    """
    task_list = todo_api.tasks_today()
    logger.log("debug", f"Got task list: {task_list}")

    if task_list["error"]:
        logger.log("error", f"Error getting task list: {task_list['error']}")
        return f"Sorry, I couldn't get your tasks. {task_list['error']}"

    if total_tasks := len(task_list["tasks"]):
        first_task = task_list["tasks"][0]

        return (
            f"You have {total_tasks} task today. The task is '{first_task}'."
            if total_tasks == 1
            else f"You have {total_tasks} tasks today. The first one is '{first_task}'."
        )
    return "You have no tasks today."


@_register(requires_text=True)
def add_todo(text: str) -> str:
    """
    Adds a task to the user's todo list.

    #### Parameters:

    text: str
        The text to parse for the task.

    #### Returns: str
        A message to the user confirming the task was added.

    #### Raises: None
    """
    if task := text_processor.find_match(text, ADD_TODO_PATTERNS, "TASK_ITEM"):

        task_item = todo_api.add_task(task.removeprefix("add").strip())
        logger.log("debug", f"Got task item: {task_item}")

        if task_item["error"]:
            logger.log("error", f"Error adding task: {task_item['error']}")
            return f"Sorry, I couldn't add your task. {task_item['error']}"

        return f"Added '{task_item['task']}' to your to-do list."

    return "Sorry, I can't understand which task you wanted to add."


if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    pprint(intent_funcs)
