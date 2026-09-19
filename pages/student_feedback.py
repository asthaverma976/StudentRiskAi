"""
pages/student_feedback.py
---------------------------
Streamlit page where students submit feedback/complaints and instantly see
the AI-generated sentiment, category and priority.
"""

import sys
import os
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from predict import analyze_feedback
from auth import ensure_bootstrap_head
from database import fetch_admin_recipients, init_db, insert_complaint, track_complaint
from style import inject_css, hero, badge

st.set_page_config(page_title="Submit Feedback", page_icon="📝", layout="centered")
inject_css()
init_db()
ensure_bootstrap_head()

with st.sidebar:
    st.markdown("### 🎓 CampusVoice")
    st.caption("AI Feedback & Complaint Analysis")

hero(
    eyebrow="STUDENT SUBMISSION",
    title="Tell us what's going on",
    subtitle="Describe your feedback or complaint in your own words — the AI reads it instantly, no forms to categorize things yourself.",
)

with st.expander("Track an existing complaint"):
    with st.form("track_complaint"):
        tracking_code = st.text_input("Receipt / tracking code", placeholder="CMP-XXXXXXXXXXXXXXX")
        track_submitted = st.form_submit_button("Track complaint")
    if track_submitted:
        complaint = track_complaint(tracking_code)
        if complaint:
            st.success(f"Current status: {complaint['status']}")
            st.caption(
                f"Submitted: {complaint['created_at']} · Category: {complaint['category']} · "
                f"Priority: {complaint['priority']}"
            )
        else:
            st.error("No complaint was found for this tracking code.")

recipients = fetch_admin_recipients()
recipient_labels = {"General office (no specific recipient)": None}
for recipient in recipients:
    label = f"{recipient['email']} ({recipient['role'].title()})"
    recipient_labels[label] = recipient["email"]

with st.form("feedback_form", clear_on_submit=False):
    student_name = st.text_input("Your name (optional)", placeholder="Leave blank to submit anonymously")
    feedback_text = st.text_area(
        "Your feedback / complaint",
        placeholder="e.g. The computer lab has several non-working computers and our practical exam is next week.",
        height=150,
    )
    recipient_label = st.selectbox(
        "Send to (optional)",
        list(recipient_labels),
        help="Choose a specific Admin or Head, or leave it with the general office.",
    )
    submitted = st.form_submit_button("Analyze & submit")

if submitted:
    if not feedback_text or not feedback_text.strip():
        st.error("Please enter your feedback or complaint before submitting.")
    else:
        with st.spinner("Reading your feedback..."):
            result = analyze_feedback(feedback_text.strip())
            new_id, receipt_code = insert_complaint(
                student_name=student_name.strip() if student_name else None,
                text=result["text"],
                sentiment=result["sentiment"],
                category=result["category"],
                priority=result["priority"],
                confidence=result["confidence"],
                assigned_admin_email=recipient_labels[recipient_label],
                return_tracking=True,
            )

        st.success(f"Submitted — reference #{new_id}")
        st.markdown(f"### Your tracking code: `{receipt_code}`")
        st.warning("Save this code. You can use it above to track your complaint without logging in.")
        receipt = (
            "CampusVoice complaint receipt\n"
            f"Reference: #{new_id}\n"
            f"Tracking code: {receipt_code}\n"
            "Initial status: Pending\n"
        )
        st.download_button(
            "Download receipt",
            data=receipt,
            file_name=f"complaint-receipt-{receipt_code}.txt",
            mime="text/plain",
        )
        if recipient_labels[recipient_label]:
            st.caption(f"Sent to: {recipient_label}")

        conf_text = f"{result['confidence']:.0%} model confidence" if result["confidence"] is not None else ""

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-row">
                    <span class="result-label">Sentiment</span>
                    {badge(result['sentiment'])}
                </div>
                <div class="result-row">
                    <span class="result-label">Category</span>
                    {badge(result['category'])}
                </div>
                <div class="result-row">
                    <span class="result-label">Priority</span>
                    {badge(result['priority'])}
                </div>
                <div class="result-row">
                    <span class="result-label">Status</span>
                    {badge("Pending")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if conf_text:
            st.caption(conf_text)

        st.write("")
        if result["priority"] == "High":
            st.warning("This has been flagged as high priority and will be prioritized for review.")
        else:
            st.info("The concerned authority will review this soon.")
