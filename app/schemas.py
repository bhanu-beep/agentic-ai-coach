"""Pydantic models describe (and validate) the inputs each tool accepts.
The LLM sees these descriptions, and bad inputs are rejected before our code runs."""
from pydantic import BaseModel, Field


class ScorePersonalityInput(BaseModel):
    user_id: int = Field(ge=1, description="The id of the current user.")
    answers: list[int] = Field(
        min_length=10,
        max_length=10,
        description="Exactly 10 answers to the questionnaire, each a whole number from 1 to 5.",
    )


class RecommendationsInput(BaseModel):
    scores: dict[str, float] = Field(
        description=(
            "Trait scores from 0 to 100. Allowed keys: openness, conscientiousness, "
            "extraversion, agreeableness, emotional_stability."
        )
    )


class ProgressInput(BaseModel):
    user_id: int = Field(ge=1, description="The id of the current user.")
    limit: int = Field(default=5, ge=1, le=20, description="How many recent assessments to return.")