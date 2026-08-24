import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "haic_app.db"
VALID_ACTION_IDS = {1, 2, 3}


def save_user_evaluation(
    insight_id: int,
    user_action_id: int,
    decision_time_ms: int,
    edited_text: str | None = None,
) -> bool:
    """Save one final evaluation for an individual database insight."""
    if user_action_id not in VALID_ACTION_IDS:
        raise ValueError("The evaluation action must be Accept, Reject, or Edit.")
    if not isinstance(decision_time_ms, int) or decision_time_ms < 0:
        raise ValueError("Decision time must be a non-negative integer.")

    if user_action_id == 3:
        if not isinstance(edited_text, str) or not edited_text.strip():
            raise ValueError("Edited text is required when Edit is selected.")
        final_edit = edited_text.strip()
    else:
        final_edit = None

    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO Evaluations (
                insight_ID,
                user_ActionID,
                edited_Text,
                decision_Time_ms
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                insight_id,
                user_action_id,
                final_edit,
                decision_time_ms,
            ),
        )
        conn.commit()
        return True

    except sqlite3.IntegrityError as error:
        conn.rollback()
        print(f"The evaluation was not saved: {error}")
        return False

    except sqlite3.Error as error:
        conn.rollback()
        print(f"Failed to save evaluation: {error}")
        return False

    finally:
        conn.close()