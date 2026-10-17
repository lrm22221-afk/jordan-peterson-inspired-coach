"""Keel CLI. Run: python -m keel [--lang he] [--offline] [--profile PATH]"""
import argparse
import sys

from . import onboarding, lifeplan
from .config import load_json
from .engine import Coach
from .llm import OfflineLLM, OpenAICompatLLM, LLMError
from .profile import ProfileStore, checkin_due
from .progress import open_commitments, resolve, add_commitment
from .tts import to_ssml

DISCLAIMER = ("Keel is an unofficial AI coaching tool inspired by Jordan B. Peterson's published ideas. "
              "It is not affiliated with or endorsed by him, and it is not therapy or medical advice.")
HELP = "/plan  build or rebuild your life plan | /commit <step>  record a step | /checkin | /profile | /export | /quit"


def weekly_checkin(profile, ask=input, say=print):
    oc = open_commitments(profile)
    if not oc:
        say("No open commitments. What's one small step for this week? (/commit <step>)")
        return
    for c in oc:
        a = (ask(f"\nDid you do: '{c['text']}'? [y/n] > ") or "").strip().lower()
        if a.startswith(("y", "כ")):
            resolve(profile, c["id"], True)
            say("Good. Kept.")
        elif a.startswith(("n", "ל")):
            resolve(profile, c["id"], False)
            say("Noted, not a verdict. The step was too big for last week. We'll halve it.")
    pr = profile["progress"]
    say(f"Streak: {pr['streak']} (best {pr['best_streak']}), level {pr['level']}, kept {pr['kept']}/{pr['kept']+pr['missed']}.")


def build_plan(profile, store, ask=input, say=print):
    lang = profile.get("language", "en")
    onboarding.run(profile, ask=ask, say=say, lang=lang)
    lifeplan.plan_goals(profile, ask=ask, lang=lang)
    store.save(profile)
    out = store.path.parent / "life_plan.md"
    out.write_text(lifeplan.render_markdown(profile), encoding="utf-8")
    say(f"\nLife plan saved to {out}")


def main(argv=None, ask=input, say=print, llm=None):
    ap = argparse.ArgumentParser(prog="keel", description=DISCLAIMER)
    ap.add_argument("--lang", choices=["en", "he"])
    ap.add_argument("--offline", action="store_true", help="no API calls (demo/testing)")
    ap.add_argument("--tts", action="store_true", help="also print SSML with pause markers for text-to-speech")
    ap.add_argument("--profile", help="path to profile JSON (default ~/.keel/profile.json)")
    args = ap.parse_args(argv)

    store = ProfileStore(args.profile)
    profile = store.load()
    if args.lang:
        profile["language"] = args.lang
    try:
        llm = llm or (OfflineLLM() if args.offline else OpenAICompatLLM())
    except LLMError as e:
        say(str(e))
        return 2
    say(DISCLAIMER)
    if not profile["onboarded"]:
        build_plan(profile, store, ask, say)
    profile["sessions"] += 1
    if checkin_due(profile):
        say("\nIt's been a week. Weekly check-in:")
        weekly_checkin(profile, ask, say)
    elif open_commitments(profile):
        say("\nOpen: " + "; ".join(c["text"] for c in open_commitments(profile)))
    store.save(profile)
    coach = Coach(llm, profile)
    safety = load_json("config/safety.json")["resources"][profile.get("language", "en")]
    say(HELP)
    while True:
        try:
            text = ask("\nyou> ")
        except (EOFError, KeyboardInterrupt):
            break
        if text is None:
            break
        text = text.strip()
        if not text:
            continue
        if text in ("/quit", "/exit"):
            break
        if text == "/profile":
            say(onboarding.summary(profile)); continue
        if text == "/plan":
            build_plan(profile, store, ask, say); continue
        if text == "/checkin":
            weekly_checkin(profile, ask, say); store.save(profile); continue
        if text == "/export":
            out = store.path.parent / "life_plan.md"
            out.write_text(lifeplan.render_markdown(profile), encoding="utf-8"); say(f"Saved {out}"); continue
        if text.startswith("/commit "):
            c = add_commitment(profile, text[8:]); store.save(profile)
            say(f"Recorded: '{c['text']}'. I'll ask about it next session."); continue
        try:
            reply, res = coach.respond(text)
        except LLMError as e:
            say(f"(error) {e}"); continue
        if res["stance"] == "SAFETY":
            say("\n" + safety)  # always shown, independent of the model
        say(f"\nkeel> {reply}")
        if args.tts:
            say(to_ssml(reply, safety=res["stance"] == "SAFETY"))
        store.save(profile)
    store.save(profile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
