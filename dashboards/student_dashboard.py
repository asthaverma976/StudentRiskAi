import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from auth import require_role, logout_user
from database import get_connection
from prediction import predict_risk, save_prediction
from intervention import (
    generate_intervention_plan,
    create_intervention,
    intervention_exists,
)
from ui import inject_styles, render_sidebar, render_risk_badge, render_stat_card, render_hero, style_plotly_chart


# =========================================================
# CACHED DATABASE HELPERS
# =========================================================

@st.cache_data(ttl=20, show_spinner=False)
def get_student_profile(campus_id):
    conn = get_connection()
    query = """
        SELECT
            attendance,
            internal_marks,
            assignment_score,
            previous_cgpa,
            study_hours,
            backlogs,
            practical_marks,
            quiz_score,
            previous_failures,
            participation
        FROM student_profiles
        WHERE campus_id = ?
    """
    df = pd.read_sql_query(query, conn, params=(campus_id,))
    conn.close()

    if df.empty:
        return None
    return df.iloc[0].to_dict()


@st.cache_data(ttl=20, show_spinner=False)
def get_prediction_history(campus_id):
    conn = get_connection()
    query = """
        SELECT
            risk_level,
            probability,
            predicted_at
        FROM predictions
        WHERE campus_id = ?
        ORDER BY predicted_at DESC
        LIMIT 15
    """
    df = pd.read_sql_query(query, conn, params=(campus_id,))
    conn.close()
    return df


@st.cache_data(ttl=20, show_spinner=False)
def get_student_interventions(campus_id):
    conn = get_connection()
    query = """
        SELECT
            id,
            intervention_type,
            risk_level,
            priority,
            status,
            recommendation,
            admin_note,
            created_at,
            updated_at
        FROM interventions
        WHERE campus_id = ?
        ORDER BY created_at DESC
    """
    df = pd.read_sql_query(query, conn, params=(campus_id,))
    conn.close()
    return df


# =========================================================
# RECOMMENDATION GENERATOR
# =========================================================

def get_smart_recommendations(data, risk):
    recs = []

    att = float(data.get("attendance", 0))
    if att < 75:
        recs.append({
            "category": "Attendance",
            "icon": "📅",
            "priority": "High",
            "title": "Boost Lecture Attendance",
            "desc": f"Your current attendance is {att:.0f}%. Increasing your attendance to at least 75% will significantly improve exam eligibility and internal scoring."
        })

    cgpa = float(data.get("previous_cgpa", 0))
    if cgpa < 6.5:
        recs.append({
            "category": "Academics",
            "icon": "📚",
            "priority": "High",
            "title": "Strengthen Core Foundation",
            "desc": f"Your previous CGPA is {cgpa:.2f}. Focus on high-credit subjects and schedule regular weekly review sessions."
        })

    backlogs = int(data.get("backlogs", 0))
    if backlogs > 0:
        recs.append({
            "category": "Backlogs",
            "icon": "⚠️",
            "priority": "Critical",
            "title": f"Clear {backlogs} Active Backlog(s)",
            "desc": "Create a structured recovery schedule for pending subjects. Consult your department mentor for previous question papers and extra tutorials."
        })

    study = float(data.get("study_hours", 0))
    if study < 2.5:
        recs.append({
            "category": "Study Habits",
            "icon": "⏳",
            "priority": "Medium",
            "title": "Increase Daily Study Hours",
            "desc": f"You are currently studying {study:.1f} hrs/day. Boosting this to 2.5–3 hours daily will reduce stress during examination periods."
        })

    internal = float(data.get("internal_marks", 0))
    if internal < 60:
        recs.append({
            "category": "Assessments",
            "icon": "📝",
            "priority": "High",
            "title": "Improve Mid-Term & Internal Marks",
            "desc": f"Internal score is {internal:.0f}/100. Practice sample assessment papers and complete assignments ahead of deadlines."
        })

    if risk == "High":
        recs.append({
            "category": "Mentorship",
            "icon": "👨‍🏫",
            "priority": "Urgent",
            "title": "Schedule Faculty Mentor Meeting",
            "desc": "An AI risk assessment indicates you would benefit greatly from personalized faculty guidance. Check your active interventions for details."
        })

    if not recs:
        recs.append({
            "category": "Excellence",
            "icon": "🌟",
            "priority": "Low",
            "title": "Maintain Consistent Momentum",
            "desc": "Your academic parameters are strong across the board. Keep up the disciplined routine and help peer study groups!"
        })

    return recs


# =========================================================
# MAIN STUDENT DASHBOARD
# =========================================================

def student_dashboard():
    require_role("student")

    # Render interactive sidebar
    active_section = render_sidebar("student", logout_user)

    campus_id = st.session_state.campus_id
    name = st.session_state.name

    # Load Student Profile Data
    data = get_student_profile(campus_id)

    if data is None:
        st.error(f"❌ Academic profile data not found for Campus ID: `{campus_id}`.")
        st.info("Please contact your campus administrator to initialize your student records.")
        return

    # Compute or retrieve AI Prediction
    if "student_prediction" not in st.session_state:
        pred_result = predict_risk(data)
        st.session_state.student_prediction = pred_result
        save_prediction(campus_id, pred_result)
    else:
        pred_result = st.session_state.student_prediction

    risk = pred_result["risk_level"]
    raw_conf = pred_result["confidence"]
    confidence = float(raw_conf) * 100 if float(raw_conf) <= 1 else float(raw_conf)


    # =====================================================
    # 1. OVERVIEW SECTION
    # =====================================================
    if active_section == "🏠 Overview":
        render_hero(
            "STUDENT PORTAL",
            f"Welcome, {name} 👋",
            "Real-time AI academic monitoring, performance metrics, and personalized recommendations to support your learning journey.",
            f"Campus ID: {campus_id} • {risk.upper()} RISK ({confidence:.1f}%)"
        )

        # Top KPI Metric Cards
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            att = float(data["attendance"])
            render_stat_card("Attendance", f"{att:.0f}%", "Regular lecture attendance" if att >= 75 else "⚠️ Below 75% requirement", "📅")
        with k2:
            render_stat_card("Current CGPA", f"{float(data['previous_cgpa']):.2f}", "Academic grade standing", "🎓")
        with k3:
            b_count = int(data["backlogs"])
            render_stat_card("Active Backlogs", f"{b_count}", "Action recommended" if b_count > 0 else "All cleared! ✨", "⚠️" if b_count > 0 else "✅")
        with k4:
            render_stat_card("Study Routine", f"{float(data['study_hours']):.1f}h / day", "Dedicated study time", "⏳")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        col_chart, col_risk = st.columns([1.7, 1.1], gap="medium")

        with col_chart:
            with st.container(border=True):
                st.markdown("### 📊 Key Academic Indicators")
                st.caption("Breakdown of scores across continuous assessments and practicals (out of 100).")

                categories = ["Attendance", "Internal Marks", "Assignments", "Practicals", "Quiz Score", "Participation"]
                scores = [
                    float(data["attendance"]),
                    float(data["internal_marks"]),
                    float(data["assignment_score"]),
                    float(data["practical_marks"]),
                    float(data["quiz_score"]),
                    float(data["participation"]),
                ]

                colors = ["#3B82F6" if s >= 70 else ("#F59E0B" if s >= 50 else "#EF4444") for s in scores]

                fig = go.Figure(go.Bar(
                    x=categories,
                    y=scores,
                    text=[f"{s:.0f}" for s in scores],
                    textposition="auto",
                    marker_color=colors,
                    marker_line_width=0,
                ))
                fig.update_layout(
                    yaxis=dict(range=[0, 100], title="Score / Percentage"),
                    xaxis=dict(title=None),
                )
                style_plotly_chart(fig, height=310)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col_risk:
            with st.container(border=True):
                st.markdown("### 🎯 AI Risk Assessment")
                st.caption("Prediction generated by Machine Learning model.")
                
                st.metric("Model Confidence", f"{confidence:.1f}%")
                st.markdown(f"**Current Status:** {render_risk_badge(risk)}", unsafe_allow_html=True)
                st.write(f"Based on your continuous performance, the AI estimates a **{risk.lower()} level** of academic risk.")

                st.divider()
                st.markdown("**Quick Action:**")
                if st.button("Explore What-If Simulator 🔮", use_container_width=True):
                    st.session_state.student_pending_nav = "🔮 What-If Simulator"
                    st.rerun()


    # =====================================================
    # 2. MY PROFILE SECTION
    # =====================================================
    elif active_section == "👤 My Profile":
        st.markdown("## 👤 Academic Profile & Assessment Breakdown")
        st.write("Detailed snapshot of all academic and engagement indicators recorded in the university database.")
        st.divider()

        p1, p2, p3 = st.columns(3)
        with p1:
            with st.container(border=True):
                st.markdown("#### 📖 Coursework & Grades")
                st.write(f"**Campus ID:** `{campus_id}`")
                st.write(f"**Full Name:** {name}")
                st.write(f"**Previous CGPA:** `{float(data['previous_cgpa']):.2f} / 10.0`")
                st.write(f"**Active Backlogs:** `{int(data['backlogs'])}`")
                st.write(f"**Previous Failures:** `{int(data['previous_failures'])}`")

        with p2:
            with st.container(border=True):
                st.markdown("#### 📝 Internal Assessments")
                st.write(f"**Internal Marks:** `{float(data['internal_marks']):.1f} / 100`")
                st.write(f"**Assignment Score:** `{float(data['assignment_score']):.1f} / 100`")
                st.write(f"**Practical Marks:** `{float(data['practical_marks']):.1f} / 100`")
                st.write(f"**Quiz Marks:** `{float(data['quiz_score']):.1f} / 100`")

        with p3:
            with st.container(border=True):
                st.markdown("#### ⏳ Engagement & Study Habits")
                st.write(f"**Attendance Rate:** `{float(data['attendance']):.1f}%`")
                st.write(f"**Daily Study Hours:** `{float(data['study_hours']):.1f} hrs/day`")
                st.write(f"**Class Participation:** `{float(data['participation']):.1f} / 100`")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("#### 🕸️ Multi-Dimensional Competency Radar")
            radar_categories = ['Attendance', 'Internals', 'Assignments', 'Practicals', 'Quizzes', 'Participation']
            radar_values = [
                float(data['attendance']),
                float(data['internal_marks']),
                float(data['assignment_score']),
                float(data['practical_marks']),
                float(data['quiz_score']),
                float(data['participation'])
            ]
            radar_categories.append(radar_categories[0])
            radar_values.append(radar_values[0])

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_values,
                theta=radar_categories,
                fill='toself',
                fillcolor='rgba(37, 99, 235, 0.25)',
                line=dict(color='#2563EB', width=2),
                name='Student Competency'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="#E2E8F0"),
                    angularaxis=dict(gridcolor="#E2E8F0")
                ),
                showlegend=False
            )
            style_plotly_chart(fig_radar, height=360)
            st.plotly_chart(fig_radar, use_container_width=True)


    # =====================================================
    # 3. AI RISK ANALYSIS SECTION
    # =====================================================
    elif active_section == "🎯 AI Risk Analysis":
        st.markdown("## 🎯 AI Risk Prediction & Feature Analysis")
        st.write("Understand the driving factors and model probabilities behind your risk classification.")
        st.divider()

        rc1, rc2 = st.columns([1, 1.3], gap="medium")

        with rc1:
            with st.container(border=True):
                st.markdown("#### Current Classification")
                st.markdown(f"### {render_risk_badge(risk, confidence)}", unsafe_allow_html=True)
                st.caption(f"Model Confidence: {confidence:.2f}%")

                if "probabilities" in pred_result:
                    st.markdown("##### Class Probability Distribution")
                    prob_df = pd.DataFrame([
                        {"Risk Class": k, "Probability (%)": float(v) * 100}
                        for k, v in pred_result["probabilities"].items()
                    ])
                    st.dataframe(prob_df, hide_index=True, use_container_width=True)

        with rc2:
            with st.container(border=True):
                st.markdown("#### 🔍 Key Indicators Impacting Your Risk")
                st.caption("Factors analyzed by the AI model to determine early intervention needs.")

                factors = []
                if float(data["attendance"]) < 75:
                    factors.append(("🔴 Attendance Warning", f"Current attendance ({float(data['attendance']):.0f}%) is below the recommended 75% threshold."))
                else:
                    factors.append(("🟢 Regular Attendance", f"Healthy attendance rate of {float(data['attendance']):.0f}%."))

                if int(data["backlogs"]) > 0:
                    factors.append(("🔴 Active Backlogs", f"{int(data['backlogs'])} active backlog(s) registered in records."))
                else:
                    factors.append(("🟢 No Backlogs", "All courses cleared successfully."))

                if float(data["internal_marks"]) < 60:
                    factors.append(("🟡 Internal Assessment", f"Internal mark average ({float(data['internal_marks']):.0f}%) has room for improvement."))
                else:
                    factors.append(("🟢 Strong Internals", f"Solid internal marks average of {float(data['internal_marks']):.0f}%."))

                if float(data["study_hours"]) < 2.0:
                    factors.append(("🟡 Low Study Hours", f"Average {float(data['study_hours']):.1f} study hours per day."))
                else:
                    factors.append(("🟢 Good Study Routine", f"{float(data['study_hours']):.1f} hours daily study routine."))

                for f_title, f_desc in factors:
                    if "🔴" in f_title:
                        st.error(f"**{f_title}**: {f_desc}")
                    elif "🟡" in f_title:
                        st.warning(f"**{f_title}**: {f_desc}")
                    else:
                        st.success(f"**{f_title}**: {f_desc}")


    # =====================================================
    # 4. RECOMMENDATIONS SECTION
    # =====================================================
    elif active_section == "💡 Recommendations":
        st.markdown("## 💡 Personalized Action Recommendations")
        st.write("Targeted, actionable suggestions generated by AI to help you achieve your best academic results.")
        st.divider()

        recs = get_smart_recommendations(data, risk)

        for rec in recs:
            with st.container(border=True):
                c_r1, c_r2 = st.columns([3, 1])
                with c_r1:
                    st.markdown(f"### {rec['icon']} {rec['title']}")
                with c_r2:
                    p_badge = "🔴 Critical" if rec["priority"] in ["Critical", "Urgent"] else ("🔵 High" if rec["priority"] == "High" else "🟢 Medium")
                    st.caption(f"**Priority:** {p_badge}")

                st.write(rec['desc'])
                st.caption(f"Category: {rec['category']}")


    # =====================================================
    # 5. WHAT-IF SIMULATOR SECTION
    # =====================================================
    elif active_section == "🔮 What-If Simulator":
        st.markdown("## 🔮 Interactive What-If Risk Simulator")
        st.write("Simulate how improving your attendance, internal marks, or study habits will lower your risk level in real-time.")
        st.divider()

        with st.container(border=True):
            st.markdown("#### 🎛️ Adjust Projected Academic Inputs")
            
            w_c1, w_c2, w_c3 = st.columns(3)
            with w_c1:
                w_att = st.slider("Projected Attendance (%)", 0.0, 100.0, float(data["attendance"]), step=1.0)
                w_internal = st.slider("Projected Internal Marks", 0.0, 100.0, float(data["internal_marks"]), step=1.0)
                w_assign = st.slider("Projected Assignment Score", 0.0, 100.0, float(data["assignment_score"]), step=1.0)
            with w_c2:
                w_study = st.slider("Projected Study Hours / Day", 0.0, 12.0, float(data["study_hours"]), step=0.5)
                w_quiz = st.slider("Projected Quiz Score", 0.0, 100.0, float(data["quiz_score"]), step=1.0)
                w_part = st.slider("Projected Participation", 0.0, 100.0, float(data["participation"]), step=1.0)
            with w_c3:
                w_practical = st.slider("Projected Practical Marks", 0.0, 100.0, float(data["practical_marks"]), step=1.0)
                w_backlogs = st.number_input("Projected Active Backlogs", 0, 15, int(data["backlogs"]))
                w_failures = st.number_input("Previous Failures", 0, 15, int(data["previous_failures"]))

            sim_btn = st.button("🚀 Calculate Projected Outcome", use_container_width=True, type="primary")

        # Run Prediction for What-If
        sim_data = {
            "attendance": w_att,
            "internal_marks": w_internal,
            "assignment_score": w_assign,
            "previous_cgpa": float(data["previous_cgpa"]),
            "study_hours": w_study,
            "backlogs": w_backlogs,
            "practical_marks": w_practical,
            "quiz_score": w_quiz,
            "previous_failures": w_failures,
            "participation": w_part,
        }

        sim_res = predict_risk(sim_data)
        sim_risk = sim_res["risk_level"]
        sim_conf = float(sim_res["confidence"]) * 100 if float(sim_res["confidence"]) <= 1 else float(sim_res["confidence"])

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("### 📊 Side-by-Side Scenario Comparison")

        comp_left, comp_right = st.columns(2)
        with comp_left:
            with st.container(border=True):
                st.markdown("#### 📌 Current Reality")
                st.markdown(f"### {render_risk_badge(risk, confidence)}", unsafe_allow_html=True)
                st.caption(f"Attendance: {float(data['attendance']):.0f}% • Backlogs: {int(data['backlogs'])} • Study: {float(data['study_hours']):.1f}h")

        with comp_right:
            with st.container(border=True):
                st.markdown("#### ✨ Simulated Outcome")
                st.markdown(f"### {render_risk_badge(sim_risk, sim_conf)}", unsafe_allow_html=True)
                st.caption(f"Attendance: {w_att:.0f}% • Backlogs: {w_backlogs} • Study: {w_study:.1f}h")

        if sim_risk != risk or sim_conf != confidence:
            if sim_risk == "Low" and risk in ["High", "Medium"]:
                st.success("🎉 Outstanding! Your simulated adjustments would successfully transition you into the **Low Risk** category!")
            elif sim_risk == "Medium" and risk == "High":
                st.info("📈 Significant progress! These improvements reduce your risk from High to Medium.")
            elif sim_risk == "High" and risk in ["Low", "Medium"]:
                st.warning("⚠️ Caution: Decreasing your attendance or study hours would escalate your risk to High.")


    # =====================================================
    # 6. MY INTERVENTIONS SECTION
    # =====================================================
    elif active_section == "🛡️ My Interventions":
        st.markdown("## 🛡️ Academic Support & Interventions")
        st.write("Track faculty mentoring actions, intervention plans, and request additional academic assistance.")
        st.divider()

        interventions_df = get_student_interventions(campus_id)

        if interventions_df.empty:
            st.info("🎉 No open interventions required. You are currently on good academic standing.")
        else:
            st.markdown("#### Active Support Plans")
            for _, row in interventions_df.iterrows():
                with st.container(border=True):
                    c_h1, c_h2 = st.columns([2, 1])
                    with c_h1:
                        st.markdown(f"### 🛡️ {row['intervention_type']}")
                    with c_h2:
                        st.caption(f"**Status:** `{row['status']}`")

                    st.write(f"**Recommended Action:** {row['recommendation']}")
                    if row['admin_note']:
                        st.info(f"**Mentor / Admin Note:** {row['admin_note']}")
                    st.caption(f"Created on: {row['created_at']} | Priority: {row['priority']}")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        with st.expander("➕ Request New Academic Support Plan"):
            st.write("Generate a personalized intervention plan based on your current indicators:")
            auto_plans = generate_intervention_plan(data)
            for plan_type, plan_text in auto_plans:
                st.markdown(f"• **{plan_type}:** {plan_text}")

            if st.button("Submit Support Request", use_container_width=True, type="primary"):
                c_created = 0
                for plan_type, plan_text in auto_plans:
                    if not intervention_exists(campus_id, risk, plan_type):
                        create_intervention(campus_id, risk, plan_type, plan_text)
                        c_created += 1
                if c_created > 0:
                    st.success(f"✅ Created {c_created} academic support request(s)!")
                    st.rerun()
                else:
                    st.info("Active support plans already exist for your profile.")


    # =====================================================
    # 7. PREDICTION HISTORY SECTION
    # =====================================================
    elif active_section == "📈 Prediction History":
        st.markdown("## 📈 AI Prediction History & Trajectory")
        st.write("Historical record of AI risk assessments logged for your account over time.")
        st.divider()

        hist_df = get_prediction_history(campus_id)

        if hist_df.empty:
            st.info("No prior prediction history records found.")
        else:
            hist_df = hist_df.copy()
            hist_df["probability_pct"] = (pd.to_numeric(hist_df["probability"], errors="coerce") * 100).round(2)

            if len(hist_df) > 1:
                with st.container(border=True):
                    st.markdown("#### 📉 Risk Probability Trend")
                    fig_hist = px.line(
                        hist_df.iloc[::-1],
                        x="predicted_at",
                        y="probability_pct",
                        markers=True,
                        title="AI Confidence Score Over Time (%)",
                        labels={"predicted_at": "Assessment Date", "probability_pct": "Confidence (%)"}
                    )
                    fig_hist.update_traces(line_color="#2563EB", marker=dict(size=8, color="#1D4ED8"))
                    style_plotly_chart(fig_hist, height=280)
                    st.plotly_chart(fig_hist, use_container_width=True)

            st.markdown("#### Assessment Log Table")
            display_table = hist_df.rename(columns={
                "risk_level": "Risk Level",
                "probability_pct": "Confidence (%)",
                "predicted_at": "Assessment Date"
            })[["Assessment Date", "Risk Level", "Confidence (%)"]]
            st.dataframe(display_table, use_container_width=True, hide_index=True)
