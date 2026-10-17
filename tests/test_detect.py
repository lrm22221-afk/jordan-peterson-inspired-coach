import json
import re
import pytest
from keel.config import load_json, principles
from keel.detect import Detector

D = Detector()

ROLEPLAY_CASES = [
    ("I want to ask my boss for a raise next week", "salary_negotiation"),
    ("אני רוצה לבקש העלאה בשכר", "salary_negotiation"),
    ("The client wants a discount and I need to negotiate my rate", "price_negotiation"),
    ("I can't say no to my sister", "set_boundary"),
    ("אני צריך להגיד לא לחבר", "set_boundary"),
    ("My roommate keeps taking advantage of me", "taken_advantage"),
    ("I always help him and he never returns the favor", "ask_reciprocity"),
    ("I had a fight with my wife about money", "conflict_partner"),
    ("רבתי עם אשתי אתמול", "conflict_partner"),
    ("My manager was unfair to me in the meeting", "conflict_work"),
    ("I have a difficult conversation with my dad tomorrow", "hard_conversation"),
]


@pytest.mark.parametrize("text,expected", ROLEPLAY_CASES)
def test_roleplay_triggers(text, expected):
    s = D.roleplay(text)
    assert s is not None and s["id"] == expected


@pytest.mark.parametrize("text", ["I went for a walk today", "What should I read next?", "היה יום רגיל"])
def test_no_roleplay_on_neutral(text):
    assert D.roleplay(text) is None


PATTERN_CASES = [
    ("I keep putting it off", "procrastination"),
    ("שוב דוחה את זה", "procrastination"),
    ("it's not fair, they always get the credit", "resentment"),
    ("It's all their fault, nothing I can do", "victim_narrative"),
    ("I have no routine and sleep until noon", "chaos_no_routine"),
    ("I always say yes, I'm a people pleaser", "pushover"),
    ("what's the point of anything", "nihilism_aimless"),
    ("I lied to my boss about the report", "lying"),
    ("that's not my problem", "no_responsibility"),
    ("I failed again with the gym", "broken_promises"),
    ("I'm fine, really, I don't care anyway", "self_deception"),
]


@pytest.mark.parametrize("text,pid", PATTERN_CASES)
def test_patterns_detected(text, pid):
    assert pid in [p["id"] for p in D.patterns(text)]


@pytest.mark.parametrize("text", ["I want to kill myself", "אני לא רוצה לחיות יותר", "thinking about self-harm"])
def test_crisis(text):
    assert D.safety(text).crisis


def test_abuse_signal():
    assert D.safety("my husband hits me").abuse


def test_every_pattern_cites_existing_principles_with_sources():
    pr = principles()
    for p in load_json("config/patterns.json")["patterns"]:
        assert p["principles"], p["id"]
        for pid in p["principles"]:
            assert pid in pr, (p["id"], pid)
            assert pr[pid]["sources"]


def test_principle_sources_exist_in_report():
    report = open("research/REPORT.md", encoding="utf-8").read()
    ids = {s for p in principles().values() for s in p["sources"]}
    for sid in ids:
        assert re.search(rf"\b{sid}\b", report), sid


def test_all_regexes_compile():
    for f in ["config/patterns.json", "config/roleplay_triggers.json", "config/safety.json"]:
        json.dumps(load_json(f))


@pytest.mark.parametrize("text", ["what's the price of eggs", "המחיר של החלב עלה", "I avoided traffic today"])
def test_no_false_positive_roleplay_or_procrastination(text):
    assert D.roleplay(text) is None
    assert "procrastination" not in [p["id"] for p in D.patterns(text)]


def test_raise_hebrew_variants():
    assert D.roleplay("אני רוצה לבקש להוריד את המחיר מהספק")["id"] == "price_negotiation"


def test_new_lecture_sources_documented_in_notes():
    notes = open("research/transcript_notes.md", encoding="utf-8").read()
    ids = {s for p in principles().values() for s in p["sources"] if s.startswith("L")}
    for sid in ids:
        assert f"## {sid}:" in notes, sid


def test_incremental_principle_verified_and_used_by_patterns():
    pr = principles()
    assert {"L13", "L15", "B1"} <= set(pr["incremental"]["sources"])
    pats = {p["id"]: p for p in load_json("config/patterns.json")["patterns"]}
    assert "incremental" in pats["procrastination"]["principles"]
    assert "agreeable_negotiation" in pats["pushover"]["principles"]
