import pytest
from ace.outputs import CommandLineOutput


@pytest.mark.parametrize(
    "prefix,message,expected",
    [
        ("ACE:", "Hello", "ACE: Hello\n"),
        ("", "Hello", "Hello\n"),
        (None, "Hello", "Hello\n"),
        ("", "", "\n"),
        (">", "Hello world!", "> Hello world!\n"),
        ("  ", "Spaces are trimmed", "Spaces are trimmed\n"),
    ],
)
def test_broadcast_command_line_output(prefix, message, expected, capsys):
    text_output = CommandLineOutput(prefix)
    text_output.broadcast(message)

    assert capsys.readouterr().out == expected
