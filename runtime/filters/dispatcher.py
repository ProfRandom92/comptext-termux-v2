"""Dispatcher: wendet alle Filter eines Profils der Reihe nach an."""
from .drop_lines import filter_drop_lines
from .keep_section import filter_keep_section
from .collapse_repeats import filter_collapse_repeats
from .max_lines import filter_max_lines
from .keep_levels import filter_keep_levels
from .abbreviate_medical import filter_abbreviate_medical
from .json_extract import filter_json_extract

FILTER_MAP = {
    "drop_lines": filter_drop_lines,
    "keep_section": filter_keep_section,
    "collapse_repeats": filter_collapse_repeats,
    "max_lines": filter_max_lines,
    "keep_levels": filter_keep_levels,
    "abbreviate_medical": filter_abbreviate_medical,
    "json_extract": filter_json_extract,
}


def apply_filters(text: str, profile: dict) -> str:
    result = text
    for f in profile.get("filters", []):
        fn = FILTER_MAP.get(f["type"])
        if fn:
            result = fn(result, f)
    return result
