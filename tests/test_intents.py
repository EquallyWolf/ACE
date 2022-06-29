from platform import system
from pytest import mark
from ace.intents import run_intent


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
