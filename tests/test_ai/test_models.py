import pytest

from ace.ai.models import IntentClassifierModel, IntentClassifierModelConfig


class TestIntentClassifierModel:

    model = IntentClassifierModel(IntentClassifierModelConfig.from_toml())

    @pytest.mark.parametrize(
        "text",
        [
            "",
            " ",
            "  ",
            None,
        ],
    )
    def test_predict_unknown(self, text):
        assert self.model.predict(text) == "unknown"

    @pytest.mark.parametrize(
        "text",
        [
            "Hello",
            "hi friend",
            "hey ACE",
            "Hello There!",
            "Hi",
            "Hey dude",
            "HELLO",
        ],
    )
    def test_predict_greeting(self, text):
        assert self.model.predict(text) == "greeting"

    @pytest.mark.parametrize(
        "text",
        [
            "Goodbye",
            "GOOD bye",
            "bye bye mate",
            "good bye!",
            "Bye!",
            "See you later",
            "See you",
        ],
    )
    def test_predict_goodbye(self, text):
        assert self.model.predict(text) == "goodbye"

    @pytest.mark.parametrize(
        "text",
        [
            "Open Google",
            "open MS Word",
            "OPEN paint",
            "please open teams",
            "open task-manager",
        ],
    )
    def test_predict_open_app(self, text):
        assert self.model.predict(text) == "open_app"

    @pytest.mark.parametrize(
        "text",
        [
            "close Google",
            "close MS Word",
            "CLOSE paint",
            "please close teams",
            "close task-manager",
        ],
    )
    def test_predict_close_app(self, text):
        assert self.model.predict(text) == "close_app"

    @pytest.mark.parametrize(
        "text",
        [
            "Current weather",
            "weather now",
            "WEATHER NOW PLEASE",
            "what is the weather",
            "what is the weather like",
            "will it thunder today?",
            "weather in london",
        ],
    )
    def test_predict_current_weather(self, text):
        assert self.model.predict(text) == "current_weather"

    @pytest.mark.parametrize(
        "text",
        [
            "Tomorrow's weather",
            "weather tomorrow",
            "TOMORROW WEATHER london",
            "what is the weather tomorrow",
            "what is the weather like tomorrow",
            "will it snow tomorrow?",
            "tell me if it will rain tomorrow",
        ],
    )
    def test_predict_tomorrows_weather(self, text):
        assert self.model.predict(text) == "tomorrow_weather"
