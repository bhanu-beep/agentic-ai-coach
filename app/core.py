"""Plain Python logic. No AI here - just normal functions we can test easily.
The agent will call these through thin 'tool' wrappers (see tools.py)."""
from . import db

TRAITS = ["openness", "conscientiousness", "extraversion", "agreeableness", "emotional_stability"]

TIPS = {
    "openness": [
        "Try one new thing each week (a new topic, route, or hobby).",
        "Read or watch something outside your usual interests for 15 minutes a day.",
    ],
    "conscientiousness": [
        "Plan tomorrow's top 3 tasks every night.",
        "Use 25-minute focus blocks with a 5-minute break.",
    ],
    "extraversion": [
        "Start one short conversation with a new person each day.",
        "Volunteer to speak or ask a question once in every meeting or class.",
    ],
    "agreeableness": [
        "Practice active listening: repeat back what you heard before replying.",
        "Give one sincere compliment or thank-you every day.",
    ],
    "emotional_stability": [
        "Try 5 minutes of slow breathing or a short walk when stressed.",
        "Write down 3 things that went well at the end of each day.",
    ],
}


def score_answers(answers: list[int]) -> dict[str, float]:
    """10 answers (each 1-5) -> 5 trait scores (each 0-100). Two questions per trait."""
    if len(answers) != 10:
        raise ValueError("Exactly 10 answers are required.")
    if any(a < 1 or a > 5 for a in answers):
        raise ValueError("Every answer must be a whole number from 1 to 5.")
    scores = {}
    for i, trait in enumerate(TRAITS):
        avg = (answers[2 * i] + answers[2 * i + 1]) / 2  # 1.0 .. 5.0
        scores[trait] = round((avg - 1) / 4 * 100, 1)    # 0 .. 100
    return scores


def save_assessment(user_id: int, scores: dict[str, float]) -> int:
    with db.get_conn() as conn:
        if conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone() is None:
            raise ValueError(f"User {user_id} does not exist.")
        cur = conn.execute(
            "INSERT INTO assessments (user_id, openness, conscientiousness, extraversion,"
            " agreeableness, emotional_stability) VALUES (?,?,?,?,?,?)",
            (user_id, *[scores[t] for t in TRAITS]),
        )
        return cur.lastrowid


def recommend(scores: dict[str, float], how_many: int = 2) -> list[dict]:
    """Pick the lowest-scoring traits and return simple, rule-based tips for them."""
    unknown = set(scores) - set(TRAITS)
    if unknown:
        raise ValueError(f"Unknown traits: {sorted(unknown)}. Use only: {TRAITS}")
    lowest = sorted(scores, key=lambda t: scores[t])[:how_many]
    return [{"trait": t, "score": scores[t], "tips": TIPS[t]} for t in lowest]


def fetch_progress(user_id: int, limit: int = 5) -> dict:
    """Latest assessments (newest first) plus how each trait changed from oldest to newest."""
    with db.get_conn() as conn:
        user = conn.execute("SELECT name FROM users WHERE id = ?", (user_id,)).fetchone()
        if user is None:
            raise ValueError(f"User {user_id} does not exist.")
        rows = conn.execute(
            "SELECT created_at, " + ", ".join(TRAITS) + " FROM assessments"
            " WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    history = [dict(r) for r in rows]
    if not history:
        return {"user": user["name"], "history": [], "change": {}, "note": "No assessments yet."}
    newest, oldest = history[0], history[-1]
    change = {t: round(newest[t] - oldest[t], 1) for t in TRAITS}
    return {"user": user["name"], "history": history, "change": change}