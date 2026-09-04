import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# ============================================================
# 1. FOLDERS
# ============================================================

os.makedirs("evaluation", exist_ok=True)


# ============================================================
# 2. LOAD DATASET
# ============================================================

df = pd.read_csv("data/student_performance.csv")

print("=" * 60)
print("DATASET INFORMATION")
print("=" * 60)

print(f"Total Records : {len(df)}")
print(f"Total Features: {len(df.columns) - 2}")

print("\nMissing Values:")
print(df.isnull().sum())

print("\nRisk Distribution:")
print(df["risk_level"].value_counts())


# ============================================================
# 3. FEATURES
# ============================================================

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


# ============================================================
# 4. TRAIN TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ============================================================
# 5. MODELS
# ============================================================

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


# ============================================================
# 6. TRAIN + EVALUATE
# ============================================================

results = []

trained_models = {}

print("\n")
print("=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

for name, model in models.items():

    print(f"\nTraining {name}...")

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

    results.append({
        "Model": name,
        "Accuracy": round(accuracy * 100, 2),
        "Precision": round(precision * 100, 2),
        "Recall": round(recall * 100, 2),
        "F1 Score": round(f1 * 100, 2)
    })

    trained_models[name] = model

    print(f"Accuracy : {accuracy * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall   : {recall * 100:.2f}%")
    print(f"F1 Score : {f1 * 100:.2f}%")


# ============================================================
# 7. RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(results)

print("\n")
print("=" * 60)
print("FINAL MODEL COMPARISON")
print("=" * 60)

print(results_df.to_string(index=False))

results_df.to_csv(
    "evaluation/model_comparison.csv",
    index=False
)


# ============================================================
# 8. BEST MODEL
# ============================================================

best_row = results_df.loc[
    results_df["F1 Score"].idxmax()
]

best_model_name = best_row["Model"]

best_model = trained_models[best_model_name]

print("\n")
print("=" * 60)
print("BEST MODEL")
print("=" * 60)

print(f"Model    : {best_model_name}")
print(f"Accuracy : {best_row['Accuracy']}%")
print(f"F1 Score : {best_row['F1 Score']}%")


# ============================================================
# 9. MODEL COMPARISON GRAPH
# ============================================================

plt.figure(figsize=(10, 6))

x = np.arange(len(results_df))
width = 0.2

plt.bar(
    x - width * 1.5,
    results_df["Accuracy"],
    width,
    label="Accuracy"
)

plt.bar(
    x - width / 2,
    results_df["Precision"],
    width,
    label="Precision"
)

plt.bar(
    x + width / 2,
    results_df["Recall"],
    width,
    label="Recall"
)

plt.bar(
    x + width * 1.5,
    results_df["F1 Score"],
    width,
    label="F1 Score"
)

plt.xticks(
    x,
    results_df["Model"],
    rotation=15
)

plt.ylabel("Score (%)")
plt.title("Machine Learning Model Comparison")
plt.ylim(0, 100)
plt.legend()
plt.tight_layout()

plt.savefig(
    "evaluation/model_comparison.png",
    dpi=150
)

plt.close()


# ============================================================
# 10. CONFUSION MATRIX
# ============================================================

best_predictions = best_model.predict(X_test)

cm = confusion_matrix(
    y_test,
    best_predictions,
    labels=["High", "Medium", "Low"]
)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["High", "Medium", "Low"]
)

fig, ax = plt.subplots(figsize=(7, 6))

disp.plot(
    ax=ax,
    values_format="d"
)

plt.title(
    f"Confusion Matrix - {best_model_name}"
)

plt.tight_layout()

plt.savefig(
    "evaluation/confusion_matrix.png",
    dpi=150
)

plt.close()


# ============================================================
# 11. RISK DISTRIBUTION
# ============================================================

risk_counts = df["risk_level"].value_counts()

plt.figure(figsize=(8, 6))

plt.bar(
    risk_counts.index,
    risk_counts.values
)

plt.title("Student Risk Distribution")
plt.xlabel("Risk Level")
plt.ylabel("Number of Students")

plt.tight_layout()

plt.savefig(
    "evaluation/risk_distribution.png",
    dpi=150
)

plt.close()


# ============================================================
# 12. FEATURE IMPORTANCE
# ============================================================

if best_model_name == "Random Forest":

    importance = best_model.feature_importances_

elif best_model_name == "Decision Tree":

    importance = best_model.feature_importances_

elif best_model_name == "Logistic Regression":

    importance = np.mean(
        np.abs(
            best_model.named_steps["model"].coef_
        ),
        axis=0
    )

feature_importance = pd.DataFrame({
    "Feature": features,
    "Importance": importance
})

feature_importance = feature_importance.sort_values(
    "Importance",
    ascending=False
)

print("\n")
print("=" * 60)
print("FEATURE IMPORTANCE")
print("=" * 60)

print(feature_importance.to_string(index=False))

feature_importance.to_csv(
    "evaluation/feature_importance.csv",
    index=False
)


# ============================================================
# 13. FEATURE IMPORTANCE GRAPH
# ============================================================

plt.figure(figsize=(10, 6))

plt.barh(
    feature_importance["Feature"],
    feature_importance["Importance"]
)

plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Feature Importance")

plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig(
    "evaluation/feature_importance.png",
    dpi=150
)

plt.close()


# ============================================================
# 14. SUMMARY
# ============================================================

summary = {
    "total_students": len(df),
    "best_model": best_model_name,
    "accuracy": float(best_row["Accuracy"]),
    "precision": float(best_row["Precision"]),
    "recall": float(best_row["Recall"]),
    "f1_score": float(best_row["F1 Score"])
}

pd.DataFrame([summary]).to_csv(
    "evaluation/model_summary.csv",
    index=False
)


print("\n")
print("=" * 60)
print("EVALUATION COMPLETE")
print("=" * 60)

print("\nGenerated files:")

print("evaluation/model_comparison.csv")
print("evaluation/model_comparison.png")
print("evaluation/confusion_matrix.png")
print("evaluation/risk_distribution.png")
print("evaluation/feature_importance.csv")
print("evaluation/feature_importance.png")
print("evaluation/model_summary.csv")

print("\nEverything completed successfully!")