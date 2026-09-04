import os
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
import joblib

# -----------------------------
# 1. Create folders
# -----------------------------
os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

# -----------------------------
# 2. Generate Student Dataset
# -----------------------------
np.random.seed(42)

n = 2500

attendance = np.clip(np.random.normal(75, 15, n), 35, 100)
internal_marks = np.clip(np.random.normal(65, 18, n), 20, 100)
assignment_score = np.clip(np.random.normal(70, 15, n), 20, 100)
previous_cgpa = np.clip(np.random.normal(6.8, 1.4, n), 3, 10)
study_hours = np.clip(np.random.normal(3.5, 1.8, n), 0.5, 10)
backlogs = np.clip(np.random.poisson(1.2, n), 0, 6)
practical_marks = np.clip(np.random.normal(68, 17, n), 20, 100)
quiz_score = np.clip(np.random.normal(65, 18, n), 20, 100)
previous_failures = np.clip(np.random.poisson(0.7, n), 0, 5)
participation = np.clip(np.random.normal(65, 20, n), 10, 100)

# -----------------------------
# 3. Calculate Risk Score
# -----------------------------
risk_score = (
    (100 - attendance) * 0.25
    + (100 - internal_marks) * 0.20
    + (100 - assignment_score) * 0.10
    + (10 - previous_cgpa) * 5
    + (10 - study_hours) * 2
    + backlogs * 6
    + (100 - practical_marks) * 0.08
    + (100 - quiz_score) * 0.07
    + previous_failures * 5
    + (100 - participation) * 0.05
)

# Add small noise so model has to actually learn patterns
risk_score += np.random.normal(0, 5, n)

def get_risk(score):
    if score >= 65:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"

risk = [get_risk(score) for score in risk_score]

# -----------------------------
# 4. Create Student IDs
# -----------------------------
student_ids = [
    f"STU{str(i).zfill(4)}"
    for i in range(1, n + 1)
]

df = pd.DataFrame({
    "student_id": student_ids,
    "attendance": attendance.round(2),
    "internal_marks": internal_marks.round(2),
    "assignment_score": assignment_score.round(2),
    "previous_cgpa": previous_cgpa.round(2),
    "study_hours": study_hours.round(2),
    "backlogs": backlogs,
    "practical_marks": practical_marks.round(2),
    "quiz_score": quiz_score.round(2),
    "previous_failures": previous_failures,
    "participation": participation.round(2),
    "risk_level": risk
})

# Save dataset
dataset_path = "data/student_performance.csv"
df.to_csv(dataset_path, index=False)

print(f"\nDataset created: {dataset_path}")
print(f"Total students: {len(df)}")
print("\nRisk Distribution:")
print(df["risk_level"].value_counts())

# -----------------------------
# 5. Prepare ML Data
# -----------------------------
features = [
    "attendance",
    "internal_marks",
    "assignment_score",
    "previous_cgpa",
    "study_hours",
    "backlogs",
    "practical_marks",
    "quiz_score",
    "previous_failures",
    "participation"
]

X = df[features]
y = df["risk_level"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# -----------------------------
# 6. Models
# -----------------------------
models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000))
    ]),

    "Decision Tree": DecisionTreeClassifier(
        max_depth=8,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )
}

results = {}

print("\n" + "=" * 60)
print("MODEL TRAINING")
print("=" * 60)

# -----------------------------
# 7. Train & Evaluate
# -----------------------------
for name, model in models.items():

    print(f"\nTraining: {name}")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )
    recall = recall_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )
    f1 = f1_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    results[name] = {
        "model": model,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

# -----------------------------
# 8. Select Best Model
# -----------------------------
best_name = max(
    results,
    key=lambda x: results[x]["f1"]
)

best_model = results[best_name]["model"]

print("\n" + "=" * 60)
print("BEST MODEL")
print("=" * 60)

print(f"Model: {best_name}")
print(f"Accuracy: {results[best_name]['accuracy']:.4f}")
print(f"F1 Score: {results[best_name]['f1']:.4f}")

# -----------------------------
# 9. Classification Report
# -----------------------------
best_predictions = best_model.predict(X_test)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        best_predictions,
        zero_division=0
    )
)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, best_predictions))

# -----------------------------
# 10. Save Model
# -----------------------------
model_path = "models/best_model.pkl"

joblib.dump(
    {
        "model": best_model,
        "features": features,
        "model_name": best_name
    },
    model_path
)

print("\n" + "=" * 60)
print("MODEL SAVED")
print("=" * 60)
print(model_path)
print("\nTraining completed successfully!")