import sqlite3
import pandas as pd


DB_NAME = "student_risk.db"
DATA_PATH = "data/student_performance.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

print("Kaggle dataset loaded:")
print(df.shape)


# ============================================================
# CONNECT DATABASE
# ============================================================

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()


# ============================================================
# ADD NEW COLUMNS
# ============================================================

new_columns = {

    "age": "INTEGER",

    "gender": "TEXT",

    "major": "TEXT",

    "GPA": "REAL",

    "course_load": "INTEGER",

    "avg_course_grade": "REAL",

    "attendance_rate": "REAL",

    "enrollment_status": "TEXT",

    "lms_logins_past_month": "INTEGER",

    "avg_session_duration_minutes": "INTEGER",

    "assignment_submission_rate": "REAL",

    "forum_participation_count": "INTEGER",

    "video_completion_rate": "REAL",
}


cursor.execute(
    "PRAGMA table_info(student_profiles)"
)

existing_columns = {
    row[1]
    for row in cursor.fetchall()
}


for column, data_type in new_columns.items():

    if column not in existing_columns:

        cursor.execute(
            f"""
            ALTER TABLE student_profiles
            ADD COLUMN {column} {data_type}
            """
        )

        print(
            f"Added column: {column}"
        )


# ============================================================
# GET STUDENTS
# ============================================================

cursor.execute(
    """
    SELECT campus_id
    FROM student_profiles
    ORDER BY id
    """
)

students = cursor.fetchall()


# ============================================================
# UPDATE PROFILES
# ============================================================

updated = 0


for index, (campus_id,) in enumerate(students):

    if index >= len(df):
        break

    row = df.iloc[index]

    cursor.execute(
        """
        UPDATE student_profiles

        SET
            age = ?,
            gender = ?,
            major = ?,
            GPA = ?,
            course_load = ?,
            avg_course_grade = ?,
            attendance_rate = ?,
            enrollment_status = ?,
            lms_logins_past_month = ?,
            avg_session_duration_minutes = ?,
            assignment_submission_rate = ?,
            forum_participation_count = ?,
            video_completion_rate = ?

        WHERE campus_id = ?
        """,
        (
            int(row["age"]),
            str(row["gender"]),
            str(row["major"]),
            float(row["GPA"]),
            int(row["course_load"]),
            float(row["avg_course_grade"]),
            float(row["attendance_rate"]),
            str(row["enrollment_status"]),
            int(row["lms_logins_past_month"]),
            int(row["avg_session_duration_minutes"]),
            float(row["assignment_submission_rate"]),
            int(row["forum_participation_count"]),
            float(row["video_completion_rate"]),
            campus_id,
        ),
    )

    updated += 1


conn.commit()
conn.close()


print()
print("=" * 50)
print("KAGGLE DATABASE MIGRATION COMPLETE")
print("=" * 50)
print("Profiles updated:", updated)
print("=" * 50)