"""
A module for managing applications on any platform.

#### Classes:

App:
    Stores details of an application.

WindowsAppManager:
    A collection of methods for managing applications on Windows.

AppManagerFactory:
    A factory class for creating AppManager instances.

#### Functions:

app_data():
    Loads the application data from the config/apps.toml file.
"""

import json
import os
import subprocess
from dataclasses import dataclass, field

import tomli


@dataclass
class App:
    """
    Stores details of an application.

    #### Parameters:

    name: str
        The name of the application.

    app_id: str
        The application ID.

    aliases: list[str]
        A list of other names that the application can be
        referred to by.

    executable: str
        The name of the executable file for the application.


    #### Methods: None
    """

    name: str = ""
    app_id: str = ""
    aliases: list[str] = field(default_factory=list)
    executable: str = ""


@dataclass
class WindowsAppManager:
    """
    A collection of methods for managing applications on Windows.

    #### Parameters: None

    #### Methods:

    open(app_name: str) -> None
        Opens the specified application and returns the exit code.

    close(app_name: str) -> int
        Closes the specified application and returns the exit code.
    """

    def open(self, app_name: str) -> None:
        """
        Opens the specified application and returns the exit code.

        #### Parameters:

        app_name: str
            The name of the application to open.

        #### Returns: None

        #### Raises: FileNotFoundError
            If the application could not be found.
        """
        for app in self.apps:
            if app_name.lower() in app.name.lower() or app_name.lower() in app.aliases:
                return os.popen(f"start shell:AppsFolder\\{app.app_id}")
        raise FileNotFoundError(f"Could not find '{app_name}'.")

    def close(self, app_name: str) -> int:
        """
        Closes the specified application and returns the exit code.

        #### Parameters:

        app_name: str
            The name of the application to close.

        #### Returns: int
            The exit code of the command, or -1 if the application
            does not have an executable file.

        #### Raises: None
        """
        for app in self.apps:
            if app_name.lower() in app.name.lower() or app_name.lower() in app.aliases:
                return (
                    subprocess.run(
                        ["taskkill", "/F", "/IM", app.executable], capture_output=True
                    ).returncode
                    if app.executable
                    else -1
                )

    @property
    def apps(self) -> list[App]:
        """
        A list of all applications on the system.

        #### Parameters: None

        #### Returns: list[App]
            A list containing App objects for each application on
            the system.

        #### Raises: None
        """
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
        """
        Helper method for finding all applications on the system.

        #### Parameters: None

        #### Returns: list[dict]
            A list of dictionaries containing the data for each
            application on the system.

        #### Raises: None
        """
        return subprocess.getoutput(
            'powershell -ExecutionPolicy Bypass "Get-StartApps|convertto-json"'
        )


@dataclass
class AppManagerFactory:
    """
    A factory class for creating AppManager instances.

    #### Parameters: None

    #### Methods:

    create(platform: str) -> WindowsAppManager
        Creates an AppManager instance.

    #### Properties:

    managers: dict[str, WindowsAppManager]
        A dictionary of AppManager instances.
    """

    @property
    def managers(self) -> dict[str, WindowsAppManager]:
        """
        A dictionary of AppManager instances available.

        #### Parameters: None

        #### Returns: dict[str, WindowsAppManager]
            A dictionary of AppManager instances.

        """
        return {
            "windows": WindowsAppManager,
        }

    def create(self, platform: str) -> WindowsAppManager:
        """
        Creates an instance of the specified AppManager.

        #### Parameters:

        platform: str
            The name of the platform to create an AppManager for.

        #### Returns: WindowsAppManager
            An instance of the specified AppManager.
        """
        return self.managers[platform.lower()]()


def app_data() -> list[dict]:
    """
    Loads the application data from the config/apps.toml file.

    #### Parameters: None

    #### Returns: list[dict]
        A list of dictionaries containing the data for each
        application on the system.
    """
    with open(os.path.join("config", "apps.toml"), "rb") as f:
        return tomli.load(f)
