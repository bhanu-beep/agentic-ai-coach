"""Thin wrappers that turn our plain functions into tools the LLM can call."""
import functools
import sqlite3
import time

from langchain_core.tools import tool

from . import core
from .schemas import ProgressInput, RecommendationsInput, ScorePersonalityInput


def retry_on_db_error(attempts: int = 3, delay: float = 0.3):
    """If SQLite is briefly busy/locked, wait a little and try again (up to `attempts`)."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except sqlite3.OperationalError:
                    if attempt == attempts:
                        raise
                    time.sleep(delay * attempt)
        return wrapper
    return decorator


@tool(args_schema=ScorePersonalityInput)
@retry_on_db_error()
def score_personality(user_id: int, answers: list[int]) -> dict:
    """Score the user's 10-question personality questionnaire and save the result.
    Use this when the user gives their answers. Never guess scores yourself."""
    scores = core.score_answers(answers)
    assessment_id = core.save_assessment(user_id, scores)
    return {"assessment_id": assessment_id, "scores": scores}


@tool(args_schema=RecommendationsInput)
def generate_recommendations(scores: dict[str, float]) -> list:
    """Give personalised improvement tips for the user's weakest personality traits.
    Use this after you have trait scores (from score_personality or get_progress)."""
    return core.recommend(scores)


@tool(args_schema=ProgressInput)
@retry_on_db_error()
def get_progress(user_id: int, limit: int = 5) -> dict:
    """Look up the user's past assessments and how their scores changed over time.
    Use this for questions about history, progress, or improvement."""
    return core.fetch_progress(user_id, limit)


TOOLS = [score_personality, generate_recommendations, get_progress]