import pytest

from ace.interfaces import CLI
from ace.utils import TextProcessor

text_processor = TextProcessor()


class TestCLI:
    def test_create_input(self):
        cli = CLI(show_header=False)

        assert cli.create_input()

    def test_create_outputs(self):
        cli = CLI(show_header=False)

        assert cli.create_outputs()

    def test_create_header_outputs(self):
        cli = CLI(show_header=False)

        assert cli.create_header_outputs()

    @pytest.mark.parametrize(
        "show_header,header,expected",
        [
            (True, "Hello world!", "Hello world!\n"),
            (False, "Hello world!", ""),
            (True, "", "\n"),
            (False, "", ""),
        ],
    )
    def test_display_header(self, show_header, header, expected, capsys):
        cli = CLI(show_header=show_header, header=header)
        cli.display_header()

        assert expected in text_processor.remove_ansi_escape(capsys.readouterr().out)

    def test_get_intent(self, mocker):
        mock_input = mocker.patch("ace.interfaces.CLI.input")
        mock_input.get.return_value = "testing 123"

        mock_intent_classifier = mocker.patch("ace.interfaces.CLI.intent_classifier")
        mock_intent_classifier.predict.return_value = "test_intent"

        cli = CLI(show_header=False)

        assert cli.get_intent() == ("test_intent", "testing 123")
