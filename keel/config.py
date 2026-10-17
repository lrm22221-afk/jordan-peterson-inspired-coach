import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_json(rel: str) -> dict:
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def load_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def principles() -> dict:
    return {p["id"]: p for p in load_json("knowledge/principles.json")["principles"]}
