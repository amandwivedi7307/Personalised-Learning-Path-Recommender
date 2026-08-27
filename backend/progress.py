import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import get_db


router = APIRouter()


# =========================================================
# REQUEST MODEL
# =========================================================

class ProgressRequest(BaseModel):

    user_id: int
    course_id: str
    completed: bool


# =========================================================
# SAVE PROGRESS
# =========================================================

@router.post("/progress")
def save_progress(data: ProgressRequest):

    if not data.user_id:
        raise HTTPException(
            status_code=400,
            detail="User ID is required."
        )

    if not data.course_id:
        raise HTTPException(
            status_code=400,
            detail="Course ID is required."
        )

    conn = get_db()
    cursor = conn.cursor()

    try:

        # =================================================
        # POSTGRESQL / NEON
        # =================================================

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                INSERT INTO course_progress
                (
                    user_id,
                    course_id,
                    completed
                )

                VALUES (%s, %s, %s)

                ON CONFLICT (user_id, course_id)

                DO UPDATE SET
                    completed = EXCLUDED.completed
                """,
                (
                    data.user_id,
                    data.course_id,
                    data.completed
                )
            )

        # =================================================
        # SQLITE / LOCAL
        # =================================================

        else:

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

            # ---------------------------------------------
            # UPDATE EXISTING
            # ---------------------------------------------

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

            # ---------------------------------------------
            # CREATE NEW
            # ---------------------------------------------

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

    except Exception as error:

        conn.rollback()

        print("PROGRESS SAVE ERROR:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to save course progress."
        )

    finally:

        cursor.close()
        conn.close()

    return {
        "success": True,
        "message": "Course progress saved successfully.",
        "user_id": data.user_id,
        "course_id": data.course_id,
        "completed": data.completed
    }


# =========================================================
# GET USER PROGRESS
# =========================================================

@router.get("/progress/{user_id}")
def get_progress(user_id: int):

    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="User ID is required."
        )

    conn = get_db()
    cursor = conn.cursor()

    try:

        # =================================================
        # POSTGRESQL / NEON
        # =================================================

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                SELECT course_id, completed
                FROM course_progress
                WHERE user_id = %s
                """,
                (user_id,)
            )

        # =================================================
        # SQLITE / LOCAL
        # =================================================

        else:

            cursor.execute(
                """
                SELECT course_id, completed
                FROM course_progress
                WHERE user_id = ?
                """,
                (user_id,)
            )

        rows = cursor.fetchall()

    except Exception as error:

        print("PROGRESS GET ERROR:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to load course progress."
        )

    finally:

        cursor.close()
        conn.close()

    # =====================================================
    # CREATE PROGRESS DICTIONARY
    # =====================================================

    progress = {}

    for row in rows:

        # Works with SQLite Row and PostgreSQL
        # RealDictCursor
        course_id = str(row["course_id"])

        progress[course_id] = bool(
            row["completed"]
        )

    return {
        "success": True,
        "progress": progress
    }