from io import StringIO

import pytest
from ace.inputs import CommandLineInput
from ace.utils import TextProcessor

text_processor = TextProcessor()


class TestCommandLineInputs:
    @pytest.mark.parametrize(
        "prompt,expected",
        [
            ("", ""),
            ("  ", ""),
            (None, ""),
        ],
    )
    def test_get_command_line_input_no_prompt(
        self, prompt, expected, monkeypatch, capsys
    ):
        text_input = CommandLineInput(prompt)
        monkeypatch.setattr("sys.stdin", StringIO("ABC"))

        output = text_input.get()

        assert text_processor.remove_ansi_escape(capsys.readouterr().out) == expected
        assert isinstance(output, str), "Should return a string"

    @pytest.mark.parametrize(
        "prompt,expected",
        [
            ("A", "A "),
            ("Enter age ", "Enter age "),
            ("mobile number     ", "mobile number "),
        ],
    )
    def test_get_command_line_input_no_special_character(
        self, prompt, expected, monkeypatch, capsys
    ):
        text_input = CommandLineInput(prompt)
        monkeypatch.setattr("sys.stdin", StringIO("ABC"))

        output = text_input.get()

        assert text_processor.remove_ansi_escape(capsys.readouterr().out) == expected
        assert isinstance(output, str), "Should return a string"

    @pytest.mark.parametrize(
        "prompt,expected",
        [
            ("1.  ", "1. "),
            ("Select menu number: ", "Select menu number: "),
            ("What is your name?", "What is your name? "),
            ("Email>", "Email> "),
        ],
    )
    def test_get_command_line_input_special_character(
        self, prompt, expected, monkeypatch, capsys
    ):
        text_input = CommandLineInput(prompt)
        monkeypatch.setattr("sys.stdin", StringIO("ABC"))

        output = text_input.get()

        assert text_processor.remove_ansi_escape(capsys.readouterr().out) == expected
        assert isinstance(output, str), "Should return a string"
