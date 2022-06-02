import platform
from dataclasses import dataclass

if platform.system() == "Windows":
    import windowsapps


@dataclass
class WindowsAppManager:
    """
    A class for interacting with applications on the
    Windows platform.
    """

    def open(self, app_name: str):
        """Opens the specified application."""
        windowsapps.open_app(app_name)


@dataclass
class AppManagerFactory:
    """
    A class for creating an AppManager instance.
    """

    @property
    def managers(self):
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
