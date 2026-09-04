from prediction import predict_risk
from database import get_connection


campus_id = "STU0001"

conn = get_connection()
cursor = conn.cursor()

cursor.execute(
    """
    SELECT
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
    FROM student_profiles
    WHERE campus_id = ?
    """,
    (campus_id,)
)

row = cursor.fetchone()
conn.close()


if row:

    student_data = {
        "attendance": row[0],
        "internal_marks": row[1],
        "assignment_score": row[2],
        "previous_cgpa": row[3],
        "study_hours": row[4],
        "backlogs": row[5],
        "practical_marks": row[6],
        "quiz_score": row[7],
        "previous_failures": row[8],
        "participation": row[9]
    }

    result = predict_risk(student_data)

    print("\n===== AI PREDICTION =====")
    print("Student:", campus_id)
    print("Risk Level:", result["risk_level"])
    print("Confidence:", round(result["confidence"] * 100, 2), "%")

    print("\nProbabilities:")

    for risk, probability in result["probabilities"].items():
        print(
            f"{risk}: {round(probability * 100, 2)}%"
        )

else:
    print("Student profile not found.")