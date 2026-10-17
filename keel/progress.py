"""Incremental progress: smallest-step commitments, streaks, gradual difficulty.

Principle (B1 Rule 4; L13 'aim high and make the goal difficult but proximal'): steps must be
small enough to be kept; after consistent success raise the bar slightly; after a miss shrink it.
"""
import uuid
from datetime import datetime, timedelta, timezone

from .profile import now_iso

LEVEL_UP_AFTER = 3   # kept commitments in a row before raising difficulty
MAX_LEVEL = 10

LEVEL_GUIDE = {
    1: "tiny: under 5 minutes, almost impossible to fail",
    2: "small: about 10-15 minutes once",
    3: "modest: 15-30 minutes, or 3 short repetitions this week",
    4: "steady: daily small habit for a week",
    5: "stretch: a meaningful task that takes real effort",
}


def level_guide(level: int) -> str:
    return LEVEL_GUIDE.get(level, LEVEL_GUIDE[5] + f" (level {level})")


def add_commitment(profile: dict, text: str, days: int = 7, pattern=None) -> dict:
    c = {
        "id": uuid.uuid4().hex[:8],
        "text": text.strip(),
        "made": now_iso(),
        "due": (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(timespec="seconds"),
        "status": "open",
        "level": profile["progress"]["level"],
        "pattern": pattern,
    }
    profile["commitments"].append(c)
    return c


def open_commitments(profile: dict) -> list:
    return [c for c in profile["commitments"] if c["status"] == "open"]


def resolve(profile: dict, cid: str, kept: bool) -> dict:
    """Mark a commitment kept/missed and adapt streak + difficulty level."""
    pr = profile["progress"]
    c = next(c for c in profile["commitments"] if c["id"] == cid)
    c["status"] = "kept" if kept else "missed"
    c["resolved"] = now_iso()
    if kept:
        pr["kept"] += 1
        pr["streak"] += 1
        pr["best_streak"] = max(pr["best_streak"], pr["streak"])
        if pr["streak"] % LEVEL_UP_AFTER == 0 and pr["level"] < MAX_LEVEL:
            pr["level"] += 1
    else:
        pr["missed"] += 1
        pr["streak"] = 0
        pr["level"] = max(1, pr["level"] - 1)
    profile["last_checkin"] = now_iso()
    return c
