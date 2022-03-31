def predict(text: str) -> str:
    """
    Predict the intent of the given text.

    returns: The predicted intent, or "unknown" if the intent is unknown.
    """
    if text is None or not text.strip():
        return "unknown"
    if any(
        word.lower() for word in text.split() if word.lower() in {"hello", "hi", "hey"}
    ):
        return "greeting"
