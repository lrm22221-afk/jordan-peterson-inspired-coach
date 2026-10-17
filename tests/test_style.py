from keel.config import load_text
from keel.engine import Coach
from keel.llm import OfflineLLM
from keel.profile import empty_profile
from keel.tts import to_ssml


def test_style_doc_has_evidence():
    s = load_text("persona/speech_style.md")
    for marker in ["Measured rhythm", "Tenderness toward suffering", "Firm but loving", "L1 00:29:39", "L19 01:39:20", "Never"]:
        assert marker in s


def test_style_folded_into_both_prompts():
    en = load_text("persona/system_prompt.en.md")
    he = load_text("persona/system_prompt.he.md")
    assert "Speech style" in en and "That's not wise." in en and "SAFETY mode, drop the rhetorical style" in en
    assert "סגנון דיבור" in he and "מקצב" in he and "במצב בטיחות" in he
    assert "NOT Jordan Peterson" in en and "אתה לא ג'ורדן פיטרסון" in he


def test_ssml_pause_markers():
    out = to_ssml("Well... think about it — carefully.\n\nThat's not wise.")
    assert out.startswith("<speak>") and '<break time="700ms"/>' in out and '<break time="400ms"/>' in out
    assert '<break time="900ms"/>' in out


def test_ssml_safety_is_calmer_not_dramatic():
    assert '<break time="500ms"/>' in to_ssml("I'm here...", safety=True)


def test_crisis_overrides_firm_even_with_style():
    p = empty_profile()
    p["patterns"]["procrastination"] = {"count": 9, "last_seen": None, "evidence": []}
    c = Coach(OfflineLLM(), p)
    _, res = c.respond("I keep putting it off and I want to kill myself")
    assert res["stance"] == "SAFETY" and res["firm_pattern"] is None
    ctx = c.llm.last_messages[-2]["content"]
    assert "FIRM PATTERN" not in ctx and "SAFETY RESOURCES" in ctx


def test_voice_profile_no_cloning_and_providers():
    from keel.tts import voice_profile
    vp = voice_profile()
    assert vp["no_cloning"] is True and "NOT supported" in vp["_doc"]
    assert vp["providers"]["openai"]["voice"] == "onyx" and "Canadian" in vp["character"]["accent"]
    assert "clon" in vp["providers"]["elevenlabs"]["voice"].lower()


def test_ssml_prosody_emphasis_on_short_lines():
    out = to_ssml("Well, think about it this way, it builds and builds over a long sentence. That's not wise.")
    assert 'rate="85%"' in out and 'rate="92%"' in out


def test_readme_states_no_voice_cloning():
    assert "no voice cloning" in load_text("README.md").lower()
