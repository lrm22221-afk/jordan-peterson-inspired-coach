from datetime import datetime, timedelta, timezone
from keel.engine import Coach
from keel.llm import OfflineLLM
from keel.profile import ProfileStore, empty_profile, checkin_due
from keel.progress import add_commitment, resolve, LEVEL_UP_AFTER
from keel import lifeplan, onboarding


def coach(profile=None):
    return Coach(OfflineLLM(), profile or empty_profile())


def test_normal_stance():
    reply, res = coach().respond("I want to read more books")
    assert res["stance"] == "NORMAL" and "[offline:NORMAL]" in reply


def test_firm_after_recurrence_and_cites_principle():
    c = coach()
    _, r1 = c.respond("I keep putting it off")
    assert r1["stance"] == "NORMAL"
    _, r2 = c.respond("haven't started, putting it off again")
    assert r2["stance"] == "FIRM"
    ctx = c.llm.last_messages[-2]["content"]
    assert "FIRM PATTERN: Procrastination" in ctx and "B2" in ctx and "smallest" in ctx.lower()


def test_patterns_persist_across_sessions(tmp_path):
    store = ProfileStore(tmp_path / "p.json")
    p = store.load()
    coach(p).respond("I can't say no to anyone")
    store.save(p)
    p2 = store.load()
    c2 = coach(p2)
    _, res = c2.respond("I always say yes again")
    assert res["stance"] == "FIRM" and p2["patterns"]["pushover"]["count"] == 2


def test_roleplay_auto_offered_once():
    c = coach()
    _, r = c.respond("I need to ask for a raise")
    assert r["stance"] == "ROLEPLAY"
    _, r2 = c.respond("my salary is too low")
    assert r2["stance"] == "NORMAL"


def test_safety_overrides_firm_and_roleplay():
    p = empty_profile()
    p["patterns"]["nihilism_aimless"] = {"count": 5, "last_seen": None, "evidence": []}
    c = coach(p)
    _, res = c.respond("what's the point, I want to kill myself before my salary talk")
    assert res["stance"] == "SAFETY" and res["firm_pattern"] is None and res["roleplay"] is None
    assert "SAFETY RESOURCES" in c.llm.last_messages[-2]["content"]
    assert p["patterns"]["nihilism_aimless"]["count"] == 5  # no counting in crisis


def test_incremental_levels():
    p = empty_profile()
    for _ in range(LEVEL_UP_AFTER):
        resolve(p, add_commitment(p, "walk 5 min")["id"], True)
    assert p["progress"]["level"] == 2 and p["progress"]["streak"] == LEVEL_UP_AFTER
    resolve(p, add_commitment(p, "walk 20 min")["id"], False)
    assert p["progress"]["level"] == 1 and p["progress"]["streak"] == 0


def test_checkin_due_weekly():
    p = empty_profile(); p["onboarded"] = True
    p["last_checkin"] = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
    assert checkin_due(p)
    p["last_checkin"] = datetime.now(timezone.utc).isoformat()
    assert not checkin_due(p)


def test_onboarding_and_lifeplan():
    answers = iter(["Dana", "family, health, craft", "building furniture", "debt, messy flat", "kids, work",
                    "doomscrolling", "college years: I quit too fast", "loyal, curious", "avoidant, late",
                    "a calm home and my own workshop", "isolated and broke", "pay off debt",
                    "freedom for my family", "impulse buys", "delete shopping apps", "-$1000, -$3000",
                    "list all debts tonight"])
    p = empty_profile()
    onboarding.run(p, ask=lambda q: next(answers), say=lambda *a: None)
    lifeplan.plan_goals(p, ask=lambda q: next(answers))
    assert p["values"][0] == "family" and p["future"]["feared"] == "isolated and broke"
    assert p["commitments"][0]["text"] == "list all debts tonight"
    md = lifeplan.render_markdown(p)
    assert "Aim at:" in md and "Smallest next step" in md and "unofficial" in md


def test_system_prompt_no_impersonation():
    c = coach()
    assert "NOT Jordan Peterson" in c.system and "never invent quotes" in c.system.lower()
