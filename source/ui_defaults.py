import os
import json

DEFAULTS_FILE_PATH = "defaults.json"

WINDOW_SETTINGS = {
    "title": "Stream Highlight Creator",
    "finalize": True,
    "icon": "assets/logo.ico" if os.name == 'nt' else "assets/logo.png"
}


def init():
    if not os.path.isfile(DEFAULTS_FILE_PATH):
        with open(DEFAULTS_FILE_PATH, 'w') as f:
            f.write(json.dumps({}))


def get_defaults(menu: str = "main") -> dict:
    with open(DEFAULTS_FILE_PATH) as f:
        return json.loads(f.read())[menu]


def set_defaults(menu: str, defaults: dict):
    with open(DEFAULTS_FILE_PATH) as f:
        data = json.loads(f.read())

    data[menu] = defaults

    with open(DEFAULTS_FILE_PATH, 'w') as f:
        f.write(json.dumps(data))


init()
