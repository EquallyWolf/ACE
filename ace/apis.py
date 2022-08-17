import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime as dt, timedelta

from typing import Union

import requests


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

            return requests.get(url).json()

        except requests.exceptions.ConnectionError:

            return None
