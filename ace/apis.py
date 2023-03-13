import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime as dt
from datetime import timedelta
from typing import Any, Union

import requests
from cachetools import TTLCache, cached
from todoist_api_python.api import TodoistAPI

from ace.utils import Logger

logger = Logger.from_toml(config_file_name="logs.toml", log_name="apis")


@dataclass
class WeatherAPI:
    """
    A class to interface with any weather API.
    """

    _base_urls: dict[str, str] = field(
        default_factory=lambda: {
            "current": "https://api.openweathermap.org/data/2.5/weather?",
            "tomorrow": "https://api.openweathermap.org/data/2.5/forecast?",
        }
    )

    _session: requests.Session = requests.Session()

    def __hash__(self) -> int:  # pragma: no cover
        return hash(self.__class__.__name__)

    def get_current_weather(
        self, location: str = "", units: str = "metric"
    ) -> Union[dict, None]:
        """
        Returns a dictionary containing the current weather for a location,
        or None if there was an error.

        If no location is provided, the location will be determined by the
        location set up in the ACE_HOME environment variable.
        """
        location = location or os.environ["ACE_HOME"]

        logger.log("debug", f"Getting current weather for: {location}")
        if response := self._get_response(location, units, "current"):

            if response["cod"] == 200:
                return {
                    "location": location.title(),
                    "condition": response["weather"][0]["description"],
                    "temp": {
                        "units": "C" if units == "metric" else "F",
                        "current": response["main"]["temp"],
                    },
                    "code": str(response["cod"]),
                }

            return {"code": str(response["cod"]), "message": response["message"]}

        return None

    def get_tomorrow_weather(
        self, location: str = "", units: str = "metric"
    ) -> Union[dict, None]:
        """
        Returns a dictionary containing the weather for tomorrow in a location,
        or None if there was an error.

        If no location is provided, the location will be determined by the
        location set up in the ACE_HOME environment variable.
        """
        location = location or os.environ["ACE_HOME"]

        logger.log("debug", f"Getting tomorrow's weather for: {location}")
        if response := self._get_response(location, units, "tomorrow"):

            if response["cod"] == "200":

                condition, temperature = self._get_weather(response)

                return {
                    "location": location.title(),
                    "condition": condition,
                    "temp": {
                        "units": "C" if units == "metric" else "F",
                        "value": temperature,
                    },
                    "code": str(response["cod"]),
                }

            return {"code": str(response["cod"]), "message": response["message"]}

        return None

    def _get_weather(self, response: dict) -> tuple[str, float]:
        """
        Helper function to get the weather condition and temperature from the
        API response.
        """
        conditions = []
        temperatures = []

        tomorrow = (dt.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        for day in response["list"]:
            if day["dt_txt"].startswith(tomorrow):
                conditions.append(day["weather"][0]["description"])
                temperatures.append(day["main"]["temp"])

        return Counter(conditions).most_common(1)[0][0], round(
            sum(temperatures) / len(temperatures), 2
        )

    @cached(cache=TTLCache(maxsize=1000, ttl=60 * 60 * 3))
    def _get_response(
        self, location: str, units: str, tag: str
    ) -> dict:  # pragma: no cover
        """
        Helper function to get the response from the API.

        Return None if no connection.
        """
        try:

            base_url = self._base_urls.get(tag, "current")
            api_key: str = f"{os.environ['ACE_WEATHER_KEY']}"
            url = f"{base_url}q={location}&appid={api_key}&units={units}"

            logger.log("debug", f"Getting weather from: {url.replace(api_key, '***')}")

            return self._session.get(url).json()

        except requests.exceptions.ConnectionError:

            return None


@dataclass
class TodoAPI:
    """
    A class to interface with task management APIs.
    """

    def tasks_today(self) -> dict:
        """
        Finds all tasks due today and overdue.

        returns: a dictionary with the keys "error" and "tasks".
        If there was an error, the value of "error" will be a string containing
        the error message. Otherwise, the value of "error" will be empty and the
        value of "tasks" will be a list of strings containing the tasks.
        """
        try:
            logger.log("debug", "Getting tasks due today or overdue.")
            tasks = TodoistAPI(os.environ["ACE_TODO_API_KEY"]).get_tasks(
                filters="(today | overdue) & !subtask"
            )

            return {
                "error": None,
                "tasks": [
                    self._clean_task_content(task.content)
                    for task in sorted(
                        filter(
                            lambda task: self._due_today(task),
                            filter(
                                lambda task: not task.content.startswith("*"),
                                tasks,
                            ),
                        ),
                        key=lambda task: task.priority,
                    )
                ],
            }

        except requests.exceptions.ConnectionError:
            return {"error": "Connection error: Check your internet connection."}

        except KeyError:
            return {"error": "API key error: Check your API key is setup correctly."}

    def add_task(self, task: str) -> dict:
        """
        Adds a task to the todoist inbox.

        returns: a dictionary with the keys "error" and "task".
        If there was an error, the value of "error" will be a string containing
        the error message. Otherwise, the value of "error" will be empty and the
        value of "task" will be a string containing the task.
        """
        try:
            logger.log("debug", f"Adding task: {task}.")
            task = TodoistAPI(os.environ["ACE_TODO_API_KEY"]).add_task(task, description="Add from ACE")  # type: ignore

            return {
                "error": None,
                "task": self._clean_task_content(task["content"] if type(task) is dict else task.content),  # type: ignore
            }

        except requests.exceptions.ConnectionError:
            return {"error": "Connection error: Check your internet connection."}

        except KeyError:
            return {"error": "API key error: Check your API key is setup correctly."}

    def _clean_task_content(self, task_content: str) -> str:
        """
        Helper function to clean up the task content.

        returns: a string containing the cleaned task content.
        """
        return task_content.split("](")[0].replace("[", "")

    def _due_today(self, task: Any) -> bool:
        """
        Helper function to check if a task is due today or overdue.

        returns: True if the task is due today or overdue, False otherwise.
        """
        return task.due.date <= dt.now().strftime("%Y-%m-%d") if task.due else False
