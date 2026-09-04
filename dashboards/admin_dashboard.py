import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from auth import require_role, logout_user
from database import update_student_profile
from ui import inject_styles, render_sidebar, render_risk_badge, render_stat_card, render_hero, style_plotly_chart

from intervention import (
    create_intervention,
    get_interventions,
    update_intervention,
    generate_intervention_plan,
    intervention_exists
)

from mentor import (
    get_mentors,
    assign_mentor
)


# =========================================================
# CACHED DATABASE HELPERS
# =========================================================

DB_NAME = "student_risk.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


@st.cache_data(ttl=20, show_spinner=False)
def get_all_students():
    conn = get_connection()
    query = """
        SELECT
            u.campus_id,
            u.name,
            u.role,
            p.attendance,
            p.internal_marks,
            p.assignment_score,
            p.previous_cgpa,
            p.study_hours,
            p.backlogs,
            p.practical_marks,
            p.quiz_score,
            p.previous_failures,
            p.participation
        FROM users u
        LEFT JOIN student_profiles p
            ON u.campus_id = p.campus_id
        WHERE u.role = 'student'
        ORDER BY u.campus_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


@st.cache_data(ttl=20, show_spinner=False)
def get_latest_predictions():
    conn = get_connection()
    query = """
        SELECT
            p.campus_id,
            u.name,
            p.risk_level,
            p.probability,
            p.predicted_at
        FROM predictions p
        JOIN users u
            ON p.campus_id = u.campus_id
        WHERE p.id IN (
            SELECT MAX(id)
            FROM predictions
            GROUP BY campus_id
        )
        ORDER BY
            CASE
                WHEN p.risk_level = 'High' THEN 1
                WHEN p.risk_level = 'Medium' THEN 2
                ELSE 3
            END
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


@st.cache_data(ttl=20, show_spinner=False)
def get_student_predictions(campus_id):
    conn = get_connection()
    query = """
        SELECT
            risk_level,
            probability,
            predicted_at
        FROM predictions
        WHERE campus_id = ?
        ORDER BY predicted_at DESC
    """
    df = pd.read_sql_query(query, conn, params=(campus_id,))
    conn.close()
    return df


# =========================================================
# MAIN ADMIN DASHBOARD
# =========================================================

def admin_dashboard():
    require_role("admin")

    # Render interactive sidebar
    active_section = render_sidebar("admin", logout_user)

    admin_name = st.session_state.get("name") or "Administrator"

    # Load master data
    students_df = get_all_students()
    predictions_df = get_latest_predictions()

    # Calculate cohort statistics
    total_students = len(students_df)
    if not predictions_df.empty:
        high_risk_count = len(predictions_df[predictions_df["risk_level"] == "High"])
        med_risk_count = len(predictions_df[predictions_df["risk_level"] == "Medium"])
        low_risk_count = len(predictions_df[predictions_df["risk_level"] == "Low"])
    else:
        high_risk_count, med_risk_count, low_risk_count = 0, 0, 0


    # =====================================================
    # 1. EXECUTIVE OVERVIEW
    # =====================================================
    if active_section == "🏠 Executive Overview":
        render_hero(
            "ADMINISTRATOR CONSOLE",
            "Executive Overview & Risk Command Center",
            "Real-time institutional analytics, cohort risk distributions, and urgent student alerts."
        )

        # Top Metric Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_stat_card("Enrolled Students", f"{total_students}", "Active cohort roster", "👥")
        with c2:
            render_stat_card("High Risk Alerts", f"{high_risk_count}", "Immediate intervention needed", "🔴")
        with c3:
            render_stat_card("Medium Risk", f"{med_risk_count}", "Proactive monitoring advised", "🟡")
        with c4:
            render_stat_card("Low Risk (Safe)", f"{low_risk_count}", "Stable academic trajectory", "🟢")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        col_donut, col_alerts = st.columns([1.1, 1.4], gap="medium")

        with col_donut:
            with st.container(border=True):
                st.markdown("### 📊 Cohort Risk Breakdown")
                st.caption("Distribution of predicted risk levels across cohort.")

                if not predictions_df.empty:
                    risk_counts = predictions_df["risk_level"].value_counts().reset_index()
                    risk_counts.columns = ["Risk Level", "Count"]

                    color_map = {
                        "High": "#EF4444",
                        "Medium": "#F59E0B",
                        "Low": "#10B981"
                    }

                    fig_pie = px.pie(
                        risk_counts,
                        names="Risk Level",
                        values="Count",
                        color="Risk Level",
                        color_discrete_map=color_map,
                        hole=0.55
                    )
                    fig_pie.update_traces(
                        textposition="inside",
                        textinfo="percent+label",
                        marker=dict(line=dict(color='#FFFFFF', width=2))
                    )
                    style_plotly_chart(fig_pie, height=290)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("No prediction data available yet.")

        with col_alerts:
            with st.container(border=True):
                st.markdown("### 🚨 High Risk Action Required")
                st.caption("Students requiring immediate faculty mentoring or intervention.")

                if predictions_df.empty:
                    st.info("No prediction data available.")
                else:
                    high_risk_df = predictions_df[predictions_df["risk_level"] == "High"]
                    if high_risk_df.empty:
                        st.success("🎉 No high-risk students detected at this time.")
                    else:
                        st.warning(f"⚠️ {len(high_risk_df)} student(s) currently flagged for immediate support.")
                        
                        display_alerts = high_risk_df.copy()
                        display_alerts["probability"] = (pd.to_numeric(display_alerts["probability"], errors="coerce") * 100).round(1).astype(str) + "%"
                        display_alerts = display_alerts.rename(columns={
                            "campus_id": "Campus ID",
                            "name": "Student Name",
                            "probability": "AI Confidence",
                            "predicted_at": "Assessment Date"
                        })[["Campus ID", "Student Name", "AI Confidence", "Assessment Date"]]
                        
                        st.dataframe(display_alerts, use_container_width=True, hide_index=True)


    # =====================================================
    # 2. STUDENT MONITORING & INSPECTOR
    # =====================================================
    elif active_section == "👥 Student Monitoring":
        st.markdown("## 👥 Student Monitoring & Academic Inspector")
        st.write("Browse, search, and deeply analyze individual student academic records.")
        st.divider()

        search_query = st.text_input("🔍 Quick Search Roster", placeholder="Search by Student Name or Campus ID...")

        filtered_students = students_df.copy()
        if search_query:
            filtered_students = filtered_students[
                filtered_students["campus_id"].astype(str).str.contains(search_query, case=False, na=False) |
                filtered_students["name"].astype(str).str.contains(search_query, case=False, na=False)
            ]

        # Merge with latest risk if available
        if not predictions_df.empty:
            merged_table = filtered_students.merge(
                predictions_df[["campus_id", "risk_level", "probability"]],
                on="campus_id",
                how="left"
            )
        else:
            merged_table = filtered_students.copy()
            merged_table["risk_level"] = "N/A"
            merged_table["probability"] = 0

        st.dataframe(
            merged_table[[
                "campus_id", "name", "risk_level", "attendance", "previous_cgpa", "internal_marks", "backlogs", "study_hours"
            ]].rename(columns={
                "campus_id": "Campus ID",
                "name": "Name",
                "risk_level": "Risk Level",
                "attendance": "Attendance (%)",
                "previous_cgpa": "CGPA",
                "internal_marks": "Internals",
                "backlogs": "Backlogs",
                "study_hours": "Study Hrs"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("### 🔍 Detailed Student Profile Inspector")

        if not students_df.empty:
            student_list = {f"{row['campus_id']} — {row['name']}": row['campus_id'] for _, row in students_df.iterrows()}
            selected_student_label = st.selectbox("Select Student to Inspect", list(student_list.keys()))
            selected_id = student_list[selected_student_label]

            selected_row = students_df[students_df["campus_id"] == selected_id].iloc[0]

            with st.container(border=True):
                st.markdown(f"### 👤 {selected_row['name']} (`{selected_id}`)")

                i1, i2, i3, i4 = st.columns(4)
                with i1:
                    st.metric("Attendance", f"{selected_row['attendance']:.1f}%")
                with i2:
                    st.metric("Previous CGPA", f"{selected_row['previous_cgpa']:.2f}")
                with i3:
                    st.metric("Active Backlogs", f"{int(selected_row['backlogs'])}")
                with i4:
                    st.metric("Daily Study Hours", f"{selected_row['study_hours']:.1f}h")

                # Academic Performance Bar Chart
                perf_df = pd.DataFrame({
                    "Indicator": ["Attendance", "Internal Marks", "Assignment Score", "Practical Marks", "Quiz Score", "Participation"],
                    "Score": [
                        selected_row["attendance"],
                        selected_row["internal_marks"],
                        selected_row["assignment_score"],
                        selected_row["practical_marks"],
                        selected_row["quiz_score"],
                        selected_row["participation"],
                    ]
                })

                fig_student = px.bar(
                    perf_df,
                    x="Indicator",
                    y="Score",
                    color="Score",
                    color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
                    title=f"Academic Indicator Profile for {selected_row['name']}"
                )
                fig_student.update_layout(coloraxis_showscale=False, yaxis=dict(range=[0, 100]))
                style_plotly_chart(fig_student, height=300)
                st.plotly_chart(fig_student, use_container_width=True)

                with st.expander(f"✏️ Edit Academic Records for {selected_row['name']}"):
                    with st.form(f"admin_edit_student_{selected_id}", border=False):
                        a_c1, a_c2, a_c3 = st.columns(3)
                        with a_c1:
                            adm_att = st.number_input("Attendance (%)", min_value=0.0, max_value=100.0, value=float(selected_row["attendance"]), step=1.0)
                            adm_internal = st.number_input("Internal Marks", min_value=0.0, max_value=100.0, value=float(selected_row["internal_marks"]), step=1.0)
                            adm_assign = st.number_input("Assignment Score", min_value=0.0, max_value=100.0, value=float(selected_row["assignment_score"]), step=1.0)
                            adm_cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=float(selected_row["previous_cgpa"]), step=0.05)
                        with a_c2:
                            adm_study = st.number_input("Study Hours/Day", min_value=0.0, max_value=16.0, value=float(selected_row["study_hours"]), step=0.5)
                            adm_backlogs = st.number_input("Active Backlogs", min_value=0, max_value=20, value=int(selected_row["backlogs"]), step=1)
                            adm_failures = st.number_input("Previous Failures", min_value=0, max_value=20, value=int(selected_row["previous_failures"]), step=1)
                        with a_c3:
                            adm_practical = st.number_input("Practical Marks", min_value=0.0, max_value=100.0, value=float(selected_row["practical_marks"]), step=1.0)
                            adm_quiz = st.number_input("Quiz Score", min_value=0.0, max_value=100.0, value=float(selected_row["quiz_score"]), step=1.0)
                            adm_part = st.number_input("Participation", min_value=0.0, max_value=100.0, value=float(selected_row["participation"]), step=1.0)

                        if st.form_submit_button("💾 Save Student Record Updates", type="primary", use_container_width=True):
                            update_student_profile(selected_id, {
                                "attendance": adm_att,
                                "internal_marks": adm_internal,
                                "assignment_score": adm_assign,
                                "previous_cgpa": adm_cgpa,
                                "study_hours": adm_study,
                                "backlogs": adm_backlogs,
                                "practical_marks": adm_practical,
                                "quiz_score": adm_quiz,
                                "previous_failures": adm_failures,
                                "participation": adm_part,
                            })
                            st.toast(f"✅ Updated records for {selected_row['name']}!", icon="🎉")
                            st.success(f"Records updated for {selected_row['name']} ({selected_id})")
                            st.rerun()


    # =====================================================
    # 3. ANALYTICS & ML PERFORMANCE
    # =====================================================
    elif active_section == "📊 Analytics & Models":
        st.markdown("## 📊 Machine Learning Model Analytics & Feature Insights")
        st.write("Evaluation metrics, feature importance rankings, and AI benchmark comparison.")
        st.divider()

        tab_feat, tab_comp = st.tabs(["📌 Feature Importance", "🤖 Model Comparison & Benchmarks"])

        with tab_feat:
            feature_file = "evaluation/feature_importance.csv"
            if os.path.exists(feature_file):
                feat_df = pd.read_csv(feature_file)
                
                col_f1, col_f2 = st.columns([1.5, 1])
                with col_f1:
                    if len(feat_df.columns) >= 2:
                        y_col, x_col = feat_df.columns[0], feat_df.columns[1]
                        fig_feat = px.bar(
                            feat_df.sort_values(by=x_col, ascending=True),
                            x=x_col,
                            y=y_col,
                            orientation="h",
                            color=x_col,
                            color_continuous_scale="Blues",
                            title="Feature Weights in Risk Prediction"
                        )
                        fig_feat.update_layout(coloraxis_showscale=False)
                        style_plotly_chart(fig_feat, height=360)
                        st.plotly_chart(fig_feat, use_container_width=True)
                with col_f2:
                    st.markdown("#### Feature Weight Table")
                    st.dataframe(feat_df, use_container_width=True, hide_index=True)
            else:
                st.info("Feature importance data file not generated yet.")

        with tab_comp:
            comp_file = "evaluation/model_comparison.csv"
            if os.path.exists(comp_file):
                comp_df = pd.read_csv(comp_file)
                st.dataframe(comp_df, use_container_width=True, hide_index=True)

                acc_col = None
                for col in comp_df.columns:
                    if "accuracy" in col.lower():
                        acc_col = col
                        break

                if acc_col:
                    fig_comp = px.bar(
                        comp_df,
                        x=comp_df.columns[0],
                        y=acc_col,
                        color=acc_col,
                        color_continuous_scale="Viridis",
                        title="Model Accuracy Comparison"
                    )
                    style_plotly_chart(fig_comp, height=320)
                    st.plotly_chart(fig_comp, use_container_width=True)
            else:
                st.info("Model comparison data file not found.")


    # =====================================================
    # 4. INTERVENTION CENTER
    # =====================================================
    elif active_section == "🚨 Intervention Center":
        st.markdown("## 🚨 Early Intervention Center")
        st.write("Generate, assign, and update academic support plans for at-risk learners.")
        st.divider()

        int_tab1, int_tab2 = st.tabs(["➕ Create New Intervention", "📋 Manage Existing Interventions"])

        with int_tab1:
            with st.container(border=True):
                st.markdown("#### Generate Support Plan for Student")
                
                if students_df.empty:
                    st.info("No students found.")
                else:
                    s_options = {f"{r['campus_id']} — {r['name']}": r['campus_id'] for _, r in students_df.iterrows()}
                    chosen_label = st.selectbox("Select Target Student", list(s_options.keys()), key="admin_int_target")
                    chosen_id = s_options[chosen_label]

                    chosen_profile = students_df[students_df["campus_id"] == chosen_id].iloc[0]
                    
                    # Risk status
                    c_pred = predictions_df[predictions_df["campus_id"] == chosen_id]
                    c_risk = c_pred.iloc[0]["risk_level"] if not c_pred.empty else "Medium"
                    
                    st.markdown(f"**Current Status:** {render_risk_badge(c_risk)}", unsafe_allow_html=True)

                    plan_items = generate_intervention_plan(chosen_profile)
                    st.markdown("##### 💡 Recommended Plan Items:")
                    for p_type, p_rec in plan_items:
                        st.markdown(f"• **{p_type}:** {p_rec}")

                    if st.button("🚀 Create and Enforce Plan", type="primary", use_container_width=True):
                        created = 0
                        for p_type, p_rec in plan_items:
                            if not intervention_exists(chosen_id, c_risk, p_type):
                                create_intervention(chosen_id, c_risk, p_type, p_rec)
                                created += 1
                        if created > 0:
                            st.success(f"✅ Successfully created {created} intervention action(s)!")
                            st.rerun()
                        else:
                            st.warning("Active intervention already exists for this student.")

        with int_tab2:
            current_ints = get_interventions()
            if current_ints.empty:
                st.info("No active interventions found.")
            else:
                st.dataframe(
                    current_ints[[
                        "id", "campus_id", "name", "risk_level", "priority", "intervention_type", "status", "created_at"
                    ]].rename(columns={
                        "id": "ID",
                        "campus_id": "Campus ID",
                        "name": "Student",
                        "risk_level": "Risk",
                        "priority": "Priority",
                        "intervention_type": "Type",
                        "status": "Status",
                        "created_at": "Created Date"
                    }),
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("#### ✏️ Update Intervention Status & Notes")
                int_choices = {f"#{r['id']} — {r['name']} ({r['intervention_type']})": r['id'] for _, r in current_ints.iterrows()}
                selected_int_label = st.selectbox("Select Intervention to Modify", list(int_choices.keys()))
                selected_int_id = int_choices[selected_int_label]
                selected_int = current_ints[current_ints["id"] == selected_int_id].iloc[0]

                status_list = ["Pending", "In Progress", "Completed", "Closed"]
                cur_status = selected_int["status"] if selected_int["status"] in status_list else "Pending"

                new_stat = st.selectbox("Status", status_list, index=status_list.index(cur_status))
                new_note = st.text_area("Administrative / Mentoring Note", value=str(selected_int["admin_note"] or ""))

                if st.button("💾 Save Changes", type="primary", use_container_width=True):
                    update_intervention(selected_int_id, new_stat, new_note)
                    st.success("✅ Intervention updated successfully!")
                    st.rerun()


    # =====================================================
    # 5. MENTOR ASSIGNMENT
    # =====================================================
    elif active_section == "👨‍🏫 Mentor Assignment":
        st.markdown("## 👨‍🏫 Faculty Mentor Assignment Hub")
        st.write("Assign specialized faculty mentors to guide students through active intervention plans.")
        st.divider()

        current_ints = get_interventions()
        mentors = get_mentors()

        if current_ints.empty:
            st.info("No open interventions requiring mentor assignment.")
        elif not mentors:
            st.warning("⚠️ No faculty mentors found. Please register mentor accounts first.")
        else:
            with st.container(border=True):
                st.markdown("#### 🤝 Assign Mentor to Support Plan")

                int_options = {f"#{r['id']} — {r['name']} ({r['intervention_type']}) - Status: {r['status']}": r['id'] for _, r in current_ints.iterrows()}
                target_int_label = st.selectbox("Select Target Intervention", list(int_options.keys()))
                target_int_id = int_options[target_int_label]

                mentor_options = {f"{m[1]} ({m[2]}) — ID: {m[0]}": m[0] for m in mentors}
                chosen_mentor_label = st.selectbox("Select Faculty Mentor", list(mentor_options.keys()))
                chosen_mentor_id = mentor_options[chosen_mentor_label]

                if st.button("👨‍🏫 Finalize Assignment", type="primary", use_container_width=True):
                    assign_mentor(target_int_id, chosen_mentor_id)
                    st.success(f"✅ Assigned {chosen_mentor_label} to intervention #{target_int_id} successfully!")
                    st.rerun()


    # =====================================================
    # 6. REPORTS & EXPORT
    # =====================================================
    elif active_section == "📄 Reports & Export":
        st.markdown("## 📄 Academic Risk Cohort Reports")
        st.write("Export institutional reports and comprehensive datasets for committee reviews.")
        st.divider()

        merged_data = students_df.merge(predictions_df, on=["campus_id", "name"], how="left")

        st.markdown("#### Master Dataset Preview")
        st.dataframe(merged_data, use_container_width=True, hide_index=True)

        csv_data = merged_data.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download Full Cohort Risk Report (CSV)",
            data=csv_data,
            file_name="student_risk_cohort_report.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
