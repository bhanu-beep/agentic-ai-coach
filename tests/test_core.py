import pytest

from app import core, db


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Every test gets its own empty temporary database."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.seed_db()


def test_score_answers_range():
    scores = core.score_answers([1, 1, 5, 5, 3, 3, 4, 2, 5, 1])
    assert scores["openness"] == 0.0
    assert scores["conscientiousness"] == 100.0
    assert all(0 <= v <= 100 for v in scores.values())


def test_score_answers_rejects_bad_input():
    with pytest.raises(ValueError):
        core.score_answers([1, 2, 3])
    with pytest.raises(ValueError):
        core.score_answers([6] * 10)


def test_recommend_picks_lowest_traits():
    scores = {"openness": 10, "conscientiousness": 90, "extraversion": 20,
              "agreeableness": 80, "emotional_stability": 70}
    result = core.recommend(scores)
    assert [r["trait"] for r in result] == ["openness", "extraversion"]


def test_recommend_rejects_unknown_trait():
    with pytest.raises(ValueError):
        core.recommend({"charisma": 50})


def test_progress_for_seeded_user():
    progress = core.fetch_progress(1)
    assert progress["user"] == "Asha"
    assert len(progress["history"]) == 3
    assert progress["change"]["conscientiousness"] == 25.0  # 60 - 35


def test_save_then_read_back():
    scores = core.score_answers([3] * 10)
    core.save_assessment(2, scores)
    assert len(core.fetch_progress(2)["history"]) == 3


def test_unknown_user_raises():
    with pytest.raises(ValueError):
        core.fetch_progress(999)