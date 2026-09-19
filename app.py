"""
app.py
-------
Main entry point for the AI-Based Student Feedback & Complaint
Analysis System.

Run with:

    streamlit run app.py

Pages:
    - pages/student_feedback.py  -> feedback / complaint submission
    - pages/admin_dashboard.py   -> admin analytics + management
"""

import streamlit as st

from database import init_db
from style import inject_css, hero


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CampusVoice",
    page_icon="🎓",
    layout="wide",
)


# ============================================================
# INITIALIZE
# ============================================================

inject_css()
init_db()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("### 🎓 CampusVoice")

    st.caption(
        "AI Feedback & Complaint Analysis"
    )

    st.markdown("---")

    st.markdown("### 📌 Modules")

    st.page_link(
        "pages/student_feedback.py",
        label="📝 Student Feedback"
    )

    st.page_link(
        "pages/admin_dashboard.py",
        label="🛡️ Admin Dashboard"
    )

    st.markdown("---")

    st.caption(
        "AI-powered student feedback and "
        "complaint management system."
    )


# ============================================================
# HERO
# ============================================================

hero(
    eyebrow="AI-POWERED STUDENT FEEDBACK",

    title="CampusVoice",

    subtitle=(
        "Submit student feedback and complaints, "
        "automatically analyze them using AI, "
        "and track their resolution through a unique "
        "complaint ID."
    ),
)


# ============================================================
# MODULE CARDS
# ============================================================

col1, col2 = st.columns(2)


# ============================================================
# STUDENT FEEDBACK CARD
# ============================================================

with col1:
    with st.container(border=True):
        st.subheader("📝 Student Feedback & Complaints")
        st.write(
            "Submit a suggestion or complaint. The system automatically analyzes "
            "your feedback and provides its AI classification."
        )
        st.markdown(
            "- 💬 Sentiment Analysis\n"
            "- 🏷️ Category Detection\n"
            "- 🚨 Priority Detection\n"
            "- 🆔 Unique Complaint ID\n"
            "- 🔎 Complaint Tracking"
        )

    st.page_link(
        "pages/student_feedback.py",
        label="📝 Submit Feedback / Complaint →"
    )


# ============================================================
# ADMIN CARD
# ============================================================

with col2:
    with st.container(border=True):
        st.subheader("🛡️ Admin Dashboard")
        st.write(
            "Authorized administrators can view, manage, and monitor student "
            "complaints through the centralized dashboard."
        )
        st.markdown(
            "- 📊 Complaint Analytics\n"
            "- 📋 Complaint Management\n"
            "- 🔄 Status Updates\n"
            "- 👤 Complaint Assignment\n"
            "- 🔎 Complaint Tracking"
        )

    st.page_link(
        "pages/admin_dashboard.py",
        label="🛡️ Open Admin Dashboard →"
    )


# ============================================================
# SYSTEM FLOW
# ============================================================

st.write("")

st.markdown("---")

st.subheader("🔄 How CampusVoice Works")

flow_col1, flow_col2, flow_col3, flow_col4 = st.columns(4)

with flow_col1:

    st.markdown(
        """
        ### 1️⃣ Submit

        Student submits a feedback,
        suggestion or complaint.
        """
    )


with flow_col2:

    st.markdown(
        """
        ### 2️⃣ Analyze

        AI analyzes sentiment,
        category and priority.
        """
    )


with flow_col3:

    st.markdown(
        """
        ### 3️⃣ Track

        Student receives a unique
        complaint ID for tracking.
        """
    )


with flow_col4:

    st.markdown(
        """
        ### 4️⃣ Resolve

        Admin manages the complaint,
        updates its status and handles
        resolution.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.write("")

st.markdown("---")

st.caption(
    "Built with Python · scikit-learn · NLTK · SQLite · Streamlit — "
    "sentiment and category are model predictions, "
    "priority is rule-assisted."
)
