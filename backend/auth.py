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


# =========================================================
# EMAIL CONFIGURATION
# =========================================================

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
    new_password: str


# =========================================================
# SIGNUP
# =========================================================

@router.post("/signup")
def signup(data: SignupRequest):

    conn = get_db()
    cursor = conn.cursor()

    try:

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
                (data.email,)
            )

        else:

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = ?
                """,
                (data.email,)
            )

        existing_user = cursor.fetchone()

        if existing_user:

            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists."
            )

        # -------------------------------------------------
        # PASSWORD LENGTH
        # -------------------------------------------------

        if len(data.password.encode("utf-8")) > 72:

            raise HTTPException(
                status_code=400,
                detail="Password must be 72 bytes or shorter."
            )

        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------

        hashed_password = hash_password(
            data.password
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
                    data.name,
                    data.email,
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
                    data.name,
                    data.email,
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

        print("SIGNUP ERROR:", error)

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
            "name": data.name,
            "email": data.email
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

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                """,
                (data.email,)
            )

        else:

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = ?
                """,
                (data.email,)
            )

        user = cursor.fetchone()

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


# =========================================================
# FORGOT PASSWORD
# =========================================================

@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest
):

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
                (data.email,)
            )

        else:

            cursor.execute(
                """
                SELECT id, email
                FROM users
                WHERE email = ?
                """,
                (data.email,)
            )

        user = cursor.fetchone()

        # -------------------------------------------------
        # SECURITY
        # -------------------------------------------------

        if not user:

            return {
                "success": True,
                "message": (
                    "If this email is registered, "
                    "a recovery email has been sent."
                )
            }

        # -------------------------------------------------
        # TEMPORARY PASSWORD
        # -------------------------------------------------

        temporary_password = secrets.token_urlsafe(8)

        hashed_password = hash_password(
            temporary_password
        )

        # -------------------------------------------------
        # RESET TOKEN
        # -------------------------------------------------

        reset_token = secrets.token_urlsafe(32)

        reset_token_expiry = (
            time.time() + (15 * 60)
        )

        # -------------------------------------------------
        # SAVE PASSWORD + TOKEN
        # -------------------------------------------------

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                UPDATE users

                SET
                    password = %s,
                    reset_token = %s,
                    reset_token_expiry = %s

                WHERE id = %s
                """,
                (
                    hashed_password,
                    reset_token,
                    reset_token_expiry,
                    user["id"]
                )
            )

        else:

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

    except Exception as error:

        conn.rollback()

        print("FORGOT PASSWORD ERROR:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to process password recovery."
        )

    finally:

        cursor.close()
        conn.close()

    # =====================================================
    # RESET LINK
    # =====================================================

    # Local development
    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )

    reset_link = (
        f"{frontend_url}/reset-password/"
        f"{reset_token}"
    )

    # =====================================================
    # SEND EMAIL
    # =====================================================

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

    await fm.send_message(message)

    return {
        "success": True,
        "message": (
            "If this email is registered, "
            "a recovery email has been sent."
        )
    }


# =========================================================
# RESET PASSWORD
# =========================================================

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest
):

    conn = get_db()
    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # FIND VALID TOKEN
        # -------------------------------------------------

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                SELECT id
                FROM users

                WHERE reset_token = %s
                AND reset_token_expiry > %s
                """,
                (
                    data.token,
                    time.time()
                )
            )

        else:

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

            raise HTTPException(
                status_code=400,
                detail="Invalid or expired reset link."
            )

        # -------------------------------------------------
        # PASSWORD LENGTH
        # -------------------------------------------------

        if len(
            data.new_password.encode("utf-8")
        ) > 72:

            raise HTTPException(
                status_code=400,
                detail="Password must be 72 bytes or shorter."
            )

        # -------------------------------------------------
        # HASH NEW PASSWORD
        # -------------------------------------------------

        hashed_password = hash_password(
            data.new_password
        )

        # -------------------------------------------------
        # UPDATE PASSWORD
        # -------------------------------------------------

        if os.getenv("DATABASE_URL"):

            cursor.execute(
                """
                UPDATE users

                SET
                    password = %s,
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

    except HTTPException:
        conn.rollback()
        raise

    except Exception as error:

        conn.rollback()

        print("RESET PASSWORD ERROR:", error)

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