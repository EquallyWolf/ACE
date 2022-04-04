import re

GREETINGS = ["hello", "hi", "hey", "hi there"]
GOODBYES = ["goodbye", "good bye", "bye"]


def predict(text: str) -> str:
    """
    Predict the intent of the given text.

    returns: The predicted intent, or "unknown" if the intent is unknown.
    """
    if _is_match(text, GREETINGS):
        return "greeting"
    if _is_match(text, GOODBYES):
        return "goodbye"
    return "unknown"


def _is_match(text: str, patterns: str) -> bool:
    """
    Helper function to check if the given text matches the given pattern.

    returns: True if the text matches the pattern, False otherwise.
    """
    return bool(re.match("|".join(patterns), text or "", re.IGNORECASE))
