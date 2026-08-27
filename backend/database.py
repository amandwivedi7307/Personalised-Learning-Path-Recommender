import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_DATABASE = "skillroute.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    # -----------------------------------------------------
    # PRODUCTION → PostgreSQL / Neon
    # -----------------------------------------------------
    if DATABASE_URL:

        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor
        )

        return conn

    # -----------------------------------------------------
    # LOCAL DEVELOPMENT → SQLite
    # -----------------------------------------------------

    conn = sqlite3.connect(SQLITE_DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    # =====================================================
    # POSTGRESQL
    # =====================================================

    if DATABASE_URL:

        conn = get_db()
        cursor = conn.cursor()

        # -------------------------------------------------
        # USERS TABLE
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (

                id SERIAL PRIMARY KEY,

                name TEXT NOT NULL,

                email TEXT UNIQUE NOT NULL,

                password TEXT NOT NULL,

                reset_token TEXT,

                reset_token_expiry DOUBLE PRECISION

            )
        """)

        # -------------------------------------------------
        # COURSE PROGRESS TABLE
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_progress (

                id SERIAL PRIMARY KEY,

                user_id INTEGER NOT NULL,

                course_id TEXT NOT NULL,

                completed BOOLEAN DEFAULT FALSE,

                UNIQUE(user_id, course_id),

                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE

            )
        """)

        conn.commit()
        cursor.close()
        conn.close()

        return

    # =====================================================
    # SQLITE
    # =====================================================

    conn = get_db()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # USERS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)

    # -----------------------------------------------------
    # RESET TOKEN
    # -----------------------------------------------------

    try:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN reset_token TEXT
        """)

    except sqlite3.OperationalError:

        pass

    # -----------------------------------------------------
    # RESET TOKEN EXPIRY
    # -----------------------------------------------------

    try:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN reset_token_expiry REAL
        """)

    except sqlite3.OperationalError:

        pass

    # -----------------------------------------------------
    # COURSE PROGRESS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_progress (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            course_id TEXT NOT NULL,

            completed INTEGER DEFAULT 0,

            UNIQUE(user_id, course_id),

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
    """)

    conn.commit()
    conn.close()