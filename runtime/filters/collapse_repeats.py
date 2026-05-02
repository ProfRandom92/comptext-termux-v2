def filter_collapse_repeats(text: str, config: dict) -> str:
    """Fasst aufeinander folgende ähnliche Zeilen zusammen."""
    min_repeats = config.get("min_repeats", 3)
    replacement_tpl = config.get("replacement", "[... {n} ähnliche Zeilen ...]")
    lines = text.splitlines(keepends=True)
    result = []
    i = 0
    while i < len(lines):
        current = lines[i].strip()
        count = 1
        while i + count < len(lines) and lines[i + count].strip() == current:
            count += 1
        if count >= min_repeats:
            result.append(replacement_tpl.format(n=count, line=current.strip()) + "\n")
            i += count
        else:
            result.append(lines[i])
            i += 1
    return "".join(result)
