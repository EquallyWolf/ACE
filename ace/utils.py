import re
from typing import Union


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

    def find_match(
        self, text: str, patterns: list[str], group: Union[str, int]
    ) -> Union[str, None]:
        """
        Find a match in a string using a list of regex patterns.

        ### Parameters:

        text: str
            The text to search.

        patterns: list[str]
            A list of regex patterns to search for.

        group: str (default: "")
            The group to return from the match.

        ### Returns:

        Union[str, None]
            The match if found, otherwise None.
        """
        for pattern in patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                return match[group] if group else match  # type: ignore
        return None
