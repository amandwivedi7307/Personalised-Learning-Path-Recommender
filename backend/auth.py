from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt
import secrets
import time
import os

from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from database import get_db


load_dotenv()
router = APIRouter()
# =========================
# EMAIL CONFIGURATION
# =========================

mail_config = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),

    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),

    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,

    USE_CREDENTIALS=True,
)



fm = FastMail(mail_config)



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

class ForgotPasswordRequest(BaseModel):

    email: str


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
# =========================
# FORGOT PASSWORD
# =========================


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):

    conn = get_db()
    cursor = conn.cursor()

    # =========================
    # FIND USER
    # =========================

    cursor.execute(
        """
        SELECT id, email
        FROM users
        WHERE email = ?
        """,
        (data.email,)
    )

    user = cursor.fetchone()

    # =========================
    # SECURITY
    # =========================

    if not user:

        conn.close()

        return {
            "success": True,
            "message": (
                "If an account exists with this email, "
                "a recovery email has been sent."
            )
        }

    # =========================
    # GENERATE TEMPORARY PASSWORD
    # =========================

    temporary_password = secrets.token_urlsafe(8)

    # =========================
    # HASH TEMPORARY PASSWORD
    # =========================

    hashed_password = hash_password(
        temporary_password
    )

    # =========================
    # GENERATE RESET TOKEN
    # =========================

    reset_token = secrets.token_urlsafe(32)

    # Token valid for 15 minutes
    reset_token_expiry = time.time() + (15 * 60)

    # =========================
    # SAVE PASSWORD + TOKEN
    # =========================

    cursor.execute(
        """
        UPDATE users
        SET
            password = ?,
            reset_token = ?,
            reset_token_expiry = ?
        WHERE id = ?
        """,
        (
            hashed_password,
            reset_token,
            reset_token_expiry,
            user["id"]
        )
    )

    conn.commit()
    conn.close()

    # =========================
    # RESET LINK
    # =========================

    reset_link = (
        "http://localhost:5173/reset-password/"
        + reset_token
    )

    # =========================
    # SEND EMAIL
    # =========================

    message = MessageSchema(
        subject="SkillRoute AI - Password Recovery",

        recipients=[user["email"]],

        body=f"""
Hello,

We received a request to recover your SkillRoute AI account.

Your temporary password is:

{temporary_password}

You can use this temporary password to login.

You can also create a new password using the link below:

{reset_link}

This reset link will expire in 15 minutes.

If you did not request a password recovery,
you can safely ignore this email.

Regards,
SkillRoute AI Team
""",

        subtype="plain"
    )

    # =========================
    # SEND EMAIL
    # =========================

    await fm.send_message(message)

    # =========================
    # RESPONSE
    # =========================

    return {
        "success": True,
        "message": (
            "If this email is registered, "
            "a recovery email has been sent."
        )
    }

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest):

    conn = get_db()
    cursor = conn.cursor()

    # Find token
    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE reset_token = ?
        AND reset_token_expiry > ?
        """,
        (
            data.token,
            time.time()
        )
    )

    user = cursor.fetchone()

    if not user:
        conn.close()

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset link."
        )

    # Password length check
    if len(data.new_password.encode("utf-8")) > 72:

        conn.close()

        raise HTTPException(
            status_code=400,
            detail="Password must be 72 bytes or shorter."
        )

    # Hash new password
    hashed_password = hash_password(
        data.new_password
    )

    # Update password + remove token
    cursor.execute(
        """
        UPDATE users
        SET
            password = ?,
            reset_token = NULL,
            reset_token_expiry = NULL
        WHERE id = ?
        """,
        (
            hashed_password,
            user["id"]
        )
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Password reset successfully."
    }
