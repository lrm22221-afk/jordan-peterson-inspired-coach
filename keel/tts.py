"""Optional TTS output: SSML with pause markers and prosody from config/voice_profile.json.

Stock voices only. Voice cloning of Jordan B. Peterson (or any real person) is NOT supported.
"""
import html
import re

from .config import load_json


def voice_profile() -> dict:
    vp = load_json("config/voice_profile.json")
    assert vp.get("no_cloning") is True, "voice cloning is not allowed"
    return vp


def _prosody(text: str, p: dict) -> str:
    attrs = " ".join(f'{k}="{v}"' for k, v in p.items())
    return f"<prosody {attrs}>{text}</prosody>"


def to_ssml(text: str, safety: bool = False) -> str:
    vp = voice_profile()["ssml"]
    b = vp["breaks"]
    eb, db, pb = (b["safety_ellipsis"], b["safety_dash"], b["safety_paragraph"]) if safety else (b["ellipsis"], b["dash"], b["paragraph"])
    paras = [x.strip() for x in re.split(r"\n\s*\n", text.strip()) if x.strip()]
    out = []
    for para in paras:
        t = html.escape(para)
        t = t.replace("...", f' <break time="{eb}"/> ').replace("…", f' <break time="{eb}"/> ')
        t = t.replace("—", f' <break time="{db}"/> ')
        t = re.sub(r"\s+", " ", t).strip()
        if safety:
            out.append(_prosody(t, vp["safety"]))
        else:
            # short landing lines (<= 6 words) are delivered slower and lower for emphasis
            sents = re.split(r"(?<=[.?!])\s+", t)
            out.append(" ".join(_prosody(s, vp["emphasis"]) if len(re.sub(r"<[^>]+>", "", s).split()) <= 6
                                else _prosody(s, vp["base"]) for s in sents))
    return "<speak>" + f' <break time="{pb}"/> '.join(out) + "</speak>"
