import base64
import hashlib
import hmac
import json
import os
import time

import streamlit as st

from database import authenticate_user, google_auth_user


SESSION_SECRET = os.environ.get(
    "STUDENT_RISK_SESSION_SECRET",
    "student-risk-ai-local-secret-change-me"
)

SESSION_TTL_SECONDS = 60 * 60 * 24 * 30


def _make_session_token(campus_id, name, role):
    payload = {
        "campus_id": str(campus_id),
        "name": str(name),
        "role": str(role),
        "expires_at": int(time.time()) + SESSION_TTL_SECONDS
    }
    encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    ).decode("ascii").rstrip("=")
    signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        encoded.encode("ascii"),
        hashlib.sha256
    ).hexdigest()
    return f"{encoded}.{signature}"


def _read_session_token(token):
    try:
        encoded, signature = token.split(".", 1)
        expected = hmac.new(
            SESSION_SECRET.encode("utf-8"),
            encoded.encode("ascii"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            return None

        padding = "=" * (-len(encoded) % 4)
        payload = json.loads(
            base64.urlsafe_b64decode(encoded + padding).decode("utf-8")
        )

        if int(payload.get("expires_at", 0)) <= int(time.time()):
            return None

        if payload.get("role") not in {"student", "admin", "mentor"}:
            return None

        return payload
    except (ValueError, TypeError, KeyError, json.JSONDecodeError,
            UnicodeDecodeError, base64.binascii.Error):
        return None


def _set_session_state(payload):
    st.session_state.logged_in = True
    st.session_state.campus_id = payload["campus_id"]
    st.session_state.name = payload["name"]
    st.session_state.role = payload["role"]


def persist_login():
    st.query_params["session"] = _make_session_token(
        st.session_state.campus_id,
        st.session_state.name,
        st.session_state.role
    )


def login_user(campus_id, password):
    user = authenticate_user(campus_id, password)

    if user:
        st.session_state.logged_in = True
        st.session_state.campus_id = user[0]
        st.session_state.name = user[1]
        st.session_state.role = user[2]
        return True

    return False


def login_google_user(email, name, role):
    user = google_auth_user(email, name, role)
    if user:
        st.session_state.logged_in = True
        st.session_state.campus_id = user[0]
        st.session_state.name = user[1]
        st.session_state.role = user[2]
        persist_login()
        return True
    return False


def restore_login():
    if st.session_state.get("logged_in", False):
        return True

    token = st.query_params.get("session")
    if token:
        payload = _read_session_token(token)
        if payload:
            _set_session_state(payload)
            return True

    return False


def logout_user():
    st.query_params.pop("session", None)

    for key in ["logged_in", "campus_id", "name", "role", "student_prediction"]:
        st.session_state.pop(key, None)

    st.rerun()


def is_logged_in():
    return st.session_state.get("logged_in", False)


def require_role(role):
    if not is_logged_in():
        st.error("Please login first.")
        st.stop()

    if st.session_state.get("role") != role:
        st.error("Access denied.")
        st.stop()
