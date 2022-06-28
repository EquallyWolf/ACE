import pytest
from ace import utils


class TestTextProcessor:
    processor = utils.TextProcessor()

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("\u001b[30m", ""),
            ("\u001b[30m\u001b[30m", ""),
            ("\u001b[30mHello", "Hello"),
            ("\u001b[36mExample Text", "Example Text"),
            ("\u001b[4m Another example\u001b[0m", " Another example"),
            ("\u001b[45;1mTest with a number: 123", "Test with a number: 123"),
        ],
    )
    def test_remove_ansi_escape(self, text, expected):
        assert self.processor.remove_ansi_escape(text) == expected
