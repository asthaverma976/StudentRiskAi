from database import initialize_database, create_user
from mentor import create_mentor


# =========================================================
# INITIALIZE DATABASE
# =========================================================

initialize_database()


# =========================================================
# MENTOR DATA
# =========================================================

mentors = [
    (
        "MENTOR001",
        "Dr. Rajesh Kumar",
        "Computer Science",
        "Mentor@123"
    ),
    (
        "MENTOR002",
        "Dr. Neha Sharma",
        "Artificial Intelligence",
        "Mentor@123"
    ),
    (
        "MENTOR003",
        "Prof. Amit Verma",
        "Information Technology",
        "Mentor@123"
    )
]


# =========================================================
# CREATE MENTORS
# =========================================================

for mentor_id, name, department, password in mentors:

    # Create mentor profile
    profile_created = create_mentor(
        mentor_id,
        name,
        department
    )

    if profile_created:
        print(
            f"Created mentor profile: {mentor_id}"
        )
    else:
        print(
            f"Mentor profile already exists: {mentor_id}"
        )

    # Create mentor login account
    user_created = create_user(
        mentor_id,
        name,
        password,
        "mentor"
    )

    if user_created:
        print(
            f"Created mentor login: {mentor_id}"
        )
    else:
        print(
            f"Mentor login already exists: {mentor_id}"
        )


print()
print("Mentor setup completed!")