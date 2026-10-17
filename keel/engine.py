"""Conversation engine: detects safety / patterns / role-play, picks a stance, builds context."""
from .config import load_text, load_json, principles
from .detect import Detector
from .profile import record_pattern
from .progress import open_commitments, level_guide


class Coach:
    def __init__(self, llm, profile: dict, detector: Detector = None, max_history: int = 16):
        self.llm = llm
        self.profile = profile
        self.det = detector or Detector()
        self.principles = principles()
        self.safety_cfg = load_json("config/safety.json")
        lang = profile.get("language", "en")
        self.system = load_text(f"persona/system_prompt.{lang}.md") + "\n\n" + load_text("knowledge/communication.md")
        self.history = []
        self.max_history = max_history
        self.roleplay_offered = set()

    # ---- decision ----
    def analyze(self, text: str) -> dict:
        safety = self.det.safety(text)
        res = {"stance": "NORMAL", "safety": safety, "patterns": [], "firm_pattern": None, "roleplay": None}
        if safety.any:
            res["stance"] = "SAFETY"
            return res  # no pattern counting or confrontation in crisis
        hits = self.det.patterns(text)
        for p in hits:
            n = record_pattern(self.profile, p["id"], text)
            res["patterns"].append((p["id"], n))
            if n >= self.det.firm_threshold and res["firm_pattern"] is None:
                res["firm_pattern"] = p
        scen = self.det.roleplay(text)
        if scen and scen["id"] not in self.roleplay_offered:
            res["roleplay"] = scen
        if res["firm_pattern"]:
            res["stance"] = "FIRM"
        elif res["roleplay"]:
            res["stance"] = "ROLEPLAY"
        return res

    def context_block(self, res: dict) -> str:
        p = self.profile
        lines = ["CONTEXT (controller, not user)", f"STANCE: {res['stance']}",
                 f"User: {p.get('name') or '-'}; values: {', '.join(p.get('values', [])[:5]) or '-'}",
                 f"Goals: {', '.join(p.get('goals', [])) or '-'}; burdens: {', '.join(p.get('burdens', [])[:5]) or '-'}",
                 f"Aim (ideal future): {p.get('future', {}).get('ideal', '')[:200] or '-'}",
                 f"Difficulty level {p['progress']['level']}: next step should be {level_guide(p['progress']['level'])}",
                 f"Streak: {p['progress']['streak']} kept in a row"]
        oc = open_commitments(p)
        if oc:
            lines.append("Open commitments: " + "; ".join(c["text"] for c in oc[-3:]))
        recurring = [k for k, v in p["patterns"].items() if v["count"] >= self.det.firm_threshold]
        if recurring:
            lines.append("Recurring patterns on record: " + ", ".join(recurring))
        if res["stance"] == "SAFETY":
            lang = p.get("language", "en")
            lines.append("SAFETY RESOURCES: " + self.safety_cfg["resources"][lang])
            if res["safety"].abuse:
                lines.append("Abuse signal: prioritise physical safety; do not coach confrontation.")
        if res["firm_pattern"]:
            fp = res["firm_pattern"]
            pr = [self.principles[i] for i in fp["principles"] if i in self.principles]
            lines.append(f"FIRM PATTERN: {fp['label']} (seen {p['patterns'][fp['id']]['count']}x)")
            lines.append("Principles: " + " | ".join(f"{x['title']} [{','.join(x['sources'])}]: {x['summary']}" for x in pr))
            lines.append("Guidance: " + fp["firm_response"])
            lines.append("Demand ONE smallest concrete step with a deadline; say you'll check it next session.")
        if res["roleplay"]:
            r = res["roleplay"]
            lines.append(f"ROLEPLAY SCENARIO: {r['id']}. Offer a short rehearsal where you play {r['other_role']} "
                         "realistically; user may type 'skip'. Afterwards debrief: one thing that worked, one to try.")
        return "\n".join(lines)

    # ---- turn ----
    def respond(self, text: str) -> tuple:
        res = self.analyze(text)
        if res["roleplay"]:
            self.roleplay_offered.add(res["roleplay"]["id"])
        msgs = [{"role": "system", "content": self.system}] + self.history[-self.max_history:]
        msgs += [{"role": "system", "content": self.context_block(res)}, {"role": "user", "content": text}]
        reply = self.llm.chat(msgs)
        self.history += [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
        return reply, res
