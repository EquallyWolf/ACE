from platform import system
from pytest import mark
from ace import intents


def test_unknown_intent():
    response = intents.unknown()

    assert response == "Sorry, I don't know what you mean."


def test_intent_greeting():
    response = intents.greeting()

    assert response == "Hello!"


def test_intent_goodbye():
    response = intents.goodbye()

    assert response == "Goodbye!"


@mark.skipif(system() != "Windows", reason="Windows-only tests")
class TestOpenAppWindows:
    @staticmethod
    def test_intent_open_app_windows(monkeypatch):
        monkeypatch.setattr("ace.application.os.popen", lambda x: None)

        response = intents.open_app("open chrome")

        assert response == "Opening 'Chrome'..."

    @staticmethod
    def test_intent_open_app_unknown_platform(monkeypatch):
        monkeypatch.setattr("platform.system", lambda: "ABC123")
        monkeypatch.setattr("ace.application.os.popen", lambda x: None)

        response = intents.open_app("open chrome")

        assert (
            response
            == "Sorry, I don't know how to open apps on this platform (ABC123)."
        )

    @staticmethod
    def test_intent_open_app_windows_not_installed(monkeypatch):
        response = intents.open_app("open UnknownApp")
        assert response == "Sorry, I can't open 'UnknownApp'. Is it installed?"

    @staticmethod
    def test_intent_open_app_windows_empty_app_list(monkeypatch):
        monkeypatch.setattr("ace.application.os.popen", lambda x: None)
        monkeypatch.setattr(
            "ace.application.WindowsAppManager._find_apps", lambda x: None
        )

        response = intents.open_app("open chrome")

        assert response == "Sorry, I can't open 'Chrome'. Is it installed?"
