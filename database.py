import sqlite3
import hashlib
from datetime import datetime
import streamlit as st


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DB_NAME = "student_risk.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# =========================================================
# DATABASE INITIALIZATION (RUN ONCE PER PROCESS)
# =========================================================

@st.cache_resource(show_spinner=False)
def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campus_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # STUDENT PROFILES TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campus_id TEXT UNIQUE NOT NULL,

            attendance REAL,
            internal_marks REAL,
            assignment_score REAL,
            previous_cgpa REAL,
            study_hours REAL,
            backlogs INTEGER,
            practical_marks REAL,
            quiz_score REAL,
            previous_failures INTEGER,
            participation REAL,

            FOREIGN KEY (campus_id)
            REFERENCES users(campus_id)
        )
    """)

    # PREDICTIONS TABLE
    cursor.execute("""
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

    # INTERVENTIONS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interventions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            campus_id TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            priority TEXT NOT NULL,

            intervention_type TEXT NOT NULL,
            recommendation TEXT NOT NULL,

            status TEXT DEFAULT 'Pending',
            admin_note TEXT,
            mentor_id TEXT,

            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,

            FOREIGN KEY (campus_id)
            REFERENCES users(campus_id)
        )
    """)

    # MENTORS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mentors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            mentor_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT,

            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# CREATE USER / AUTHENTICATE
# =========================================================

def create_user(campus_id, name, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users
            (campus_id, name, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            campus_id.strip(),
            name.strip(),
            hash_password(password.strip()),
            role.strip().lower(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authenticate_user(campus_id, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT campus_id, name, role
        FROM users
        WHERE LOWER(campus_id) = LOWER(?)
        AND password_hash = ?
    """, (
        campus_id.strip(),
        hash_password(password.strip())
    ))

    user = cursor.fetchone()
    conn.close()
    return user


# =========================================================
# STUDENT REGISTRATION
# =========================================================

def register_student(campus_id, name, password, profile_data=None):
    """
    Registers a new student account and creates their initial academic profile.
    """
    cid = campus_id.strip()
    cname = name.strip()

    if not create_user(cid, cname, password, "student"):
        return False

    conn = get_connection()
    cursor = conn.cursor()

    if profile_data is None:
        profile_data = {
            "attendance": 80.0,
            "internal_marks": 70.0,
            "assignment_score": 75.0,
            "previous_cgpa": 7.5,
            "study_hours": 3.0,
            "backlogs": 0,
            "practical_marks": 75.0,
            "quiz_score": 72.0,
            "previous_failures": 0,
            "participation": 80.0
        }

    cursor.execute("""
        INSERT INTO student_profiles (
            campus_id, attendance, internal_marks, assignment_score,
            previous_cgpa, study_hours, backlogs, practical_marks,
            quiz_score, previous_failures, participation
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cid,
        float(profile_data.get("attendance", 80.0)),
        float(profile_data.get("internal_marks", 70.0)),
        float(profile_data.get("assignment_score", 75.0)),
        float(profile_data.get("previous_cgpa", 7.5)),
        float(profile_data.get("study_hours", 3.0)),
        int(profile_data.get("backlogs", 0)),
        float(profile_data.get("practical_marks", 75.0)),
        float(profile_data.get("quiz_score", 72.0)),
        int(profile_data.get("previous_failures", 0)),
        float(profile_data.get("participation", 80.0))
    ))

    conn.commit()
    conn.close()
    return True


# =========================================================
# UPDATE STUDENT PROFILE
# =========================================================

def update_student_profile(campus_id, profile_data):
    """
    Updates the academic profile for a student in the student_profiles table.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE student_profiles
        SET
            attendance = ?,
            internal_marks = ?,
            assignment_score = ?,
            previous_cgpa = ?,
            study_hours = ?,
            backlogs = ?,
            practical_marks = ?,
            quiz_score = ?,
            previous_failures = ?,
            participation = ?
        WHERE campus_id = ?
    """, (
        float(profile_data.get("attendance", 0)),
        float(profile_data.get("internal_marks", 0)),
        float(profile_data.get("assignment_score", 0)),
        float(profile_data.get("previous_cgpa", 0)),
        float(profile_data.get("study_hours", 0)),
        int(profile_data.get("backlogs", 0)),
        float(profile_data.get("practical_marks", 0)),
        float(profile_data.get("quiz_score", 0)),
        int(profile_data.get("previous_failures", 0)),
        float(profile_data.get("participation", 0)),
        campus_id
    ))

    conn.commit()
    conn.close()

    try:
        st.cache_data.clear()
    except Exception:
        pass

    return True


# =========================================================
# MENTOR REGISTRATION
# =========================================================

def register_mentor(mentor_id, name, department, password):
    """
    Registers a new faculty mentor account and populates the mentors table.
    """
    mid = mentor_id.strip()
    mname = name.strip()
    mdep = department.strip() if department else "Computer Science"

    if not create_user(mid, mname, password, "mentor"):
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO mentors (mentor_id, name, department, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        mid,
        mname,
        mdep,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()
    return True


# =========================================================
# GOOGLE AUTHENTICATION / REGISTRATION
# =========================================================

def google_auth_user(email, name, role):
    """
    Authenticates or auto-provisions a user signing in with Google.
    """
    email_clean = email.strip().lower()
    name_clean = name.strip() if name else email_clean.split('@')[0].capitalize()
    role_clean = role.strip().lower()

    conn = get_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("""
        SELECT campus_id, name, role
        FROM users
        WHERE LOWER(campus_id) = LOWER(?)
    """, (email_clean,))
    existing = cursor.fetchone()
    conn.close()

    if existing:
        return existing

    # User does not exist, provision new account
    dummy_password = f"GoogleOAuth_{email_clean}_secret"
    
    if role_clean == "mentor":
        register_mentor(email_clean, name_clean, "Academic Department", dummy_password)
    else:
        register_student(email_clean, name_clean, dummy_password)

    return (email_clean, name_clean, role_clean)