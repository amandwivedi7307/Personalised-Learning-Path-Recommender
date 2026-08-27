from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import get_db


router = APIRouter()


# =========================
# REQUEST MODEL
# =========================

class ProgressRequest(BaseModel):

    user_id: int
    course_id: str
    completed: bool


# =========================
# SAVE PROGRESS
# =========================

@router.post("/progress")
def save_progress(data: ProgressRequest):

    conn = get_db()
    cursor = conn.cursor()

    # Check whether progress already exists
    cursor.execute(
        """
        SELECT id
        FROM course_progress
        WHERE user_id = ?
        AND course_id = ?
        """,
        (
            data.user_id,
            data.course_id
        )
    )

    existing = cursor.fetchone()


    # =========================
    # UPDATE EXISTING
    # =========================

    if existing:

        cursor.execute(
            """
            UPDATE course_progress

            SET completed = ?

            WHERE user_id = ?
            AND course_id = ?
            """,
            (
                data.completed,
                data.user_id,
                data.course_id
            )
        )


    # =========================
    # CREATE NEW
    # =========================

    else:

        cursor.execute(
            """
            INSERT INTO course_progress
            (
                user_id,
                course_id,
                completed
            )

            VALUES (?, ?, ?)
            """,
            (
                data.user_id,
                data.course_id,
                data.completed
            )
        )


    conn.commit()
    conn.close()


    return {
        "success": True,
        "message": "Course progress saved successfully."
    }


# =========================
# GET USER PROGRESS
# =========================

@router.get("/progress/{user_id}")
def get_progress(user_id: int):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT course_id, completed
        FROM course_progress
        WHERE user_id = ?
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()


    progress = {}

    for row in rows:

        progress[str(row["course_id"])] = bool(
            row["completed"]
        )


    return {
        "success": True,
        "progress": progress
    }