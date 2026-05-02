def filter_keep_section(text: str, config: dict) -> str:
    """Behält nur Abschnitte, die mit einem Trigger-String beginnen."""
    trigger = config.get("trigger", "")
    end_triggers = config.get("end_triggers", [])
    max_lines = config.get("max_lines", 9999)
    if not trigger:
        return text

    lines = text.splitlines(keepends=True)
    result = []
    in_section = False
    section_lines = 0

    for line in lines:
        if trigger in line:
            in_section = True
            section_lines = 0
        if in_section:
            result.append(line)
            section_lines += 1
            if section_lines >= max_lines:
                in_section = False
            elif any(t in line for t in end_triggers) and section_lines > 1:
                in_section = False
    return "".join(result) if result else text
