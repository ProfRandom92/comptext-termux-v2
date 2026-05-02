def filter_max_lines(text: str, config: dict) -> str:
    """Begrenzt den Output auf eine maximale Zeilenanzahl."""
    limit = config.get("limit", 200)
    msg = config.get("truncate_msg", "\n[comptext-runtime] Output gekürzt.")
    lines = text.splitlines(keepends=True)
    if len(lines) <= limit:
        return text
    return "".join(lines[:limit]) + msg + "\n"
