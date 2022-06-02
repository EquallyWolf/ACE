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


def test_intent_open_app_windows(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr("ace.application.WindowsAppManager.open", lambda *args: None)

    response = intents.open_app("open chrome")

    assert response == "Opening 'Chrome'..."


def test_intent_open_app_unknown_platform(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "ABC123")

    response = intents.open_app("open chrome")

    assert response == "Sorry, I don't know how to open apps on this platform (ABC123)."


def test_intent_open_app_windows_not_installed(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "ace.application.windowsapps.find_app",
        lambda x: "test",
    )

    response = intents.open_app("open test")

    assert response == "Sorry, I can't open 'test'. Is it installed?"
