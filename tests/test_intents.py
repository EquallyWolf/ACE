import json
from platform import system

import pytest
from ace.intents import run_intent
from freezegun import freeze_time
from pytest import mark


def test_unknown_intent():
    response, exit_script = run_intent("unknown")

    assert response == "Sorry, I don't know what you mean."
    assert exit_script is False


def test_intent_greeting():
    response, exit_script = run_intent("greeting")

    assert response == "Hello!"
    assert exit_script is False


def test_intent_goodbye():
    response, exit_script = run_intent("goodbye")

    assert response == "Goodbye!"
    assert exit_script is True


@mark.skipif(system() != "Windows", reason="Windows-only tests")
class TestOpenAppWindows:
    @staticmethod
    def test_intent_open_app_windows(monkeypatch):
        monkeypatch.setattr("ace.application.os.popen", lambda x: None)

        response, exit_script = run_intent("open_app", "open chrome")

        assert response == "Opening 'chrome'..."
        assert exit_script is False

    @staticmethod
    def test_intent_open_app_unknown_platform(monkeypatch):
        monkeypatch.setattr("platform.system", lambda: "ABC123")
        monkeypatch.setattr("ace.application.os.popen", lambda x: None)

        response, exit_script = run_intent("open_app", "open chrome")

        assert (
            response
            == "Sorry, I don't know how to open apps on this platform (ABC123)."
        )
        assert exit_script is False

    @staticmethod
    def test_intent_open_app_windows_not_installed(monkeypatch):
        response, exit_script = run_intent("open_app", "open UnknownApp")

        assert response == "Sorry, I can't open 'UnknownApp'. Is it installed?"
        assert exit_script is False

    @staticmethod
    def test_intent_open_app_windows_empty_app_list(monkeypatch):
        monkeypatch.setattr("ace.application.os.popen", lambda x: None)
        monkeypatch.setattr(
            "ace.application.WindowsAppManager._find_apps", lambda x: None
        )

        response, exit_script = run_intent("open_app", "open chrome")

        assert response == "Sorry, I can't open 'chrome'. Is it installed?"
        assert exit_script is False


@mark.skipif(system() != "Windows", reason="Windows-only tests")
class TestCloseAppIntent:
    @staticmethod
    def test_intent_close_app_windows(monkeypatch):
        monkeypatch.setattr("ace.application.os.popen", lambda x: None)

        response, exit_script = run_intent("close_app", "close Chrome")

        assert response == "Closing 'Chrome'..."
        assert exit_script is False

    @staticmethod
    def test_intent_close_app_unknown_platform(monkeypatch):
        monkeypatch.setattr("platform.system", lambda: "ABC123")
        monkeypatch.setattr("ace.application.os.popen", lambda x: None)

        response, exit_script = run_intent("close_app", "close Chrome")

        assert (
            response
            == "Sorry, I don't know how to close apps on this platform (ABC123)."
        )
        assert exit_script is False

    @staticmethod
    def test_intent_close_app_windows_not_installed(monkeypatch):
        response, exit_script = run_intent("close_app", "close UnknownApp")

        assert response == "Sorry, I can't close 'UnknownApp'. Is it running?"
        assert exit_script is False


class TestCurrentWeatherIntent:
    environment = {"ACE_WEATHER_KEY": "123456789", "ACE_HOME": "London"}
    mock_weather_file = "tests/data/weather/current_weather.json"

    @pytest.fixture
    def mock_weather_response_success(self):
        with open(self.mock_weather_file) as f:
            return json.load(f)["SUCCESS"]

    @pytest.fixture
    def mock_weather_response_failure_404(self):
        with open(self.mock_weather_file) as f:
            return json.load(f)["FAILURE"]["404"]

    @pytest.fixture
    def mock_weather_response_failure_401(self):
        with open(self.mock_weather_file) as f:
            return json.load(f)["FAILURE"]["401"]

    @pytest.fixture
    def mock_weather_response_failure_429(self):
        with open(self.mock_weather_file) as f:
            return json.load(f)["FAILURE"]["429"]

    @staticmethod
    def test_current_weather_response_incorrect_city(
        monkeypatch, mock_weather_response_failure_404
    ):
        monkeypatch.setattr(
            "ace.intents.WeatherAPI._get_response",
            lambda *args: mock_weather_response_failure_404,
        )

        response, exit_script = run_intent(
            "current_weather", "current weather in London"
        )

        assert (
            response == "Couldn't find that location. Check the spelling and try again."
        )
        assert exit_script is False

    @staticmethod
    def test_current_weather_response_incorrect_key(
        monkeypatch, mock_weather_response_failure_401
    ):
        monkeypatch.setattr(
            "ace.intents.WeatherAPI._get_response",
            lambda *args: mock_weather_response_failure_401,
        )

        response, exit_script = run_intent(
            "current_weather", "current weather in London"
        )

        assert (
            response
            == "The configured weather API key is invalid. Please check the 'ACE_WEATHER_KEY' environment variable."
        )
        assert exit_script is False

    @staticmethod
    def test_current_weather_response_too_many_requests(
        monkeypatch, mock_weather_response_failure_429
    ):
        monkeypatch.setattr(
            "ace.intents.WeatherAPI._get_response",
            lambda *args, success=False: mock_weather_response_failure_429,
        )
        response, exit_script = run_intent(
            "current_weather", "current weather in London"
        )

        assert (
            response
            == "The configured weather API key has been used too many times. Please wait and try again."
        )
        assert exit_script is False

    @staticmethod
    def test_current_weather_response_unknown_error(monkeypatch):
        monkeypatch.setattr(
            "ace.intents.WeatherAPI._get_response",
            lambda *args: None,
        )
        response, exit_script = run_intent(
            "current_weather", "current weather in London"
        )

        assert (
            response
            == "Sorry, I couldn't get the weather for you. Check your connection and try again."
        )
        assert exit_script is False

    @pytest.mark.parametrize(
        "text,expected",
        [
            (
                "Current weather",
                "The weather in London is 14.19\N{DEGREE SIGN}C and few clouds.",
            ),
            (
                "current weather conditions",
                "The weather in London is 14.19\N{DEGREE SIGN}C and few clouds.",
            ),
            (
                "weather in London",
                "The weather in London is 14.19\N{DEGREE SIGN}C and few clouds.",
            ),
            (
                "Get weather in Billingshurst",
                "The weather in Billingshurst is 14.19\N{DEGREE SIGN}C and few clouds.",
            ),
            (
                "get current weather in Paris",
                "The weather in Paris is 14.19\N{DEGREE SIGN}C and few clouds.",
            ),
            (
                "Current weather conditions",
                "The weather in London is 14.19\N{DEGREE SIGN}C and few clouds.",
            ),
        ],
    )
    def test_current_weather_api_response(
        self,
        monkeypatch,
        text,
        expected,
        mock_weather_response_success,
    ):
        monkeypatch.setattr(
            "ace.apis.os.environ",
            self.environment,
        )

        monkeypatch.setattr(
            "ace.intents.WeatherAPI._get_response",
            lambda *args, success=True: mock_weather_response_success,
        )
        response, exit_script = run_intent("current_weather", text)

        assert response == expected
        assert exit_script is False


@freeze_time("13-07-2022 08:00:00")
class TestTomorrowWeatherIntent:
    environment = {"ACE_WEATHER_KEY": "123456789", "ACE_HOME": "London"}
    mock_weather_file = "tests/data/weather/tomorrow_weather.json"

    @pytest.fixture
    def mock_weather_response_success(self):
        with open(self.mock_weather_file) as f:
            return json.load(f)["SUCCESS"]

    @pytest.fixture
    def mock_weather_response_failure_404(self):
        with open(self.mock_weather_file) as f:
            return json.load(f)["FAILURE"]["404"]

    @pytest.fixture
    def mock_weather_response_failure_401(self):
        with open(self.mock_weather_file) as f:
            return json.load(f)["FAILURE"]["401"]

    @pytest.fixture
    def mock_weather_response_failure_429(self):
        with open(self.mock_weather_file) as f:
            return json.load(f)["FAILURE"]["429"]

    def test_tomorrow_weather_response_incorrect_city(
        self, monkeypatch, mock_weather_response_failure_404
    ):
        monkeypatch.setattr(
            "ace.intents.WeatherAPI._get_response",
            lambda *args: mock_weather_response_failure_404,
        )

        response, exit_script = run_intent(
            "tomorrow_weather", "tomorrow weather in London"
        )

        assert (
            response == "Couldn't find that location. Check the spelling and try again."
        )
        assert exit_script is False

    def test_tomorrow_weather_response_incorrect_key(
        self, monkeypatch, mock_weather_response_failure_401
    ):
        monkeypatch.setattr(
            "ace.intents.WeatherAPI._get_response",
            lambda *args: mock_weather_response_failure_401,
        )

        response, exit_script = run_intent(
            "tomorrow_weather", "tomorrow weather in London"
        )

        assert (
            response
            == "The configured weather API key is invalid. Please check the 'ACE_WEATHER_KEY' environment variable."
        )
        assert exit_script is False

    def test_tomorrow_weather_response_too_many_requests(
        self, monkeypatch, mock_weather_response_failure_429
    ):
        monkeypatch.setattr(
            "ace.intents.WeatherAPI._get_response",
            lambda *args, success=False: mock_weather_response_failure_429,
        )
        response, exit_script = run_intent(
            "tomorrow_weather", "tomorrow weather in London"
        )

        assert (
            response
            == "The configured weather API key has been used too many times. Please wait and try again."
        )
        assert exit_script is False

    def test_tomorrow_weather_response_unknown_error(self, monkeypatch):
        monkeypatch.setattr(
            "ace.intents.WeatherAPI._get_response",
            lambda *args: None,
        )
        response, exit_script = run_intent(
            "tomorrow_weather", "tomorrow weather in London"
        )

        assert (
            response
            == "Sorry, I couldn't get the weather for you. Check your connection and try again."
        )
        assert exit_script is False

    @pytest.mark.parametrize(
        "text,expected",
        [
            (
                "Tomorrow weather",
                "The weather tomorrow in London will be 19.99\N{DEGREE SIGN}C and scattered clouds.",
            ),
            (
                "tomorrow weather conditions",
                "The weather tomorrow in London will be 19.99\N{DEGREE SIGN}C and scattered clouds.",
            ),
            (
                "weather tomorrow in London",
                "The weather tomorrow in London will be 19.99\N{DEGREE SIGN}C and scattered clouds.",
            ),
            (
                "Get weather tomorrow in Billingshurst",
                "The weather tomorrow in Billingshurst will be 19.99\N{DEGREE SIGN}C and scattered clouds.",
            ),
            (
                "get tomorrow weather in Paris",
                "The weather tomorrow in Paris will be 19.99\N{DEGREE SIGN}C and scattered clouds.",
            ),
            (
                "Tomorrow weather conditions",
                "The weather tomorrow in London will be 19.99\N{DEGREE SIGN}C and scattered clouds.",
            ),
            (
                "Tomorrow's weather",
                "The weather tomorrow in London will be 19.99\N{DEGREE SIGN}C and scattered clouds.",
            ),
        ],
    )
    def test_tomorrow_weather_api_response(
        self,
        monkeypatch,
        text,
        expected,
        mock_weather_response_success,
    ):
        monkeypatch.setattr(
            "ace.apis.os.environ",
            self.environment,
        )

        monkeypatch.setattr(
            "ace.intents.WeatherAPI._get_response",
            lambda *args, success=True: mock_weather_response_success,
        )
        response, exit_script = run_intent("tomorrow_weather", text)

        assert response == expected
        assert exit_script is False
