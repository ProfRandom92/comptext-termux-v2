def filter_keep_levels(text: str, config: dict) -> str:
    """Behält nur Log-Zeilen mit bestimmten Level-Keywords."""
    levels = config.get("levels", ["ERROR", "CRITICAL"])
    fallback = config.get("fallback_max_lines", 30)
    lines = text.splitlines(keepends=True)
    relevant = [l for l in lines if any(lv in l for lv in levels)]
    if relevant:
        return "".join(relevant)
    return "".join(lines[-fallback:])
