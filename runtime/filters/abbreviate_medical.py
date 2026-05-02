def filter_abbreviate_medical(text: str, config: dict) -> str:
    """Ersetzt medizinische Langformen durch CompText-Kürzel."""
    if not config.get("enabled", True):
        return text
    mappings = config.get("mappings", {})
    result = text
    for long_form, abbrev in mappings.items():
        result = result.replace(long_form, abbrev)
    return result
