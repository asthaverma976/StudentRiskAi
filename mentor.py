import sqlite3
from datetime import datetime
import streamlit as st

from database import get_connection


# =========================================================
# CREATE MENTOR
# =========================================================

def create_mentor(
    mentor_id,
    name,
    department
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO mentors
            (
                mentor_id,
                name,
                department,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                mentor_id,
                name,
                department,
                datetime.now().isoformat()
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


# =========================================================
# GET ALL MENTORS
# =========================================================

@st.cache_data(ttl=20, show_spinner=False)
def get_mentors():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            mentor_id,
            name,
            department
        FROM mentors
        ORDER BY name
        """
    )

    mentors = cursor.fetchall()

    conn.close()

    return mentors


# =========================================================
# ASSIGN MENTOR
# =========================================================

def assign_mentor(
    intervention_id,
    mentor_id
):

    conn = get_connection()
    cursor = conn.cursor()

    # Check whether column exists
    columns = [
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(interventions)"
        ).fetchall()
    ]

    if "mentor_id" not in columns:
        cursor.execute(
            """
            ALTER TABLE interventions
            ADD COLUMN mentor_id TEXT
            """
        )

    cursor.execute(
        """
        UPDATE interventions
        SET
            mentor_id = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            mentor_id,
            datetime.now().isoformat(),
            intervention_id
        )
    )

    conn.commit()
    conn.close()

    try:
        st.cache_data.clear()
    except Exception:
        pass


# =========================================================
# GET MENTOR INTERVENTIONS
# =========================================================

@st.cache_data(ttl=20, show_spinner=False)
def get_mentor_interventions(
    mentor_id
):

    conn = get_connection()
    cursor = conn.cursor()

    # Ensure column exists
    columns = [
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(interventions)"
        ).fetchall()
    ]

    if "mentor_id" not in columns:

        conn.close()

        return []

    cursor.execute(
        """
        SELECT
            i.id,
            i.campus_id,
            u.name,
            i.risk_level,
            i.priority,
            i.intervention_type,
            i.recommendation,
            i.status,
            i.admin_note,
            i.created_at,
            i.updated_at
        FROM interventions i
        LEFT JOIN users u
            ON i.campus_id = u.campus_id
        WHERE i.mentor_id = ?
        ORDER BY
            CASE i.priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                ELSE 3
            END,
            i.created_at DESC
        """,
        (mentor_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


# =========================================================
# UPDATE MENTOR ACTION
# =========================================================

def update_mentor_action(
    intervention_id,
    status,
    note
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE interventions
        SET
            status = ?,
            admin_note = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            status,
            note,
            datetime.now().isoformat(),
            intervention_id
        )
    )

    conn.commit()
    conn.close()

    try:
        st.cache_data.clear()
    except Exception:
        pass