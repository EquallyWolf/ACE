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
