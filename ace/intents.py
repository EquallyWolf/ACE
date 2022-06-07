import os
import platform

import tomli
import ace.application as app


app_factory = app.AppManagerFactory()


def unknown() -> str:
    return "Sorry, I don't know what you mean."


def greeting() -> str:
    return "Hello!"


def goodbye() -> str:
    return "Goodbye!"


def open_app(text: str) -> str:
    app_name = " ".join(text.split(" ")[1:])

    with open(os.path.join("config", "apps.toml"), "rb") as f:
        app_data = tomli.load(f)

    for app_id, aliases in app_data["aliases"].items():
        if app_name in aliases:
            app_name = app_id
            break

    current_platform = platform.system()

    try:
        manager = app_factory.create(current_platform)
    except KeyError:
        return f"Sorry, I don't know how to open apps on this platform ({current_platform})."

    try:
        manager.open(app_name)
        return f"Opening '{app_name}'..."
    except FileNotFoundError:
        return f"Sorry, I can't open '{app_name}'. Is it installed?"


def close_app(text: str) -> str:
    app_name = " ".join(text.split(" ")[1:])

    with open(os.path.join("config", "apps.toml"), "rb") as f:
        app_data = tomli.load(f)

    for app_id, aliases in app_data["aliases"].items():
        if app_name in aliases:
            app_name = app_id
            break

    current_platform = platform.system()

    try:
        manager = app_factory.create(current_platform)
    except KeyError:
        return f"Sorry, I don't know how to close apps on this platform ({current_platform})."

    try:
        manager.close(app_name)
        return f"Closing '{app_name}'..."
    except FileNotFoundError:
        return f"Sorry, I can't close '{app_name}'. Is it installed?"
