from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt

from database import get_db


router = APIRouter()


# =========================
# PASSWORD FUNCTIONS
# =========================

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    """
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify entered password against stored hash.
    """
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# =========================
# REQUEST MODELS
# =========================

class SignupRequest(BaseModel):

    name: str
    email: str
    password: str


class LoginRequest(BaseModel):

    email: str
    password: str


# =========================
# SIGNUP
# =========================

@router.post("/signup")
def signup(data: SignupRequest):

    conn = get_db()
    cursor = conn.cursor()

    # Check existing user
    cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        (data.email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:

        conn.close()

        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists."
        )

    # Check password length
    if len(data.password.encode("utf-8")) > 72:

        conn.close()

        raise HTTPException(
            status_code=400,
            detail="Password must be 72 bytes or shorter."
        )

    # Hash password
    hashed_password = hash_password(data.password)

    # Save user
    cursor.execute(
        """
        INSERT INTO users
        (name, email, password)
        VALUES (?, ?, ?)
        """,
        (
            data.name,
            data.email,
            hashed_password
        )
    )

    conn.commit()

    user_id = cursor.lastrowid

    conn.close()

    return {
        "success": True,
        "message": "Account created successfully.",
        "user": {
            "id": user_id,
            "name": data.name,
            "email": data.email
        }
    }


# =========================
# LOGIN
# =========================

@router.post("/login")
def login(data: LoginRequest):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (data.email,)
    )

    user = cursor.fetchone()

    conn.close()

    # User doesn't exist
    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # Verify password
    password_correct = verify_password(
        data.password,
        user["password"]
    )

    if not password_correct:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return {
        "success": True,
        "message": "Login successful.",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }