from database import initialize_database, create_user

initialize_database()

# Admin account
create_user(
    campus_id="ADMIN001",
    name="System Administrator",
    password="Admin@123",
    role="admin"
)

# Student accounts
students = [
    ("STU0001", "Aarav Sharma", "Student@123"),
    ("STU0002", "Priya Singh", "Student@123"),
    ("STU0003", "Rahul Verma", "Student@123"),
    ("STU0004", "Ananya Gupta", "Student@123"),
    ("STU0005", "Karan Kumar", "Student@123"),
]

for campus_id, name, password in students:
    create_user(
        campus_id=campus_id,
        name=name,
        password=password,
        role="student"
    )

print("Users created successfully!")
print()
print("ADMIN")
print("Campus ID: ADMIN001")
print("Password : Admin@123")
print()
print("STUDENT")
print("Campus ID: STU0001")
print("Password : Student@123")