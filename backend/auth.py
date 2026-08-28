from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt
import os

from dotenv import load_dotenv

from database import get_db


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# PASSWORD FUNCTIONS
# =========================================================

def hash_password(password: str) -> str:

    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    hashed_password: str
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# =========================================================
# REQUEST MODELS
# =========================================================

class SignupRequest(BaseModel):

    name: str
    email: str
    password: str


class LoginRequest(BaseModel):

    email: str
    password: str


# =========================================================
# SIGNUP
# =========================================================

@router.post("/signup")
def signup(data: SignupRequest):

    conn = get_db()
    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # CLEAN INPUT
        # -------------------------------------------------

        name = data.name.strip()
        email = data.email.strip().lower()
        password = data.password


        # -------------------------------------------------
        # BASIC VALIDATION
        # -------------------------------------------------

        if not name:

            raise HTTPException(
                status_code=400,
                detail="Name is required."
            )


        if not email:

            raise HTTPException(
                status_code=400,
                detail="Email is required."
            )


        if not password:

            raise HTTPException(
                status_code=400,
                detail="Password is required."
            )


        # -------------------------------------------------
        # PASSWORD LENGTH
        # -------------------------------------------------

        if len(password.encode("utf-8")) > 72:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Password must be "
                    "72 bytes or shorter."
                )
            )


        if len(password) < 6:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Password must be "
                    "at least 6 characters."
                )
            )


        # -------------------------------------------------
        # CHECK EXISTING USER
        # -------------------------------------------------

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

        else:

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = ?
                """,
                (email,)
            )


        existing_user = cursor.fetchone()


        if existing_user:

            raise HTTPException(
                status_code=400,
                detail=(
                    "An account with this email "
                    "already exists."
                )
            )


        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------

        hashed_password = hash_password(
            password
        )


        # -------------------------------------------------
        # INSERT USER
        # -------------------------------------------------

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password
                )
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    name,
                    email,
                    hashed_password
                )
            )

            user_id = cursor.fetchone()["id"]

        else:

            cursor.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password
                )
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    email,
                    hashed_password
                )
            )

            user_id = cursor.lastrowid


        conn.commit()


    except HTTPException:

        conn.rollback()

        raise


    except Exception as error:

        conn.rollback()

        print(
            "SIGNUP ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create account."
        )


    finally:

        cursor.close()
        conn.close()


    # -----------------------------------------------------
    # SUCCESS RESPONSE
    # -----------------------------------------------------

    return {

        "success": True,

        "message": "Account created successfully.",

        "user": {

            "id": user_id,

            "name": name,

            "email": email

        }

    }


# =========================================================
# LOGIN
# =========================================================

@router.post("/login")
def login(data: LoginRequest):

    conn = get_db()
    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # CLEAN INPUT
        # -------------------------------------------------

        email = data.email.strip().lower()
        password = data.password


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not email or not password:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Email and password "
                    "are required."
                )
            )


        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

        else:

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = ?
                """,
                (email,)
            )


        user = cursor.fetchone()


    except HTTPException:

        raise


    except Exception as error:

        print(
            "LOGIN DATABASE ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to login."
        )


    finally:

        cursor.close()
        conn.close()


    # -----------------------------------------------------
    # USER DOESN'T EXIST
    # -----------------------------------------------------

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )


    # -----------------------------------------------------
    # VERIFY PASSWORD
    # -----------------------------------------------------

    try:

        password_correct = verify_password(
            password,
            user["password"]
        )

    except Exception as error:

        print(
            "PASSWORD VERIFY ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to login."
        )


    if not password_correct:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )


    # -----------------------------------------------------
    # LOGIN SUCCESS
    # -----------------------------------------------------

    return {

        "success": True,

        "message": "Login successful.",

        "user": {

            "id": user["id"],

            "name": user["name"],

            "email": user["email"]

        }

    }