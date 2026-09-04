import pandas as pd

from database import get_connection


DATASET_PATH = "data/student_performance.csv"


def seed_students():

    df = pd.read_csv(DATASET_PATH)

    # First 5 records for our demo students
    student_ids = [
        "STU0001",
        "STU0002",
        "STU0003",
        "STU0004",
        "STU0005"
    ]

    conn = get_connection()
    cursor = conn.cursor()

    # Remove existing demo profiles
    for campus_id in student_ids:
        cursor.execute(
            "DELETE FROM student_profiles WHERE campus_id = ?",
            (campus_id,)
        )

    # Insert profiles
    for i, campus_id in enumerate(student_ids):

        row = df.iloc[i]

        cursor.execute(
            """
            INSERT INTO student_profiles
            (
                campus_id,
                attendance,
                internal_marks,
                assignment_score,
                previous_cgpa,
                study_hours,
                backlogs,
                practical_marks,
                quiz_score,
                previous_failures,
                participation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                campus_id,
                float(row["attendance"]),
                float(row["internal_marks"]),
                float(row["assignment_score"]),
                float(row["previous_cgpa"]),
                float(row["study_hours"]),
                int(row["backlogs"]),
                float(row["practical_marks"]),
                float(row["quiz_score"]),
                int(row["previous_failures"]),
                float(row["participation"])
            )
        )

        print(f"Profile created: {campus_id}")

    conn.commit()
    conn.close()

    print("\nStudent profiles seeded successfully!")


if __name__ == "__main__":
    seed_students()