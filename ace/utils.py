import re


class TextProcessor:
    """
    Class for storing helper functions related to processing
    and formatting text.
    """

    def remove_ansi_escape(self, text: str) -> str:
        """
        Remove ANSI escape sequences from a string.
        """
        return re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", text)
