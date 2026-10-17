# jordan-peterson-inspired-coach (Keel)

**Keel** is a command-line AI life coach. Its tone, its way of reasoning and its ideas are **inspired by Jordan B. Peterson's published work**: responsibility, aim, truthful speech, order and chaos, and incremental self-improvement. It builds a complete life plan with you and holds you accountable week by week.

> ⚠️ **Disclaimer.** This is an **unofficial** project. It is **not affiliated with, endorsed by, or connected to Jordan B. Peterson** or his companies. Keel never claims to be him, and it does not quote him beyond short, cited excerpts (`research/transcript_notes.md`). It is **not therapy, counselling or medical advice**. If you are in crisis, contact your local emergency services. In the US you can call or text **988**; in Israel you can call **ERAN 1201**.

## What it does
- **Life plan (central feature).** A guided flow modelled on Peterson's self-authoring idea, with original question wording:
  - **Past:** the chapter that still stings, and its lesson.
  - **Present:** your virtues and your faults.
  - **Future:** the ideal future to aim at and the feared future to avoid.
  - Then 1–3 goals, each with a why, obstacles, counter-moves, milestones and the **smallest next step**.
  - The plan is exported to `~/.keel/life_plan.md`.
- **Values map.** Values, motivations, burdens, and what is essential versus non-essential.
- **Incremental progress.** Every goal and every intervention becomes one small, doable step ("aim high and make the goal difficult but proximal"). Streaks are tracked. The difficulty level goes up after 3 kept commitments in a row and down after a miss.
- **Weekly check-ins** on open commitments.
- **Pattern memory.** Ten recurring patterns are tracked across sessions:
  - procrastination
  - self-deception
  - resentment
  - victim narrative
  - chaos
  - being a pushover
  - aimlessness
  - lying
  - not taking responsibility
  - broken promises

  When a pattern recurs, the coach switches to a **firm, direct, caring stance**. It cites the principle and its source (`config/patterns.json` → `knowledge/principles.json`), asks for one concrete step, and checks on it next session.
- **Dealing with people** is built into every conversation: truth, listening, precision, negotiation, conditions, reciprocity, and saying no. There are ethical limits, including no manipulation (`knowledge/communication.md`).
- **Automatic role-play.** Keel offers a rehearsal, playing the other side, when you mention any of these (triggers in `config/roleplay_triggers.json`):
  - negotiating a raise or a price
  - setting a boundary
  - a conflict with a partner or boss
  - being taken advantage of
  - an upcoming hard conversation
- **Safety first.** Crisis and abuse signals (English and Hebrew) override everything. In that case there is no firmness and no role-play, and crisis resources are always printed (`config/safety.json`).
- **Speech style.** Rhythm, pauses, rhetorical questions, tenderness, and firm-but-loving delivery are grounded in transcript evidence (`persona/speech_style.md`).
- **Optional TTS (`--tts`).** Prints SSML with pause markers and prosody built from `config/voice_profile.json`. The profile describes a deep, mid-low North American (Canadian-neutral) male voice with a measured pace and earnest delivery, and lists settings for OpenAI, ElevenLabs, Azure and Google *stock* voices. **No voice cloning:** this project does not clone, and must not be used to clone, Jordan B. Peterson's voice or any real person's voice.
- **Languages:** English and Hebrew.

## Run
```bash
python3 -m venv .venv && source .venv/bin/activate   # Python 3.9+, no runtime deps
export KEEL_API_KEY=...            # any OpenAI-compatible endpoint
export KEEL_BASE_URL=https://api.openai.com/v1   # optional
export KEEL_MODEL=gpt-4o-mini                    # optional
python -m keel                     # English
python -m keel --lang he           # Hebrew
python -m keel --offline           # demo without API calls
```
In-chat commands: `/plan`, `/commit <step>`, `/checkin`, `/profile`, `/export`, `/quit`.

Your profile is stored locally at `~/.keel/profile.json` with file mode 600. You can change the location with `--profile` or `KEEL_PROFILE`. Nothing is sent anywhere except to the LLM endpoint you configure.

## Tests
```bash
pip install pytest && python -m pytest -q
python tools/verify_quotes.py /path/to/transcripts   # quote verification (transcripts not distributed)
```

## Layout
```
research/                 REPORT.md (Hebrew summary + sources), transcript_notes.md (verified excerpts)
knowledge/                principles.json (27 cited principles), communication.md
persona/                  system_prompt.en.md, system_prompt.he.md
config/                   patterns.json, roleplay_triggers.json, safety.json
keel/                     cli, engine, detect, profile, progress, onboarding, lifeplan, llm
tools/                    verify_quotes.py
tests/                    detection, engine, CLI tests
```

## License
MIT. See `LICENSE`. "Jordan Peterson" is used only descriptively, to credit the source of the ideas.
