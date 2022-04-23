from io import StringIO

import pytest
from ace.inputs import CommandLineInput


@pytest.mark.parametrize(
    "prompt,expected",
    [
        ("Enter your name", "Enter your name "),
        ("Enter your age:", "Enter your age: "),
        ("Email>", "Email> "),
        ("", ""),
        ("  ", ""),
        (None, ""),
        ("1.  ", "1. "),
        ("Select menu number: ", "Select menu number: "),
    ],
)
def test_get_command_line_input(prompt, expected, monkeypatch, capsys):
    text_input = CommandLineInput(prompt)
    monkeypatch.setattr("sys.stdin", StringIO("ABC"))

    output = text_input.get()

    assert capsys.readouterr().out == expected
    assert isinstance(output, str), "Should return a string"
