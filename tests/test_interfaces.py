import pytest

from ace import interfaces
from ace.utils import TextProcessor

text_processor = TextProcessor()


class TestCLI:
    def test_create_input(self):
        cli = interfaces.CLI(show_header=False)

        assert cli.create_input()

    def test_create_outputs(self):
        cli = interfaces.CLI(show_header=False)

        assert cli.create_outputs()

    def test_create_header_outputs(self):
        cli = interfaces.CLI(show_header=False)

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
        cli = interfaces.CLI(show_header=show_header, header=header)
        cli.display_header()

        assert expected in text_processor.remove_ansi_escape(capsys.readouterr().out)

    def test_get_intent(self, mocker):
        mock_input = mocker.patch("ace.interfaces.CLI.input")
        mock_input.get.return_value = "testing 123"

        mock_intent_classifier = mocker.patch("ace.interfaces.CLI.intent_classifier")
        mock_intent_classifier.predict.return_value = "test_intent"

        cli = interfaces.CLI(show_header=False)

        assert cli.get_intent() == ("test_intent", "testing 123")


class TestGUI:
    @pytest.fixture
    def mock_tk(self, mocker):
        return mocker.patch("ace.interfaces.ctk")

    @pytest.fixture
    def mock_intent_classifier(self, mocker):
        return mocker.patch("ace.interfaces.GUI.intent_classifier")

    @pytest.fixture
    def mock_config_default(self, monkeypatch):
        monkeypatch.setattr(
            interfaces.GUI,
            "config",
            {
                "input": {"text": True},
                "outputs": {
                    "text": True,
                    "speech": False,
                },
                "headers": {
                    "text": True,
                    "speech": False,
                },
                "theme": "dark-blue",
                "test": True,
            },
        )

    def test_gui_objects_created(self, mock_tk, mock_config_default):
        gui = interfaces.GUI(show_header=False)

        assert gui.root
        assert gui.input
        assert gui.chat_box
        assert gui.send_button

    def test_create_input_false(self, mock_tk, monkeypatch):
        monkeypatch.setattr(
            interfaces.GUI,
            "config",
            {
                "input": {"text": False},
                "outputs": {
                    "text": True,
                    "speech": False,
                },
                "headers": {
                    "text": True,
                    "speech": False,
                },
                "theme": "dark-blue",
                "test": True,
            },
        )

        gui = interfaces.GUI(show_header=False)

        assert not gui.user_input
        assert not gui.send_button

    def test_create_outputs_false(self, mock_tk, monkeypatch):
        monkeypatch.setattr(
            interfaces.GUI,
            "config",
            {
                "input": {"text": True},
                "outputs": {
                    "text": False,
                    "speech": False,
                },
                "headers": {
                    "text": True,
                    "speech": False,
                },
                "theme": "dark-blue",
                "test": True,
            },
        )

        gui = interfaces.GUI(show_header=False)

        assert not gui.chat_box

    def test_get_intent(self, mock_tk, mock_intent_classifier, mock_config_default):
        gui = interfaces.GUI(show_header=False)

        assert type(gui.get_intent("testing 123")) == tuple

    def test_get_user_input_default_arguments(
        self, mock_tk, monkeypatch, mock_config_default
    ):
        gui = interfaces.GUI(show_header=False)

        monkeypatch.setattr(gui.input, "get", lambda: "testing 123")

        assert gui.get_user_input() == "testing 123"

    def test_get_user_input_invalid_input_type(
        self, mock_tk, monkeypatch, mock_config_default
    ):
        gui = interfaces.GUI(show_header=False)

        monkeypatch.setattr(gui.input, "get", lambda: "testing 123")

        with pytest.raises(ValueError):
            gui.get_user_input("INVALID")

    def test_get_user_input_valid_type_but_disabled(self, mock_tk, monkeypatch):
        monkeypatch.setattr(
            interfaces.GUI,
            "config",
            {
                "input": {"text": False},
                "outputs": {
                    "text": True,
                    "speech": False,
                },
                "headers": {
                    "text": True,
                    "speech": False,
                },
                "theme": "dark-blue",
                "test": True,
            },
        )

        gui = interfaces.GUI(show_header=False)

        assert gui.get_user_input("text") == ""
