import sqlite3


DATABASE = "skillroute.db"


def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    cursor = conn.cursor()

    # =========================
    # USERS TABLE
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)

    # =========================
    # ADD RESET TOKEN
    # =========================

    try:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN reset_token TEXT
        """)

    except sqlite3.OperationalError:

        # Column already exists
        pass


    # =========================
    # ADD TOKEN EXPIRY
    # =========================

    try:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN reset_token_expiry REAL
        """)

    except sqlite3.OperationalError:

        # Column already exists
        pass

    # =========================
    # COURSE PROGRESS TABLE
    # =========================

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