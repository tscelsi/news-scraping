def asciify(text: str | None) -> str:
    if text is None:
        return text
    return text.encode("ascii", "ignore").decode("utf-8")
