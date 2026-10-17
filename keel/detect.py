"""Rule-based detectors: safety signals, role-play scenarios, behaviour patterns."""
import re
from dataclasses import dataclass
from typing import Optional

from .config import load_json


def _compile(pats):
    return [re.compile(p, re.IGNORECASE) for p in pats]


@dataclass
class SafetyResult:
    crisis: bool = False
    abuse: bool = False

    @property
    def any(self):
        return self.crisis or self.abuse


class Detector:
    def __init__(self, safety=None, triggers=None, patterns=None):
        self.safety_cfg = safety or load_json("config/safety.json")
        self.trig_cfg = triggers or load_json("config/roleplay_triggers.json")
        self.pat_cfg = patterns or load_json("config/patterns.json")
        self._crisis = _compile(self.safety_cfg["crisis_patterns"])
        self._abuse = _compile(self.safety_cfg["abuse_patterns"])
        self._scen = sorted(
            [(s, _compile(s["patterns"])) for s in self.trig_cfg["scenarios"]],
            key=lambda x: -x[0]["priority"],
        )
        self._pats = [(p, _compile(p["regex"])) for p in self.pat_cfg["patterns"]]
        self.firm_threshold = self.pat_cfg.get("firm_threshold", 2)

    def safety(self, text: str) -> SafetyResult:
        return SafetyResult(
            crisis=any(r.search(text) for r in self._crisis),
            abuse=any(r.search(text) for r in self._abuse),
        )

    def roleplay(self, text: str) -> Optional[dict]:
        for scen, regs in self._scen:
            if any(r.search(text) for r in regs):
                return scen
        return None

    def patterns(self, text: str) -> list:
        return [p for p, regs in self._pats if any(r.search(text) for r in regs)]

    def pattern_by_id(self, pid: str) -> Optional[dict]:
        return next((p for p, _ in self._pats if p["id"] == pid), None)
