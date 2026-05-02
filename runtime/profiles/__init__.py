import os
import yaml

PROFILES_DIR = os.path.join(os.path.dirname(__file__))

COMMAND_MAP = {
    "git": "dev",
    "pytest": "dev",
    "python -m pytest": "dev",
    "cargo test": "dev",
    "npm test": "dev",
    "grep": "log",
    "cat": "log",
    "tail": "log",
    "sqlite3": "repo",
    "med": "med",
    "codex": "med",
    "medcodex": "med",
}


def load_profile(cmd: str = "", override: str = None) -> dict:
    name = override
    if not name:
        for key, profile_name in COMMAND_MAP.items():
            if key in cmd.lower():
                name = profile_name
                break
    if not name:
        name = "dev"

    path = os.path.join(PROFILES_DIR, f"{name}.yml")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            profile = yaml.safe_load(f)
            profile["name"] = name
            return profile
    return {"name": name, "filters": []}
