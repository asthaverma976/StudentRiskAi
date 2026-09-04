import streamlit as st
import pandas as pd

from auth import require_role, logout_user
from ui import inject_styles, render_sidebar, render_risk_badge, render_stat_card, render_hero
from mentor import (
    get_mentor_interventions,
    update_mentor_action
)


# =========================================================
# MENTOR DASHBOARD
# =========================================================

def mentor_dashboard():
    require_role("mentor")

    # Render interactive sidebar
    active_section = render_sidebar("mentor", logout_user)

    mentor_id = st.session_state.get("campus_id")
    mentor_name = st.session_state.get("name") or "Faculty Mentor"

    # Get Assigned Interventions
    interventions = get_mentor_interventions(mentor_id)

    # Compute Stats
    if interventions:
        total = len(interventions)
        pending = sum(1 for item in interventions if item[7] == "Pending")
        in_progress = sum(1 for item in interventions if item[7] == "In Progress")
        completed = sum(1 for item in interventions if item[7] == "Completed")
    else:
        total, pending, in_progress, completed = 0, 0, 0, 0


    # =====================================================
    # 1. ASSIGNED STUDENTS
    # =====================================================
    if active_section == "🏠 Assigned Students":
        render_hero(
            "FACULTY MENTOR WORKSPACE",
            f"Welcome, Prof. {mentor_name} 👨‍🏫",
            "Support your assigned students, track meeting progress, and record personalized follow-up interventions.",
            f"Mentor ID: {mentor_id}"
        )

        # KPI Metrics
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_stat_card("Total Assigned", f"{total}", "Active student cases", "📋")
        with k2:
            render_stat_card("Pending Action", f"{pending}", "Awaiting initial contact", "⏳")
        with k3:
            render_stat_card("In Progress", f"{in_progress}", "Active mentoring sessions", "🔄")
        with k4:
            render_stat_card("Resolved", f"{completed}", "Successfully supported", "✅")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        if not interventions:
            st.info("🎉 No interventions are currently assigned to your queue. You're all caught up!")
        else:
            st.markdown("### 📋 Assigned Student Interventions")
            st.caption("Expand any card to view detailed recommendations and log follow-up notes.")

            # Filter tabs
            status_filter = st.radio(
                "Filter by Status",
                ["All", "Pending", "In Progress", "Completed"],
                horizontal=True,
                label_visibility="collapsed"
            )

            filtered_items = interventions
            if status_filter != "All":
                filtered_items = [i for i in interventions if i[7] == status_filter]

            if not filtered_items:
                st.info(f"No students found with status: '{status_filter}'")

            for item in filtered_items:
                (
                    int_id,
                    student_id,
                    student_name,
                    risk_level,
                    priority,
                    int_type,
                    recommendation,
                    status,
                    admin_note,
                    created_at,
                    updated_at
                ) = item

                with st.expander(f"👤 {student_name} ({student_id}) — {risk_level} Risk • {status}", expanded=(status == "Pending")):
                    c_info1, c_info2 = st.columns([1.2, 1])

                    with c_info1:
                        st.markdown(f"**Student:** {student_name} (`{student_id}`)")
                        st.markdown(f"**Risk Level:** {render_risk_badge(risk_level)}", unsafe_allow_html=True)
                        st.markdown(f"**Priority:** `{priority}` | **Type:** `{int_type}`")
                        st.markdown(f"**Assigned Recommendation:**")
                        st.info(f"💡 {recommendation}")

                    with c_info2:
                        st.markdown("#### ✏️ Update Mentoring Progress")
                        status_opts = ["Pending", "In Progress", "Completed", "Closed"]
                        cur_idx = status_opts.index(status) if status in status_opts else 0
                        
                        new_status = st.selectbox(
                            "Status",
                            status_opts,
                            index=cur_idx,
                            key=f"mentor_status_{int_id}"
                        )

                        mentor_note = st.text_area(
                            "Follow-up Notes / Meeting Summary",
                            value=str(admin_note or ""),
                            placeholder="Enter notes from student interaction, study goals set, or progress made...",
                            key=f"mentor_note_{int_id}"
                        )

                        if st.button("💾 Save Progress & Note", key=f"mentor_save_{int_id}", type="primary", use_container_width=True):
                            update_mentor_action(int_id, new_status, mentor_note)
                            st.success("✅ Follow-up logged successfully!")
                            st.rerun()


    # =====================================================
    # 2. FOLLOW-UP NOTES & LOGS
    # =====================================================
    elif active_section == "📝 Follow-up Notes":
        st.markdown("## 📝 Mentoring History & Interaction Log")
        st.write("Consolidated log of all notes, counseling sessions, and student status updates.")
        st.divider()

        if not interventions:
            st.info("No recorded interaction history found.")
        else:
            log_data = []
            for i in interventions:
                log_data.append({
                    "Intervention ID": f"#{i[0]}",
                    "Student Name": i[2],
                    "Campus ID": i[1],
                    "Risk Level": i[3],
                    "Status": i[7],
                    "Notes": i[8] if i[8] else "No notes logged yet",
                    "Last Updated": i[10]
                })

            df_log = pd.DataFrame(log_data)
            st.dataframe(df_log, use_container_width=True, hide_index=True)


    # =====================================================
    # 3. GUIDELINES & BEST PRACTICES
    # =====================================================
    elif active_section == "📌 Mentor Guidelines":
        st.markdown("## 📌 Academic Mentoring Guidelines & Action Playbook")
        st.write("Standard operating procedures for guiding at-risk students toward academic recovery.")
        st.divider()

        with st.container(border=True):
            st.markdown("### 🎯 4-Step Mentoring Workflow")
            
            g1, g2 = st.columns(2)
            with g1:
                st.markdown(
                    """
                    **1. Proactive Outreach (Within 48h)**
                    - Review AI indicator profile before initial meeting.
                    - Reach out privately via email or campus portal.
                    - Frame meeting around academic support, never penalization.

                    **2. Root Cause Discovery**
                    - Identify underlying bottlenecks (e.g. concept gaps, attendance hurdles, personal distress).
                    - Discuss continuous assessment performance.
                    """
                )
            with g2:
                st.markdown(
                    """
                    **3. Actionable Recovery Roadmaps**
                    - Set weekly micro-goals (e.g. 85% attendance for next 3 weeks).
                    - Direct to specialized faculty tutorial sessions.
                    - Prioritize backlog subject preparation.

                    **4. Continuous Tracking**
                    - Log all counseling notes into the system.
                    - Mark status as *Completed* only when performance stabilizes.
                    """
                )
