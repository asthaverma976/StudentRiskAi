from datetime import datetime
import streamlit as st

from database import get_connection


# =========================================================
# CREATE INTERVENTION
# =========================================================

def create_intervention(
    campus_id,
    risk_level,
    intervention_type,
    recommendation
):

    if risk_level == "High":
        priority = "High"

    elif risk_level == "Medium":
        priority = "Medium"

    else:
        priority = "Low"

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO interventions
        (
            campus_id,
            risk_level,
            priority,
            intervention_type,
            recommendation,
            status,
            admin_note,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            campus_id,
            risk_level,
            priority,
            intervention_type,
            recommendation,
            "Pending",
            "",
            now,
            now
        )
    )

    conn.commit()
    conn.close()

    try:
        st.cache_data.clear()
    except Exception:
        pass


# =========================================================
# CHECK EXISTING INTERVENTION
# =========================================================

def intervention_exists(campus_id, risk_level, intervention_type=None):
    conn = get_connection()
    cursor = conn.cursor()

    if intervention_type is None:
        cursor.execute("""
            SELECT id
            FROM interventions
            WHERE campus_id = ?
            AND risk_level = ?
            AND status != 'Completed'
            ORDER BY id DESC
            LIMIT 1
        """, (campus_id, risk_level))

    else:
        cursor.execute("""
            SELECT id
            FROM interventions
            WHERE campus_id = ?
            AND risk_level = ?
            AND intervention_type = ?
            AND status != 'Completed'
            ORDER BY id DESC
            LIMIT 1
        """, (
            campus_id,
            risk_level,
            intervention_type
        ))

    result = cursor.fetchone()

    conn.close()

    return result is not None

# =========================================================
# GET INTERVENTIONS
# =========================================================

@st.cache_data(ttl=20, show_spinner=False)
def get_interventions():

    conn = get_connection()

    cursor = conn.cursor()

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
        ORDER BY
            CASE i.priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                ELSE 3
            END,
            i.created_at DESC
        """
    )

    rows = cursor.fetchall()

    columns = [
        "id",
        "campus_id",
        "name",
        "risk_level",
        "priority",
        "intervention_type",
        "recommendation",
        "status",
        "admin_note",
        "created_at",
        "updated_at"
    ]

    conn.close()

    import pandas as pd

    return pd.DataFrame(
        rows,
        columns=columns
    )


# =========================================================
# UPDATE INTERVENTION
# =========================================================

def update_intervention(
    intervention_id,
    status,
    admin_note
):

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

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
            admin_note,
            now,
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
# AUTOMATIC INTERVENTION PLAN
# =========================================================

def generate_intervention_plan(student):

    plans = []

    attendance = float(
        student["attendance"]
    )

    cgpa = float(
        student["previous_cgpa"]
    )

    backlogs = int(
        student["backlogs"]
    )

    internal_marks = float(
        student["internal_marks"]
    )

    study_hours = float(
        student["study_hours"]
    )

    previous_failures = int(
        student["previous_failures"]
    )

    # -----------------------------------------------------
    # ATTENDANCE
    # -----------------------------------------------------

    if attendance < 75:

        plans.append(
            (
                "Attendance Support",
                "Monitor attendance and encourage the student "
                "to maintain at least 75% attendance."
            )
        )

    # -----------------------------------------------------
    # CGPA
    # -----------------------------------------------------

    if cgpa < 6.5:

        plans.append(
            (
                "Academic Mentoring",
                "Assign a faculty mentor and create a "
                "subject-wise academic improvement plan."
            )
        )

    # -----------------------------------------------------
    # BACKLOGS
    # -----------------------------------------------------

    if backlogs > 0:

        plans.append(
            (
                "Backlog Recovery",
                "Prepare a backlog clearance schedule and "
                "prioritize pending subjects."
            )
        )

    # -----------------------------------------------------
    # INTERNAL MARKS
    # -----------------------------------------------------

    if internal_marks < 60:

        plans.append(
            (
                "Assessment Support",
                "Provide additional practice material and "
                "schedule regular internal assessment preparation."
            )
        )

    # -----------------------------------------------------
    # STUDY HOURS
    # -----------------------------------------------------

    if study_hours < 2:

        plans.append(
            (
                "Study Planning",
                "Create a daily study routine and gradually "
                "increase focused study hours."
            )
        )

    # -----------------------------------------------------
    # PREVIOUS FAILURES
    # -----------------------------------------------------

    if previous_failures > 0:

        plans.append(
            (
                "Subject Support",
                "Identify previously failed subjects and "
                "provide targeted faculty or peer support."
            )
        )

    # -----------------------------------------------------
    # DEFAULT
    # -----------------------------------------------------

    if not plans:

        plans.append(
            (
                "Regular Monitoring",
                "Continue regular academic monitoring and "
                "maintain the current performance."
            )
        )

    return plans