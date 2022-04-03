import re


def predict(text: str) -> str:
    """
    Predict the intent of the given text.

    returns: The predicted intent, or "unknown" if the intent is unknown.
    """
    if re.match(
        "|".join(["hello", "hi", "hey", "hi there"]), text or "", re.IGNORECASE
    ):
        return "greeting"
    if re.match("|".join(["goodbye", "good bye", "bye"]), text or "", re.IGNORECASE):
        return "goodbye"
    return "unknown"
