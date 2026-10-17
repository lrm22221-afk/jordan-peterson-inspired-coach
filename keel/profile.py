"""Local JSON user profile: values, burdens, goals, patterns, commitments, progress."""
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_PATH = Path(os.environ.get("KEEL_PROFILE", Path.home() / ".keel" / "profile.json"))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s)


def empty_profile() -> dict:
    return {
        "version": 1,
        "created": now_iso(),
        "language": "en",
        "name": "",
        "onboarded": False,
        "values": [], "motivations": [], "burdens": [], "goals": [],
        "essential": [], "non_essential": [],
        "past": {}, "present": {"virtues": [], "faults": []},
        "future": {"ideal": "", "feared": ""},
        "patterns": {},          # id -> {"count": n, "last_seen": iso, "evidence": [..]}
        "commitments": [],       # {"id","text","made","due","status","level","pattern"}
        "progress": {"streak": 0, "best_streak": 0, "level": 1, "kept": 0, "missed": 0},
        "last_checkin": None,
        "sessions": 0,
    }


class ProfileStore:
    def __init__(self, path=None):
        self.path = Path(path) if path else DEFAULT_PATH

    def load(self) -> dict:
        if not self.path.exists():
            return empty_profile()
        with open(self.path, encoding="utf-8") as f:
            data = json.load(f)
        base = empty_profile()
        base.update(data)
        return base

    def save(self, profile: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass


def record_pattern(profile: dict, pid: str, evidence: str) -> int:
    p = profile["patterns"].setdefault(pid, {"count": 0, "last_seen": None, "evidence": []})
    p["count"] += 1
    p["last_seen"] = now_iso()
    p["evidence"] = (p["evidence"] + [evidence[:160]])[-5:]
    return p["count"]


def checkin_due(profile: dict, days: int = 7, now=None) -> bool:
    now = now or datetime.now(timezone.utc)
    if not profile.get("onboarded"):
        return False
    last = profile.get("last_checkin")
    if last is None:
        open_c = [c for c in profile["commitments"] if c["status"] == "open"]
        return any(parse_iso(c["made"]) <= now - timedelta(days=days) for c in open_c)
    return parse_iso(last) <= now - timedelta(days=days)
