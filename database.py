"""
database.py
-----------
SQLite database module for:

1. StudentRiskAI student profiles
2. Student predictions
3. Feedback / complaints
4. Admin / Head RBAC
5. Complaint tracking and assignment
"""

import sqlite3
import os
import hashlib
import hmac
import secrets
from datetime import datetime


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "feedback.db"
)

# The sole account permitted to manage administrator accounts.
SUPER_ADMIN_EMAIL = "asthaverma976@gmail.com"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():

    conn = get_connection()
    cur = conn.cursor()

    # ========================================================
    # USERS TABLE
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            campus_id TEXT UNIQUE NOT NULL,

            name TEXT NOT NULL,

            password_hash TEXT NOT NULL,

            role TEXT NOT NULL
                CHECK(role IN ('student', 'admin', 'mentor', 'head')),

            created_at TEXT NOT NULL
        )
    """)


    # ========================================================
    # STUDENT PROFILES
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            campus_id TEXT UNIQUE NOT NULL,

            age INTEGER,

            gender TEXT,

            major TEXT,

            GPA REAL,

            course_load INTEGER,

            avg_course_grade REAL,

            attendance_rate REAL,

            enrollment_status TEXT,

            lms_logins_past_month INTEGER,

            avg_session_duration_minutes INTEGER,

            assignment_submission_rate REAL,

            forum_participation_count INTEGER,

            video_completion_rate REAL,

            FOREIGN KEY (campus_id)
                REFERENCES users(campus_id)
        )
    """)


    # ========================================================
    # PREDICTIONS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            campus_id TEXT NOT NULL,

            risk_level TEXT NOT NULL,

            probability REAL,

            predicted_at TEXT NOT NULL,

            FOREIGN KEY (campus_id)
                REFERENCES users(campus_id)
        )
    """)


    # ========================================================
    # INTERVENTIONS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS interventions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            campus_id TEXT NOT NULL,

            risk_level TEXT NOT NULL,

            priority TEXT NOT NULL,

            intervention_type TEXT NOT NULL,

            recommendation TEXT NOT NULL,

            status TEXT DEFAULT 'Pending',

            admin_note TEXT,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL,

            FOREIGN KEY (campus_id)
                REFERENCES users(campus_id)
        )
    """)


    # ========================================================
    # COMPLAINTS
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_name TEXT,

            text TEXT NOT NULL,

            sentiment TEXT,

            category TEXT,

            priority TEXT,

            confidence REAL,

            assigned_admin_email TEXT,

            tracking_code TEXT UNIQUE,

            status TEXT DEFAULT 'Pending',

            created_at TEXT NOT NULL
        )
    """)


    # ========================================================
    # ADMIN USERS / RBAC
    # ========================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

            role TEXT NOT NULL
                CHECK(role IN ('admin', 'head')),

            created_at TEXT NOT NULL
        )
    """)


    # ========================================================
    # COMPLAINT MIGRATION COLUMNS
    # ========================================================

    complaint_columns = {
        row["name"]
        for row in cur.execute(
            "PRAGMA table_info(complaints)"
        ).fetchall()
    }


    if "confidence" not in complaint_columns:

        cur.execute("""
            ALTER TABLE complaints
            ADD COLUMN confidence REAL
        """)


    if "assigned_admin_email" not in complaint_columns:

        cur.execute("""
            ALTER TABLE complaints
            ADD COLUMN assigned_admin_email TEXT
        """)


    if "tracking_code" not in complaint_columns:

        cur.execute("""
            ALTER TABLE complaints
            ADD COLUMN tracking_code TEXT
        """)


    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_complaints_tracking_code
        ON complaints(tracking_code)
    """)


    # ========================================================
    # COMMIT
    # ========================================================

    conn.commit()
    conn.close()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):

    if not isinstance(password, str):
        raise ValueError(
            "Password must be a string."
        )

    salt = secrets.token_hex(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        310_000
    )

    return (
        f"pbkdf2_sha256$310000$"
        f"{salt}${digest.hex()}"
    )


def _hash_password(password, salt=None):

    salt = salt or secrets.token_hex(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        310_000
    )

    return (
        f"pbkdf2_sha256$310000$"
        f"{salt}${digest.hex()}"
    )


def _verify_password(
    password,
    stored_hash
):

    try:

        algorithm, iterations, salt, expected = (
            stored_hash.split("$", 3)
        )

        if algorithm != "pbkdf2_sha256":
            return False

        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations)
        ).hex()

        return hmac.compare_digest(
            candidate,
            expected
        )

    except (
        AttributeError,
        ValueError
    ):

        return False


# ============================================================
# EMAIL NORMALIZATION
# ============================================================

def _normalize_email(email):

    if isinstance(email, str):
        return email.strip().lower()

    return ""


# ============================================================
# USER MANAGEMENT
# ============================================================

def create_user(
    campus_id,
    name,
    password,
    role
):

    campus_id = (
        campus_id.strip()
        if isinstance(campus_id, str)
        else ""
    )

    name = (
        name.strip()
        if isinstance(name, str)
        else ""
    )

    if not campus_id:
        raise ValueError(
            "Campus ID is required."
        )

    if not name:
        raise ValueError(
            "Name is required."
        )

    if not isinstance(password, str) or len(password) < 6:

        raise ValueError(
            "Password must contain at least 6 characters."
        )

    role = role.lower().strip()

    allowed_roles = {
        "student",
        "mentor",
    }

    if role not in allowed_roles:

        raise ValueError(
            "Invalid user role."
        )

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO users
            (
                campus_id,
                name,
                password_hash,
                role,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                campus_id,
                name,
                hash_password(password),
                role,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


# ============================================================
# USER AUTHENTICATION
# ============================================================

def authenticate_user(
    campus_id,
    password
):

    campus_id = (
        campus_id.strip()
        if isinstance(campus_id, str)
        else ""
    )

    if not campus_id or not isinstance(password, str):
        return None

    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            campus_id,
            name,
            role,
            password_hash
        FROM users
        WHERE campus_id = ?
        """,
        (campus_id,)
    ).fetchone()

    conn.close()

    if not row:
        return None

    if not _verify_password(
        password,
        row["password_hash"]
    ):

        return None

    return (
        row["campus_id"],
        row["name"],
        row["role"]
    )


# ============================================================
# ADMIN / HEAD
# ============================================================

def bootstrap_head(
    email,
    password
):

    email = _normalize_email(email)

    if (
        email != SUPER_ADMIN_EMAIL
        or not isinstance(password, str)
        or len(password) < 8
    ):

        return False

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO admin_users
            (
                email,
                password_hash,
                role,
                created_at
            )
            VALUES (?, ?, 'head', ?)

            ON CONFLICT(email)
            DO UPDATE SET
                password_hash = excluded.password_hash,
                role = 'head'
            """,
            (
                email,
                _hash_password(password),
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )

        conn.commit()

        return True

    finally:

        conn.close()


def create_admin(
    actor_email,
    email,
    password,
    role="admin"
):

    if _normalize_email(actor_email) != SUPER_ADMIN_EMAIL:
        raise PermissionError("Only the super-admin can create administrator accounts.")

    email = _normalize_email(email)

    role = role.lower().strip()

    if (
        "@" not in email
        or not isinstance(password, str)
        or len(password) < 8
        or role not in {"admin", "head"}
    ):

        raise ValueError("Provide a valid email, role, and password of at least 8 characters.")

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO admin_users
            (
                email,
                password_hash,
                role,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                email,
                _hash_password(password),
                role,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def delete_admin(actor_email, email):
    """Delete an administrator only when requested by the sole super-admin."""
    if _normalize_email(actor_email) != SUPER_ADMIN_EMAIL:
        raise PermissionError("Only the super-admin can delete administrator accounts.")

    email = _normalize_email(email)
    if not email or email == SUPER_ADMIN_EMAIL:
        raise ValueError("The super-admin account cannot be deleted.")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE complaints SET assigned_admin_email = NULL WHERE assigned_admin_email = ?",
            (email,),
        )
        cur.execute("DELETE FROM admin_users WHERE email = ?", (email,))
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


def authenticate_admin(
    email,
    password
):

    email = _normalize_email(email)

    if not email or not isinstance(password, str):
        return None

    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            email,
            password_hash,
            role
        FROM admin_users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    conn.close()

    if row and _verify_password(
        password,
        row["password_hash"]
    ):

        return {
            "email": row["email"],
            "role": row["role"]
        }

    return None


def get_admin_identity(email):

    email = _normalize_email(email)

    if not email:
        return None

    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            email,
            role
        FROM admin_users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    conn.close()

    return dict(row) if row else None


def fetch_admin_recipients():

    conn = get_connection()

    rows = [
        dict(row)
        for row in conn.execute(
            """
            SELECT
                email,
                role
            FROM admin_users
            ORDER BY
                role DESC,
                email
            """
        )
    ]

    conn.close()

    return rows


# ============================================================
# STUDENT PROFILE
# ============================================================

def save_student_profile(
    campus_id,
    student_data
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO student_profiles
        (
            campus_id,
            age,
            gender,
            major,
            GPA,
            course_load,
            avg_course_grade,
            attendance_rate,
            enrollment_status,
            lms_logins_past_month,
            avg_session_duration_minutes,
            assignment_submission_rate,
            forum_participation_count,
            video_completion_rate
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(campus_id)
        DO UPDATE SET

            age = excluded.age,
            gender = excluded.gender,
            major = excluded.major,
            GPA = excluded.GPA,
            course_load = excluded.course_load,
            avg_course_grade = excluded.avg_course_grade,
            attendance_rate = excluded.attendance_rate,
            enrollment_status = excluded.enrollment_status,
            lms_logins_past_month = excluded.lms_logins_past_month,
            avg_session_duration_minutes =
                excluded.avg_session_duration_minutes,
            assignment_submission_rate =
                excluded.assignment_submission_rate,
            forum_participation_count =
                excluded.forum_participation_count,
            video_completion_rate =
                excluded.video_completion_rate
        """,
        (
            campus_id,
            student_data.get("age"),
            student_data.get("gender"),
            student_data.get("major"),
            student_data.get("GPA"),
            student_data.get("course_load"),
            student_data.get("avg_course_grade"),
            student_data.get("attendance_rate"),
            student_data.get("enrollment_status"),
            student_data.get("lms_logins_past_month"),
            student_data.get(
                "avg_session_duration_minutes"
            ),
            student_data.get(
                "assignment_submission_rate"
            ),
            student_data.get(
                "forum_participation_count"
            ),
            student_data.get(
                "video_completion_rate"
            ),
        )
    )

    conn.commit()
    conn.close()


def get_student_profile(
    campus_id
):

    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            campus_id,
            age,
            gender,
            major,
            GPA,
            course_load,
            avg_course_grade,
            attendance_rate,
            enrollment_status,
            lms_logins_past_month,
            avg_session_duration_minutes,
            assignment_submission_rate,
            forum_participation_count,
            video_completion_rate
        FROM student_profiles
        WHERE campus_id = ?
        """,
        (campus_id,)
    ).fetchone()

    conn.close()

    if row is None:
        return None

    return dict(row)


# ============================================================
# PREDICTIONS
# ============================================================

def save_prediction(
    campus_id,
    risk_level,
    probability
):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO predictions
        (
            campus_id,
            risk_level,
            probability,
            predicted_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            campus_id,
            risk_level,
            probability,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )

    conn.commit()
    conn.close()


def get_prediction_history(
    campus_id
):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            id,
            campus_id,
            risk_level,
            probability,
            predicted_at
        FROM predictions
        WHERE campus_id = ?
        ORDER BY id DESC
        """,
        (campus_id,)
    ).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# COMPLAINT INSERT
# ============================================================

def insert_complaint(
    student_name,
    text,
    sentiment,
    category,
    priority,
    confidence=None,
    assigned_admin_email=None,
    return_tracking=False
):

    assigned_admin_email = (
        _normalize_email(
            assigned_admin_email
        )
        or None
    )

    conn = get_connection()
    cur = conn.cursor()

    if assigned_admin_email:

        recipient = cur.execute(
            """
            SELECT 1
            FROM admin_users
            WHERE email = ?
            """,
            (assigned_admin_email,)
        ).fetchone()

        if recipient is None:

            conn.close()

            raise ValueError(
                "Selected recipient is not available."
            )


    for _ in range(3):

        tracking_code = (
            f"CMP-{secrets.token_hex(8).upper()}"
        )

        try:

            cur.execute(
                """
                INSERT INTO complaints
                (
                    student_name,
                    text,
                    sentiment,
                    category,
                    priority,
                    confidence,
                    assigned_admin_email,
                    tracking_code,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
                """,
                (
                    student_name or "Anonymous",
                    text,
                    sentiment,
                    category,
                    priority,
                    confidence,
                    assigned_admin_email,
                    tracking_code,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                )
            )

            break

        except sqlite3.IntegrityError:

            continue

    else:

        conn.close()

        raise RuntimeError(
            "Could not generate a unique tracking code."
        )

    conn.commit()

    new_id = cur.lastrowid

    conn.close()

    if return_tracking:

        return (
            new_id,
            tracking_code
        )

    return new_id


# ============================================================
# TRACK COMPLAINT
# ============================================================

def track_complaint(
    tracking_code
):

    code = (
        tracking_code.strip().upper()
        if isinstance(
            tracking_code,
            str
        )
        else ""
    )

    if not code:
        return None

    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            tracking_code,
            category,
            priority,
            status,
            created_at
        FROM complaints
        WHERE tracking_code = ?
        """,
        (code,)
    ).fetchone()

    conn.close()

    return dict(row) if row else None


# ============================================================
# FETCH ALL COMPLAINTS
# ============================================================

def fetch_all_complaints():

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM complaints
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# FILTER COMPLAINTS
# ============================================================

def fetch_filtered(
    category=None,
    sentiment=None,
    priority=None,
    status=None,
    search_text=None,
    assigned_admin_email=None
):

    query = """
        SELECT *
        FROM complaints
        WHERE 1=1
    """

    params = []


    if category and category != "All":

        query += """
            AND category = ?
        """

        params.append(category)


    if sentiment and sentiment != "All":

        query += """
            AND sentiment = ?
        """

        params.append(sentiment)


    if priority and priority != "All":

        query += """
            AND priority = ?
        """

        params.append(priority)


    if status and status != "All":

        query += """
            AND status = ?
        """

        params.append(status)


    if search_text:

        query += """
            AND text LIKE ?
        """

        params.append(
            f"%{search_text}%"
        )


    if assigned_admin_email:

        query += """
            AND assigned_admin_email = ?
        """

        params.append(
            _normalize_email(
                assigned_admin_email
            )
        )


    query += """
        ORDER BY id DESC
    """


    conn = get_connection()

    rows = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# UPDATE COMPLAINT STATUS
# ============================================================

def update_status(
    complaint_id,
    new_status,
    assigned_admin_email=None
):

    conn = get_connection()

    query = """
        UPDATE complaints
        SET status = ?
        WHERE id = ?
    """

    params = [
        new_status,
        complaint_id
    ]


    if assigned_admin_email:

        query += """
            AND assigned_admin_email = ?
        """

        params.append(
            _normalize_email(
                assigned_admin_email
            )
        )


    cur = conn.cursor()

    cur.execute(
        query,
        params
    )

    conn.commit()

    updated = (
        cur.rowcount == 1
    )

    conn.close()

    return updated


# ============================================================
# ADMIN DASHBOARD STATS
# ============================================================

def get_stats(
    assigned_admin_email=None
):

    conn = get_connection()

    cur = conn.cursor()


    def count(
        query,
        params=()
    ):

        cur.execute(
            query,
            params
        )

        return cur.fetchone()[0]


    visibility_clause = ""

    visibility_params = ()


    if assigned_admin_email:

        visibility_clause = """
            WHERE assigned_admin_email = ?
        """

        visibility_params = (
            _normalize_email(
                assigned_admin_email
            ),
        )


    def with_visibility(
        condition=""
    ):

        if visibility_clause and condition:

            connector = " AND "

        elif condition:

            connector = " WHERE "

        else:

            connector = ""


        return (
            "SELECT COUNT(*) "
            "FROM complaints"
            f"{visibility_clause}"
            f"{connector}"
            f"{condition}"
        )


    stats = {

        "total": count(
            with_visibility(),
            visibility_params
        ),

        "pending": count(
            with_visibility(
                "status = 'Pending'"
            ),
            visibility_params
        ),

        "in_progress": count(
            with_visibility(
                "status = 'In Progress'"
            ),
            visibility_params
        ),

        "resolved": count(
            with_visibility(
                "status = 'Resolved'"
            ),
            visibility_params
        ),

        "high_priority": count(
            with_visibility(
                "priority = 'High'"
            ),
            visibility_params
        ),
    }


    conn.close()

    return stats


# ============================================================
# INITIALIZE DATABASE WHEN RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    init_db()

    print(
        f"Database initialized at:\n{DB_PATH}"
    )
