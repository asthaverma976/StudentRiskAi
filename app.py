import streamlit as st

from database import initialize_database, register_student, register_mentor
from auth import login_user, persist_login, restore_login, logout_user
from ui import inject_styles, render_login_hero
from dashboards.mentor_dashboard import mentor_dashboard
from dashboards.admin_dashboard import admin_dashboard
from dashboards.student_dashboard import student_dashboard


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="StudentRiskAI — Early Academic Risk Detection & Support",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_styles()


# =========================================================
# DATABASE
# =========================================================

initialize_database()


# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "campus_id" not in st.session_state:
    st.session_state.campus_id = None

if "name" not in st.session_state:
    st.session_state.name = None

if "role" not in st.session_state:
    st.session_state.role = None


# =========================================================
# LOGIN & REGISTRATION PAGE
# =========================================================

def login_page():
    def quick_fill_demo(demo_role, demo_id, demo_pwd):
        st.session_state.login_role_choice = demo_role
        st.session_state.input_campus_id = demo_id
        st.session_state.input_password = demo_pwd

    if "login_role_choice" not in st.session_state:
        st.session_state.login_role_choice = "Student"
    if "input_campus_id" not in st.session_state:
        st.session_state.input_campus_id = ""
    if "input_password" not in st.session_state:
        st.session_state.input_password = ""

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        render_login_hero()

    with right:
        auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "✨ Create New Account"])

        # =================================================
        # TAB 1: SIGN IN
        # =================================================
        with auth_tab1:
            st.markdown("## Welcome Back 👋")
            st.caption("Sign in with your Campus ID / Email or Google.")

            with st.form("login_form", border=True):
                role = st.radio(
                    "Account Type",
                    ["Student", "Admin", "Mentor"],
                    horizontal=True,
                    key="login_role_choice"
                )

                campus_id = st.text_input(
                    "Campus ID or Email",
                    placeholder="e.g. STU0001, ADMIN001, or name@gmail.com",
                    key="input_campus_id"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="input_password"
                )

                col_rem, col_help = st.columns([1, 1])
                with col_rem:
                    st.checkbox("Remember me", value=True, key="remember_me")
                with col_help:
                    st.caption("Default passwords in demo cards")

                submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

            if submitted:
                if not campus_id.strip() or not password.strip():
                    st.warning("⚠️ Please enter both Campus ID/Email and Password.")
                else:
                    success = login_user(campus_id.strip(), password.strip())

                    if success:
                        actual_role = st.session_state.role
                        if actual_role != role.lower():
                            st.session_state.logged_in = False
                            st.session_state.campus_id = None
                            st.session_state.name = None
                            st.session_state.role = None
                            st.error(f"❌ Role mismatch: This ID belongs to '{actual_role.capitalize()}', but you selected '{role}'.")
                        else:
                            persist_login()
                            st.success(f"✅ Welcome back, {st.session_state.name}!")
                            st.rerun()
                    else:
                        st.error("❌ Invalid Campus ID or password. If you are new, click 'Create New Account' tab above.")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.markdown("### 🎯 Quick Demo Login")
            st.caption("Click any demo card to instantly prefill credentials:")

            c1, c2 = st.columns(2)
            demos = [
                ("Student", "STU0001", "Student@123", "👤"),
                ("Mentor", "MENTOR001", "Mentor@123", "👨‍🏫"),
            ]

            for col, (d_role, d_id, d_pwd, d_icon) in zip([c1, c2], demos):
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{d_icon} {d_role}**")
                        st.caption(f"ID: `{d_id}`\nPwd: `{d_pwd}`")
                        st.button(
                            f"Fill {d_role}",
                            key=f"quick_demo_{d_role.lower()}",
                            use_container_width=True,
                            on_click=quick_fill_demo,
                            args=(d_role, d_id, d_pwd)
                        )

        # =================================================
        # TAB 2: CREATE NEW ACCOUNT
        # =================================================
        with auth_tab2:
            st.markdown("## Create New Account ✨")
            st.caption("Register a new Student or Faculty Mentor account (Admin ID is single and predefined).")

            with st.form("register_form", border=True):
                reg_role = st.radio(
                    "I want to register as:",
                    ["Student", "Mentor"],
                    horizontal=True,
                    key="reg_role_choice"
                )

                reg_name = st.text_input("Full Name", placeholder="e.g. Priyanshu Rajput", key="reg_name")
                reg_id = st.text_input("Campus ID or Email", placeholder="e.g. STU1001 or priyanshu@gmail.com", key="reg_id")
                
                reg_p1, reg_p2 = st.columns(2)
                with reg_p1:
                    reg_pwd = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_pwd")
                with reg_p2:
                    reg_pwd_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_pwd_confirm")

                # Role specific fields
                if reg_role == "Mentor":
                    reg_dept = st.selectbox("Department", [
                        "Computer Science & Engineering",
                        "Information Technology",
                        "Electronics & Communication",
                        "Mechanical Engineering",
                        "Applied Mathematics"
                    ], key="reg_dept")
                else:
                    reg_dept = None
                    with st.expander("📊 Initial Academic Baseline (Optional)"):
                        st.caption("You can customize your baseline metrics or use default starter values:")
                        b_c1, b_c2 = st.columns(2)
                        with b_c1:
                            init_att = st.slider("Current Attendance (%)", 0.0, 100.0, 80.0, step=1.0, key="init_att")
                            init_cgpa = st.slider("Previous CGPA", 0.0, 10.0, 7.5, step=0.1, key="init_cgpa")
                        with b_c2:
                            init_study = st.slider("Study Hours / Day", 0.0, 12.0, 3.0, step=0.5, key="init_study")
                            init_backlogs = st.number_input("Active Backlogs", 0, 10, 0, key="init_backlogs")

                reg_submitted = st.form_submit_button("Create Account & Sign In →", use_container_width=True, type="primary")

            if reg_submitted:
                if not reg_name.strip() or not reg_id.strip() or not reg_pwd.strip():
                    st.warning("⚠️ Please fill in all required fields.")
                elif len(reg_pwd) < 4:
                    st.error("Password must be at least 4 characters long.")
                elif reg_pwd != reg_pwd_confirm:
                    st.error("❌ Passwords do not match.")
                else:
                    if reg_role == "Student":
                        profile_dict = {
                            "attendance": init_att,
                            "internal_marks": 70.0,
                            "assignment_score": 75.0,
                            "previous_cgpa": init_cgpa,
                            "study_hours": init_study,
                            "backlogs": init_backlogs,
                            "practical_marks": 75.0,
                            "quiz_score": 72.0,
                            "previous_failures": 0,
                            "participation": 80.0
                        }
                        ok = register_student(reg_id.strip(), reg_name.strip(), reg_pwd.strip(), profile_dict)
                    else:
                        ok = register_mentor(reg_id.strip(), reg_name.strip(), reg_dept, reg_pwd.strip())

                    if ok:
                        # Auto login
                        login_user(reg_id.strip(), reg_pwd.strip())
                        persist_login()
                        st.success(f"🎉 Account created successfully! Welcome, {reg_name}!")
                        st.rerun()
                    else:
                        st.error("❌ An account with this Campus ID or Email already exists. Please Sign In instead.")


# =========================================================
# RESTORE LOGIN FROM SESSION
# =========================================================

restore_login()


# =========================================================
# APPLICATION ROUTER
# =========================================================

if not st.session_state.logged_in:
    login_page()
else:
    current_role = st.session_state.role

    if current_role == "student":
        student_dashboard()
    elif current_role == "admin":
        admin_dashboard()
    elif current_role == "mentor":
        mentor_dashboard()
    else:
        st.error("Invalid account role.")
        logout_user()
