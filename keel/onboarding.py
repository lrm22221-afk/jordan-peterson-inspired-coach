"""Onboarding: maps values, motivations, burdens, goals.

Structure is *inspired by* the public description of the Self-Authoring Suite (S1):
past (epochs, lessons), present (virtues and faults), future (ideal and feared self).
Questions are original wording.
"""

QUESTIONS = {
    "en": [
        ("name", "What should I call you?", False),
        ("values", "Name 3-5 things that matter most to you, in order (comma-separated).", True),
        ("motivations", "When did you last feel fully engaged, time disappearing? What were you doing?", True),
        ("burdens", "What weighs on you right now: problems you keep avoiding or carrying? (comma-separated)", True),
        ("essential", "Of everything you spend time on, what is truly essential? (comma-separated)", True),
        ("non_essential", "What could you drop or reduce without real loss? (comma-separated)", True),
        ("past.epochs", "Past: split your life into a few chapters. Name the one that still stings, and what it taught you.", False),
        ("present.virtues", "Present: two or three strengths others could rely on (comma-separated).", True),
        ("present.faults", "Present: two or three faults that cost you the most (comma-separated). Be honest.", True),
        ("future.ideal", "Future: in 3-5 years, if things went well because you acted well, what does your life look like?", False),
        ("future.feared", "Future: and if you kept avoiding what you know you should do, where would you end up?", False),
        ("goals", "Name 1-3 goals for the next 3 months (comma-separated).", True),
    ],
    "he": [
        ("name", "איך לקרוא לך?", False),
        ("values", "מה 3–5 הדברים הכי חשובים לך, לפי סדר? (מופרדים בפסיקים)", True),
        ("motivations", "מתי לאחרונה היית שקוע לגמרי והזמן נעלם? מה עשית?", True),
        ("burdens", "מה מכביד עליך עכשיו – בעיות שאתה דוחה או סוחב? (בפסיקים)", True),
        ("essential", "מכל מה שאתה מקדיש לו זמן – מה באמת הכרחי? (בפסיקים)", True),
        ("non_essential", "על מה אפשר לוותר או לצמצם בלי הפסד אמיתי? (בפסיקים)", True),
        ("past.epochs", "עבר: חלק את חייך לכמה פרקים. איזה פרק עדיין צורב, ומה למדת ממנו?", False),
        ("present.virtues", "הווה: 2–3 חוזקות שאחרים יכולים לסמוך עליהן (בפסיקים).", True),
        ("present.faults", "הווה: 2–3 חסרונות שעולים לך הכי ביוקר (בפסיקים). בכנות.", True),
        ("future.ideal", "עתיד: בעוד 3–5 שנים, אם פעלת נכון – איך נראים חייך?", False),
        ("future.feared", "עתיד: ואם תמשיך להתחמק ממה שאתה יודע שצריך – לאן תגיע?", False),
        ("goals", "1–3 מטרות לשלושת החודשים הקרובים (בפסיקים).", True),
    ],
}


def _set(profile, key, value):
    if "." in key:
        a, b = key.split(".", 1)
        profile.setdefault(a, {})[b] = value
    else:
        profile[key] = value


def apply_answer(profile: dict, key: str, answer: str, is_list: bool) -> None:
    answer = answer.strip()
    if is_list:
        value = [x.strip() for x in answer.replace("،", ",").split(",") if x.strip()]
    else:
        value = answer
    _set(profile, key, value)


def run(profile: dict, ask=input, say=print, lang: str = "en") -> dict:
    profile["language"] = lang
    say("Let's map where you stand. Short honest answers beat long polished ones. (Enter to skip)"
        if lang == "en" else "בוא נמפה איפה אתה עומד. תשובה קצרה וכנה עדיפה על ארוכה ומלוטשת. (Enter לדילוג)")
    for key, q, is_list in QUESTIONS[lang]:
        ans = ask(f"\n{q}\n> ")
        if ans and ans.strip():
            apply_answer(profile, key, ans, is_list)
    profile["onboarded"] = True
    return profile


def summary(profile: dict) -> str:
    f = profile.get("future", {})
    pr = profile.get("present", {})
    lines = [
        f"Name: {profile.get('name') or '-'}",
        f"Values (ranked): {', '.join(profile.get('values', [])) or '-'}",
        f"Motivations: {', '.join(profile.get('motivations', [])) or '-'}",
        f"Burdens: {', '.join(profile.get('burdens', [])) or '-'}",
        f"Essential: {', '.join(profile.get('essential', [])) or '-'}",
        f"Non-essential: {', '.join(profile.get('non_essential', [])) or '-'}",
        f"Virtues: {', '.join(pr.get('virtues', [])) or '-'} | Faults: {', '.join(pr.get('faults', [])) or '-'}",
        f"Past lesson: {profile.get('past', {}).get('epochs', '-')}",
        f"Ideal future: {f.get('ideal') or '-'}",
        f"Feared future: {f.get('feared') or '-'}",
        f"Goals: {', '.join(profile.get('goals', [])) or '-'}",
    ]
    return "\n".join(lines)
