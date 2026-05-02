def filter_drop_lines(text: str, config: dict) -> str:
    """Entfernt Zeilen, die bestimmte Strings enthalten."""
    patterns = config.get("contains", [])
    lines = text.splitlines(keepends=True)
    out = [l for l in lines if not any(p in l for p in patterns)]
    return "".join(out)
