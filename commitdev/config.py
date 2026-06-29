import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".commitdev.json"


def save_token(token: str):
    CONFIG_PATH.write_text(json.dumps({"token": token}))


def get_token():
    if not CONFIG_PATH.exists():
        return None

    return json.loads(CONFIG_PATH.read_text()).get("token")


def clear_token():
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()