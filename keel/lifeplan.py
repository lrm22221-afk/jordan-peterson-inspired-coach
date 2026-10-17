"""Life plan builder: Past -> Present -> Future (ideal vs feared) -> goals -> concrete plans.

Modeled on the publicly described structure of Peterson's writing program (S1: past authoring,
present faults/virtues, future authoring) and B2 Rule 2 ('Imagine who you could be...') and
Rule 9 (write old upsetting memories down). Question wording is original.
"""
from .progress import add_commitment

GOAL_QUESTIONS = {
    "en": [
        ("why", "Why does '{g}' matter? Which of your values does it serve, and who besides you benefits?"),
        ("obstacles", "What will most likely stop you, including things in yourself? (comma-separated)"),
        ("counter", "For the biggest obstacle: what will you do when it shows up?"),
        ("milestones", "What would solid progress look like in 4 weeks? In 12? (comma-separated)"),
        ("first_step", "What is the smallest step toward it you will certainly do in the next 7 days?"),
    ],
    "he": [
        ("why", "למה '{g}' חשוב? איזה מהערכים שלך הוא משרת, ומי מלבדך מרוויח?"),
        ("obstacles", "מה הכי סביר שיעצור אותך, כולל דברים בתוכך? (בפסיקים)"),
        ("counter", "למכשול הגדול ביותר: מה תעשה כשהוא יופיע?"),
        ("milestones", "איך נראית התקדמות טובה בעוד 4 שבועות? 12? (בפסיקים)"),
        ("first_step", "מה הצעד הקטן ביותר שתעשה בוודאות ב-7 הימים הקרובים?"),
    ],
}


def plan_goals(profile: dict, ask=input, lang: str = "en") -> list:
    plans = []
    for g in profile.get("goals", [])[:3]:
        plan = {"goal": g}
        for key, q in GOAL_QUESTIONS[lang]:
            ans = (ask(f"\n{q.format(g=g)}\n> ") or "").strip()
            plan[key] = [x.strip() for x in ans.split(",") if x.strip()] if key in ("obstacles", "milestones") else ans
        if plan.get("first_step"):
            add_commitment(profile, plan["first_step"], days=7)
        plans.append(plan)
    profile["life_plan"] = plans
    return plans


def render_markdown(profile: dict) -> str:
    f, pr, past = profile.get("future", {}), profile.get("present", {}), profile.get("past", {})
    out = [f"# Life plan: {profile.get('name') or 'me'}", "",
           "_Built with Keel, an unofficial coach inspired by Jordan B. Peterson's ideas. Not therapy._", "",
           "## Values (ranked)", *[f"{i+1}. {v}" for i, v in enumerate(profile.get("values", []))], "",
           "## Past: lesson still being learned", past.get("epochs", "-") or "-", "",
           "## Present",
           f"- Virtues: {', '.join(pr.get('virtues', [])) or '-'}",
           f"- Faults to work on: {', '.join(pr.get('faults', [])) or '-'}",
           f"- Essential: {', '.join(profile.get('essential', [])) or '-'}",
           f"- Drop/reduce: {', '.join(profile.get('non_essential', [])) or '-'}", "",
           "## Future", f"**Aim at:** {f.get('ideal') or '-'}", "", f"**Avoid:** {f.get('feared') or '-'}", "",
           "## Goals and plans"]
    for p in profile.get("life_plan", []):
        out += [f"### {p['goal']}", f"- Why: {p.get('why') or '-'}",
                f"- Obstacles: {', '.join(p.get('obstacles', [])) or '-'}",
                f"- When it shows up: {p.get('counter') or '-'}",
                f"- Milestones: {', '.join(p.get('milestones', [])) or '-'}",
                f"- **Smallest next step (7 days):** {p.get('first_step') or '-'}", ""]
    out += ["## Rule of progress", "Compare yourself to who you were yesterday. Keep the step small enough to keep; "
            "raise it slightly after three kept commitments in a row."]
    return "\n".join(out)
