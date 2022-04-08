import pytest
from ace.net import IntentModel


class TestIntentModel:
    model = IntentModel()

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("", "unknown"),
            (None, "unknown"),
        ],
    )
    def test_predict_unknown(self, text, expected):
        assert self.model.predict(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Hello", "greeting"),
            ("hello", "greeting"),
            ("Hi", "greeting"),
            ("Hey", "greeting"),
            ("hey", "greeting"),
            ("Hello There!", "greeting"),
            ("hello there!", "greeting"),
        ],
    )
    def test_predict_greeting(self, text, expected):
        assert self.model.predict(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Goodbye", "goodbye"),
            ("goodbye", "goodbye"),
            ("Good bye", "goodbye"),
            ("good bye", "goodbye"),
            ("Bye!", "goodbye"),
        ],
    )
    def test_predict_goodbye(self, text, expected):
        assert self.model.predict(text) == expected
