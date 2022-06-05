import json
import os
import subprocess
from dataclasses import dataclass


@dataclass
class WindowsAppManager:
    """
    A class for interacting with applications on the
    Windows platform.
    """

    def open(self, app_name: str) -> None:
        """Opens the specified application."""
        for app in sorted(self.apps, key=lambda x: x["Name"]):
            if app_name in app["Name"]:
                return os.popen(f"start shell:AppsFolder\\{app['AppID']}")
        raise FileNotFoundError(f"Could not find '{app_name}'.")

    @property
    def apps(self) -> list[dict]:
        """Finds the path of the specified application."""
        return json.loads(
            subprocess.getoutput(
                'powershell -ExecutionPolicy Bypass "Get-StartApps|convertto-json"'
            )
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
