"""
pages/admin_dashboard.py
--------------------------
Admin dashboard: statistics, charts, filters, complaint history and status
management, as per PRD Section 11 (Dashboard) — plus a submissions trend
chart and CSV export.
"""

import sys
import os
from html import escape
import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    SUPER_ADMIN_EMAIL,
    create_admin,
    delete_admin,
    fetch_admin_recipients,
    get_stats,
    fetch_filtered,
    init_db,
    update_status,
)
from auth import HEAD_ROLE, require_admin
from style import inject_css, hero, badge

st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")
init_db()
inject_css()
current_admin = require_admin()

# Consistent palette across all charts
COLOR_MAP_SENTIMENT = {"Positive": "#3A7D57", "Neutral": "#8A6E2F", "Negative": "#B0413E"}
COLOR_MAP_PRIORITY = {"Low": "#3A7D57", "Medium": "#C08A2E", "High": "#B0413E"}
CATEGORY_PALETTE = ["#1F2D50", "#B98B27", "#3A7D57", "#33538A", "#8A6E2F", "#6B7280"]

with st.sidebar:
    st.markdown("### 🎓 CampusVoice")
    st.caption("AI Feedback & Complaint Analysis")

hero(
    eyebrow="ADMIN",
    title="Complaint dashboard",
    subtitle="Everything submitted so far, sorted by sentiment, category and urgency.",
)

if current_admin["email"] == SUPER_ADMIN_EMAIL:
    with st.expander("Manage administrator accounts"):
        with st.form("create_admin"):
            new_email = st.text_input("Admin email")
            new_password = st.text_input("Temporary password", type="password")
            new_role = st.selectbox("Role", ["admin", "head"], format_func=str.title)
            create_submitted = st.form_submit_button("Create account")
        if create_submitted:
            try:
                if create_admin(current_admin["email"], new_email, new_password, new_role):
                    st.success(f"{new_role.title()} account created for {new_email.strip().lower()}.")
                else:
                    st.error("An account with this email already exists.")
            except (PermissionError, ValueError) as error:
                st.error(str(error))

        removable_accounts = [
            account for account in fetch_admin_recipients()
            if account["email"] != SUPER_ADMIN_EMAIL
        ]
        if removable_accounts:
            account_labels = {
                f"{account['email']} ({account['role'].title()})": account["email"]
                for account in removable_accounts
            }
            with st.form("delete_admin"):
                target_label = st.selectbox("Administrator to delete", list(account_labels))
                delete_submitted = st.form_submit_button("Delete account")
            if delete_submitted:
                try:
                    if delete_admin(current_admin["email"], account_labels[target_label]):
                        st.success("Administrator account deleted. Its assigned complaints were moved to General office.")
                        st.rerun()
                    st.error("Administrator account was not found.")
                except (PermissionError, ValueError) as error:
                    st.error(str(error))

recipient_scope = None if current_admin["role"] == HEAD_ROLE else current_admin["email"]

# ---------------- Summary metrics ----------------
stats = get_stats(assigned_admin_email=recipient_scope)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total", stats["total"])
c2.metric("Pending", stats["pending"])
c3.metric("In progress", stats["in_progress"])
c4.metric("Resolved", stats["resolved"])
c5.metric("High priority", stats["high_priority"])

st.write("")

# ---------------- Filters ----------------
with st.expander("🔍 Search & filters", expanded=True):
    f1, f2, f3, f4, f5 = st.columns(5)
    category_filter = f1.selectbox(
        "Category", ["All", "Faculty", "Hostel", "Library", "Canteen", "Examination", "Infrastructure"]
    )
    sentiment_filter = f2.selectbox("Sentiment", ["All", "Positive", "Neutral", "Negative"])
    priority_filter = f3.selectbox("Priority", ["All", "Low", "Medium", "High"])
    status_filter = f4.selectbox("Status", ["All", "Pending", "In Progress", "Resolved"])
    search_text = f5.text_input("Search text", placeholder="Keyword...")

rows = fetch_filtered(
    category=category_filter,
    sentiment=sentiment_filter,
    priority=priority_filter,
    status=status_filter,
    search_text=search_text if search_text else None,
    assigned_admin_email=recipient_scope,
)
df = pd.DataFrame(rows)

st.markdown("---")

# ---------------- Charts ----------------
st.subheader("Analytics")

if df.empty:
    st.info("No complaints match the current filters yet.")
else:
    chart_col1, chart_col2, chart_col3 = st.columns(3)

    with chart_col1:
        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]
        fig = px.bar(
            cat_counts, x="category", y="count", title="By category",
            color="category", color_discrete_sequence=CATEGORY_PALETTE,
        )
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        sent_counts = df["sentiment"].value_counts().reset_index()
        sent_counts.columns = ["sentiment", "count"]
        fig2 = px.pie(
            sent_counts, names="sentiment", values="count", title="By sentiment",
            color="sentiment", color_discrete_map=COLOR_MAP_SENTIMENT, hole=0.45,
        )
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    with chart_col3:
        pri_counts = df["priority"].value_counts().reindex(["Low", "Medium", "High"]).fillna(0).reset_index()
        pri_counts.columns = ["priority", "count"]
        fig3 = px.bar(
            pri_counts, x="priority", y="count", title="By priority",
            color="priority", color_discrete_map=COLOR_MAP_PRIORITY,
            category_orders={"priority": ["Low", "Medium", "High"]},
        )
        fig3.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig3, use_container_width=True)

    # ---- Trend over time ----
    trend_df = df.copy()
    trend_df["date"] = pd.to_datetime(trend_df["created_at"]).dt.date
    trend_counts = trend_df.groupby("date").size().reset_index(name="count")
    if len(trend_counts) > 1:
        fig4 = px.line(
            trend_counts, x="date", y="count", title="Submissions over time", markers=True,
        )
        fig4.update_traces(line_color="#1F2D50")
        fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ---------------- Complaint table + status management ----------------
st.subheader("Complaint history")

if df.empty:
    st.write("No complaints to display.")
else:
    top_col1, top_col2 = st.columns([4, 1])
    with top_col2:
        st.download_button(
            "⬇ Export CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="complaints_export.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Render table with color-coded badges via HTML (richer than st.dataframe for status/priority)
    table_rows = ""
    for _, r in df.iterrows():
        table_rows += f"""
        <tr>
            <td>{escape(str(r['id']))}</td>
            <td>{escape(str(r['student_name']))}</td>
            <td>{escape(str(r.get('assigned_admin_email') or 'General office'))}</td>
            <td style="max-width:340px;">{escape(str(r['text']))}</td>
            <td>{badge(r['sentiment'])}</td>
            <td>{escape(str(r['category']))}</td>
            <td>{badge(r['priority'])}</td>
            <td>{badge(r['status'])}</td>
            <td>{escape(str(r['created_at']))}</td>
        </tr>
        """

    st.markdown(
        f"""
        <div style="overflow-x:auto; border:1px solid #E4DCC9; border-radius:4px;">
        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
            <thead style="background-color:#F0EADD;">
                <tr style="text-align:left;">
                    <th style="padding:0.6rem;">ID</th>
                    <th style="padding:0.6rem;">Student</th>
                    <th style="padding:0.6rem;">Recipient</th>
                    <th style="padding:0.6rem;">Feedback</th>
                    <th style="padding:0.6rem;">Sentiment</th>
                    <th style="padding:0.6rem;">Category</th>
                    <th style="padding:0.6rem;">Priority</th>
                    <th style="padding:0.6rem;">Status</th>
                    <th style="padding:0.6rem;">Submitted</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown("#### Update complaint status")
    sel_col1, sel_col2, sel_col3 = st.columns([2, 2, 1])
    complaint_id = sel_col1.selectbox("Complaint ID", df["id"].tolist())
    new_status = sel_col2.selectbox("New status", ["Pending", "In Progress", "Resolved"])
    if sel_col3.button("Update", use_container_width=True):
        if update_status(complaint_id, new_status, assigned_admin_email=recipient_scope):
            st.success(f"Complaint #{complaint_id} status updated to '{new_status}'.")
        else:
            st.error("You are not allowed to update this complaint.")
        st.rerun()
