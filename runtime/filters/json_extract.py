import json
import re


def filter_json_extract(text: str, config: dict) -> str:
    """Extrahiert bestimmte Felder aus JSON-Blöcken im Output."""
    fields = config.get("fields", [])
    if not fields:
        return text

    json_pattern = re.compile(r'\{[^{}]*\}', re.DOTALL)
    result_parts = []
    last_end = 0

    for m in json_pattern.finditer(text):
        result_parts.append(text[last_end:m.start()])
        try:
            obj = json.loads(m.group())
            extracted = {k: obj[k] for k in fields if k in obj}
            result_parts.append(json.dumps(extracted, ensure_ascii=False))
        except Exception:
            result_parts.append(m.group())
        last_end = m.end()

    result_parts.append(text[last_end:])
    return "".join(result_parts)
