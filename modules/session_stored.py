import json
import math
import sqlite3
import uuid
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "haic_app.db"

ALLOWED_INSIGHT_TYPES = {
    "KPI Performance",
    "Anomaly / Risk",
    "Data Quality / Limitation",
}


def _make_json_safe(value):
    """Convert nested EDA values into standards-compliant JSON values."""
    if isinstance(value, dict):
        return {
            str(key): _make_json_safe(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_make_json_safe(item) for item in value]
    if hasattr(value, "item") and callable(value.item):
        return _make_json_safe(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _validate_insights(insights: list[dict]) -> None:
    """Defensively validate insights before starting a database transaction."""
    if not isinstance(insights, list) or len(insights) != 3:
        raise ValueError("Exactly three validated insights are required.")

    insight_numbers = []

    for insight in insights:
        if not isinstance(insight, dict):
            raise ValueError("Each insight must be a dictionary.")

        insight_number = insight.get("insight_id")
        insight_type = insight.get("type")
        title = insight.get("title")
        narrative = insight.get("narrative")

        if type(insight_number) is not int:
            raise ValueError("Each insight ID must be an integer.")
        if insight_type not in ALLOWED_INSIGHT_TYPES:
            raise ValueError(f"Unsupported insight type: {insight_type!r}.")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Each insight must have a non-empty title.")
        if not isinstance(narrative, str) or not narrative.strip():
            raise ValueError("Each insight must have a non-empty narrative.")

        insight_numbers.append(insight_number)

    if insight_numbers != [1, 2, 3]:
        raise ValueError("Insight IDs must be exactly 1, 2, and 3 in order.")


def save_completed_analysis(
    participant_id: str,
    dataset_name: str,
    domain: str,
    audience: str,
    goal: str,
    eda_package: dict,
    insights: list[dict],
    generation_time_ms: int,
) -> dict:
    """Save one completed analysis and return its database identifiers.

    Nothing is retained when one of the inserts fails.
    """
    _validate_insights(insights)

    if not isinstance(generation_time_ms, int) or generation_time_ms < 0:
        raise ValueError("Generation time must be a non-negative integer.")

    eda_json = json.dumps(
        _make_json_safe(eda_package),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    )
    session_id = str(uuid.uuid4())

    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO Sessions (
                session_ID,
                participant_ID,
                dataset_name,
                domain_Chosen,
                target_Audience,
                analysis_goal
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                participant_id.strip(),
                dataset_name.strip(),
                domain,
                audience,
                goal.strip(),
            ),
        )

        cursor.execute(
            """
            INSERT INTO Generations (
                session_ID,
                eda_json,
                generation_Time_ms
            )
            VALUES (?, ?, ?)
            """,
            (session_id, eda_json, generation_time_ms),
        )
        generation_id = cursor.lastrowid

        insight_ids = {}

        for insight in insights:
            insight_number = insight["insight_id"]

            cursor.execute(
                """
                INSERT INTO Insights (
                    generation_ID,
                    insight_number,
                    insight_type,
                    title,
                    analysis_narrative
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    generation_id,
                    insight_number,
                    insight["type"],
                    insight["title"].strip(),
                    insight["narrative"].strip(),
                ),
            )
            insight_ids[insight_number] = cursor.lastrowid

        conn.commit()

        return {
            "session_id": session_id,
            "generation_id": generation_id,
            "insight_ids": insight_ids,
        }

    except (sqlite3.Error, ValueError) as error:
        conn.rollback()
        raise RuntimeError(
            f"The completed analysis could not be saved: {error}"
        ) from error

    finally:
        conn.close()
