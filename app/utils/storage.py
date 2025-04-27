import json, pathlib

_DB = pathlib.Path(__file__).with_suffix(".json")

def load_seen() -> set[str]:
    if _DB.exists():
        return set(json.loads(_DB.read_text()))
    return set()

def add_seen(entry_id: str):
    seen = load_seen()
    seen.add(entry_id)
    _DB.write_text(json.dumps(list(seen)))
