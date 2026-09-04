import os
import joblib
import pandas as pd

from database import get_connection


import streamlit as st

MODEL_PATH = os.path.join(
    "models",
    "best_model.pkl"
)


# =========================================================
# CACHED TRAINED MODEL LOADER
# =========================================================

def _load_model_raw():
    model_bundle = joblib.load(MODEL_PATH)
    if isinstance(model_bundle, dict):
        if "model" in model_bundle:
            return model_bundle["model"]
        elif "best_model" in model_bundle:
            return model_bundle["best_model"]
        elif "classifier" in model_bundle:
            return model_bundle["classifier"]
        else:
            for value in model_bundle.values():
                if hasattr(value, "predict"):
                    return value
            raise ValueError("No trained ML model found inside best_model.pkl")
    return model_bundle

try:
    load_cached_model = st.cache_resource(show_spinner=False)(_load_model_raw)
except Exception:
    load_cached_model = _load_model_raw

model = load_cached_model()


# =========================================================
# FEATURES
# =========================================================

FEATURES = [
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


# =========================================================
# PREDICTION
# =========================================================

def predict_risk(student_data):

    values = [
        student_data["attendance"],
        student_data["internal_marks"],
        student_data["assignment_score"],
        student_data["previous_cgpa"],
        student_data["study_hours"],
        student_data["backlogs"],
        student_data["practical_marks"],
        student_data["quiz_score"],
        student_data["previous_failures"],
        student_data["participation"]
    ]

    # Create DataFrame with feature names
    X = pd.DataFrame(
        [values],
        columns=FEATURES
    )

    # -----------------------------------------------------
    # AI Prediction
    # -----------------------------------------------------

    prediction = model.predict(X)[0]

    # -----------------------------------------------------
    # Prediction Probability
    # -----------------------------------------------------

    if hasattr(model, "predict_proba"):

        probabilities = model.predict_proba(X)[0]

        if hasattr(model, "classes_"):
            class_names = model.classes_

        else:
            class_names = [
                "High",
                "Low",
                "Medium"
            ]

        probability_dict = {
            str(class_name): float(probability)
            for class_name, probability
            in zip(
                class_names,
                probabilities
            )
        }

        confidence = float(
            max(probabilities)
        )

    else:

        probability_dict = {
            str(prediction): 1.0
        }

        confidence = 1.0


    return {
        "risk_level": str(prediction),
        "confidence": confidence,
        "probabilities": probability_dict
    }


# =========================================================
# SAVE PREDICTION
# =========================================================

def save_prediction(
    campus_id,
    result
):

    from datetime import datetime

    conn = get_connection()
    cursor = conn.cursor()

    risk_level = result["risk_level"]

    probability = result["confidence"]

    predicted_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        """
        INSERT INTO predictions
        (
            campus_id,
            risk_level,
            probability,
            predicted_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            campus_id,
            risk_level,
            probability,
            predicted_at
        )
    )

    conn.commit()
    conn.close()


# =========================================================
# PREDICT + SAVE
# =========================================================

def predict_and_save(
    campus_id,
    student_data
):

    result = predict_risk(
        student_data
    )

    save_prediction(
        campus_id,
        result
    )

    return result