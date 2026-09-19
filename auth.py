"""Authentication and role checks for the Streamlit application.

Only the feedback form is public.  Admin credentials are deliberately loaded
from deployment configuration, never from source control.
"""

import os

try:
    import streamlit as st
except ModuleNotFoundError:  # Allows the pure credential policy to be unit tested.
    st = None


ADMIN_ROLE = "admin"
HEAD_ROLE = "head"
ANONYMOUS_ROLE = "anonymous"


def _configured_admin_credentials():
    """Return configured admin credentials, or ``(None, None)`` if absent."""
    username = os.environ.get("ADMIN_USERNAME")
    password = os.environ.get("ADMIN_PASSWORD")

    if st is not None:
        try:
            username = st.secrets.get("ADMIN_USERNAME", username)
            password = st.secrets.get("ADMIN_PASSWORD", password)
        except Exception:
            # Local development can run without a secrets.toml file. Missing or
            # invalid secrets still leave the dashboard closed unless both
            # environment variables were supplied.
            pass

    return username, password


def ensure_bootstrap_head():
    """Synchronize the configured deployment owner as the initial Head account."""
    username, password = _configured_admin_credentials()
    if not all((username, password)):
        return False
    from database import bootstrap_head

    return bootstrap_head(username, password)


def logout_admin():
    """End the current admin session."""
    if st is None:
        raise RuntimeError("Streamlit is required for session management.")
    st.session_state["role"] = ANONYMOUS_ROLE
    st.session_state.pop("admin_email", None)


def require_admin():
    """Stop rendering unless the current Streamlit session has the admin role."""
    if st is None:
        raise RuntimeError("Streamlit is required for admin access control.")
    email = st.session_state.get("admin_email")
    if email:
        from database import get_admin_identity

        account = get_admin_identity(email)
    else:
        account = None
    if account and account["role"] in {ADMIN_ROLE, HEAD_ROLE}:
        st.session_state["role"] = account["role"]
        with st.sidebar:
            if st.button("Sign out", key="admin_sign_out", use_container_width=True):
                logout_admin()
                st.rerun()
        return account

    logout_admin()

    st.title("Welcome back, administrator")
    st.caption("Sign in to manage complaints assigned to you and keep students updated.")

    if not ensure_bootstrap_head():
        st.error(
            "Admin access is not configured. Set ADMIN_USERNAME and "
            "ADMIN_PASSWORD in Streamlit secrets or environment variables."
        )
        st.stop()

    info_col, login_col = st.columns([1, 1.15], gap="large")
    with info_col:
        with st.container(border=True):
            st.subheader("🛡️ Your admin workspace")
            st.write("Use your authorized account to access the complaint workflow.")
            st.markdown(
                "- **Admin** — view and resolve complaints sent to you\n"
                "- **Head** — view all complaints\n"
                "- **Students** — remain anonymous and use receipt codes to track status"
            )
            with st.expander("How complaint tracking works"):
                st.write(
                    "Students receive a private tracking code after submission. "
                    "They can check only the complaint status without accessing the dashboard."
                )

    with login_col:
        with st.container(border=True):
            st.subheader("Sign in securely")
            st.info("This dashboard is restricted to authorized administrators.")
            with st.form("admin_login"):
                username = st.text_input("Email address", autocomplete="username")
                password = st.text_input("Password", type="password", autocomplete="current-password")
                submitted = st.form_submit_button("Sign in →", use_container_width=True)

    if submitted:
        from database import authenticate_admin

        account = authenticate_admin(username, password)
        if account:
            st.session_state["role"] = account["role"]
            st.session_state["admin_email"] = account["email"]
            st.rerun()
        st.error("Invalid username or password.")

    st.divider()
    st.caption("Need access? Contact the CampusVoice super-admin to create your account.")

    # Crucially, this prevents every database read/export/update below the guard.
    st.stop()
