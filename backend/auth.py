from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

import bcrypt
import os
import time
import secrets
import requests

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


class ForgotPasswordRequest(BaseModel):

    email: str


class ResetPasswordRequest(BaseModel):

    token: str
    password: str


# =========================================================
# SIGNUP
# =========================================================

@router.post("/signup")
def signup(data: SignupRequest):

    conn = get_db()
    cursor = conn.cursor()

    try:

        name = data.name.strip()
        email = data.email.strip().lower()
        password = data.password

        # -------------------------------------------------
        # VALIDATION
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

        if len(password.encode("utf-8")) > 72:

            raise HTTPException(
                status_code=400,
                detail="Password must be 72 bytes or shorter."
            )

        if len(password) < 6:

            raise HTTPException(
                status_code=400,
                detail="Password must be at least 6 characters."
            )

        # -------------------------------------------------
        # CHECK USER
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
                detail="An account with this email already exists."
            )

        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------

        hashed_password = hash_password(password)

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

        email = data.email.strip().lower()
        password = data.password

        if not email or not password:

            raise HTTPException(
                status_code=400,
                detail="Email and password are required."
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

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

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

    return {

        "success": True,

        "message": "Login successful.",

        "user": {

            "id": user["id"],

            "name": user["name"],

            "email": user["email"]

        }

    }


# =========================================================
# FORGOT PASSWORD
# =========================================================

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest
):

    email = data.email.strip().lower()

    if not email:

        raise HTTPException(
            status_code=400,
            detail="Email is required."
        )

    conn = get_db()
    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                SELECT id, email
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

        else:

            cursor.execute(
                """
                SELECT id, email
                FROM users
                WHERE email = ?
                """,
                (email,)
            )

        user = cursor.fetchone()

        # Don't reveal whether email exists
        if not user:

            return {
                "success": True,
                "message": (
                    "If this email is registered, "
                    "a password reset link has been sent."
                )
            }

        # -------------------------------------------------
        # GENERATE TOKEN
        # -------------------------------------------------

        reset_token = secrets.token_urlsafe(32)

        # 15 minutes
        expiry = time.time() + (15 * 60)

        # -------------------------------------------------
        # SAVE TOKEN
        # -------------------------------------------------

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                UPDATE users
                SET reset_token = %s,
                    reset_token_expiry = %s
                WHERE id = %s
                """,
                (
                    reset_token,
                    expiry,
                    user["id"]
                )
            )

        else:

            cursor.execute(
                """
                UPDATE users
                SET reset_token = ?,
                    reset_token_expiry = ?
                WHERE id = ?
                """,
                (
                    reset_token,
                    expiry,
                    user["id"]
                )
            )

        conn.commit()

    except Exception as error:

        conn.rollback()

        print(
            "FORGOT PASSWORD DATABASE ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to process password reset."
        )

    finally:

        cursor.close()
        conn.close()

    # =====================================================
    # BREVO
    # =====================================================

    brevo_api_key = os.getenv("BREVO_API_KEY")

    sender_email = os.getenv("BREVO_SENDER_EMAIL")
    sender_name = os.getenv(
        "BREVO_SENDER_NAME",
        "SkillRoute AI"
    )

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "https://skillroute-ai.vercel.app"
    )

    reset_link = (
        f"{frontend_url}/reset-password"
        f"?token={reset_token}"
    )

    if not brevo_api_key:

        print("BREVO_API_KEY is missing.")

        raise HTTPException(
            status_code=500,
            detail="Email service is not configured."
        )

    if not sender_email:

        print("BREVO_SENDER_EMAIL is missing.")

        raise HTTPException(
            status_code=500,
            detail="Email sender is not configured."
        )

    email_data = {

        "sender": {

            "name": sender_name,

            "email": sender_email

        },

        "to": [

            {
                "email": email
            }

        ],

        "subject": "SkillRoute AI - Reset Your Password",

        "htmlContent": f"""
        <html>
        <body>

            <h2>Reset your SkillRoute AI password</h2>

            <p>
                We received a request to reset your password.
            </p>

            <p>
                Click the button below to create a new password:
            </p>

            <p>

                <a
                    href="{reset_link}"
                    style="
                        display:inline-block;
                        padding:12px 20px;
                        background:#6c63ff;
                        color:white;
                        text-decoration:none;
                        border-radius:6px;
                    "
                >
                    Reset Password
                </a>

            </p>

            <p>
                This link will expire in 15 minutes.
            </p>

            <p>
                If you did not request this password reset,
                you can safely ignore this email.
            </p>

            <p>
                Regards,<br>
                SkillRoute AI
            </p>

        </body>
        </html>
        """

    }

    try:

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",

            headers={
                "accept": "application/json",
                "api-key": brevo_api_key,
                "content-type": "application/json"
            },

            json=email_data,

            timeout=20
        )

        print(
            "BREVO STATUS:",
            response.status_code
        )

        print(
            "BREVO RESPONSE:",
            response.text
        )

        response.raise_for_status()

    except Exception as error:

        print(
            "EMAIL ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to send password reset email."
        )

    return {

        "success": True,

        "message": (
            "If this email is registered, "
            "a password reset link has been sent."
        )

    }


# =========================================================
# RESET PASSWORD
# =========================================================

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest
):

    token = data.token.strip()
    new_password = data.password

    if not token:

        raise HTTPException(
            status_code=400,
            detail="Reset token is required."
        )

    if not new_password:

        raise HTTPException(
            status_code=400,
            detail="Password is required."
        )

    if len(new_password) < 6:

        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters."
        )

    if len(new_password.encode("utf-8")) > 72:

        raise HTTPException(
            status_code=400,
            detail="Password must be 72 bytes or shorter."
        )

    conn = get_db()
    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # FIND TOKEN
        # -------------------------------------------------

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                SELECT id, reset_token_expiry
                FROM users
                WHERE reset_token = %s
                """,
                (token,)
            )

        else:

            cursor.execute(
                """
                SELECT id, reset_token_expiry
                FROM users
                WHERE reset_token = ?
                """,
                (token,)
            )

        user = cursor.fetchone()

        if not user:

            raise HTTPException(
                status_code=400,
                detail="Invalid or expired reset link."
            )

        # -------------------------------------------------
        # CHECK EXPIRY
        # -------------------------------------------------

        expiry = user["reset_token_expiry"]

        if not expiry or time.time() > float(expiry):

            raise HTTPException(
                status_code=400,
                detail="Invalid or expired reset link."
            )

        # -------------------------------------------------
        # HASH NEW PASSWORD
        # -------------------------------------------------

        hashed_password = hash_password(
            new_password
        )

        # -------------------------------------------------
        # UPDATE PASSWORD
        # -------------------------------------------------

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                UPDATE users
                SET password = %s,
                    reset_token = NULL,
                    reset_token_expiry = NULL
                WHERE id = %s
                """,
                (
                    hashed_password,
                    user["id"]
                )
            )

        else:

            cursor.execute(
                """
                UPDATE users
                SET password = ?,
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

    except HTTPException:

        conn.rollback()
        raise

    except Exception as error:

        conn.rollback()

        print(
            "RESET PASSWORD ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to reset password."
        )

    finally:

        cursor.close()
        conn.close()

    return {

        "success": True,

        "message": "Password reset successfully."

    }