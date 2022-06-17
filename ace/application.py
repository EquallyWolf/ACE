import json
import os
import subprocess
from dataclasses import field, dataclass

import tomli


@dataclass
class App:
    """
    A class for storing details of an application.
    """

    name: str = ""
    app_id: str = ""
    aliases: list[str] = field(default_factory=list)
    executable: str = ""


@dataclass
class WindowsAppManager:
    """
    A class for interacting with applications on the
    Windows platform.
    """

    def open(self, app_name: str) -> None:
        """Opens the specified application."""
        for app in self.apps:
            if app_name.lower() in app.name.lower() or app_name.lower() in app.aliases:
                return os.popen(f"start shell:AppsFolder\\{app.app_id}")
        raise FileNotFoundError(f"Could not find '{app_name}'.")

    def close(self, app_name: str) -> None:
        """Closes the specified application."""
        for app in self.apps:
            if app_name.lower() in app.name.lower() or app_name.lower() in app.aliases:
                return os.popen(" ".join(["taskkill", "/F", "/IM", app.executable]))
        raise FileNotFoundError(f"Could not find '{app_name}'.")

    @property
    def apps(self) -> list[App]:
        """Returns a list containing details of all applications
        installed on the system."""
        if output := self._find_apps():
            found_apps = json.loads(output)
            data = app_data()

            return [
                App(
                    name=app["Name"],
                    app_id=app["AppID"],
                    aliases=data["aliases"].get(app["Name"], []),
                    executable=data["executable"].get(app["Name"], ""),
                )
                for app in found_apps
            ]

        else:
            return [App()]

    def _find_apps(self) -> list[dict]:
        """Run command to find all applications on the system."""
        return subprocess.getoutput(
            'powershell -ExecutionPolicy Bypass "Get-StartApps|convertto-json"'
        )


@dataclass
class AppManagerFactory:
    """
    A class for creating an AppManager instance.
    """

    @property
    def managers(self) -> dict[str, WindowsAppManager]:
        """
        Returns a dictionary of AppManager instances.
        """
        return {
            "windows": WindowsAppManager,
        }

    def create(self, platform: str) -> WindowsAppManager:
        """
        Creates an AppManager instance.
        """
        return self.managers[platform.lower()]()


def app_data() -> list[dict]:
    """
    Returns a list of dictionaries containing the data for all apps.
    """
    with open(os.path.join("config", "apps.toml"), "rb") as f:
        return tomli.load(f)


def app_id(app_name: str) -> str:
    """
    Returns the ID of the app with the given name.
    """
    for app_id, aliases in app_data()["aliases"].items():
        if app_name in aliases:
            return app_id
