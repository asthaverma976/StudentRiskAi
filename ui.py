import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# =========================================================
# GLOBAL DESIGN SYSTEM & STYLING
# =========================================================

def inject_styles():
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">

        <style>
        :root {
            --font-main: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-heading: 'Outfit', sans-serif;
            --primary: #2563EB;
            --primary-dark: #1D4ED8;
            --navy: #0B192C;
            --bg-main: #F4F7FB;
            --bg-card: #FFFFFF;
        }

        /* Global Reset & Fonts */
        html, body, .stApp {
            font-family: var(--font-main) !important;
            background-color: var(--bg-main) !important;
            color: #0F172A;
        }

        /* Preserve Streamlit Material Icon Fonts */
        [data-testid="stIconMaterial"], 
        .material-symbols-rounded, 
        .material-icons,
        [data-testid="stSidebarCollapseButton"] *,
        [data-testid="stHeader"] button * {
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        }

        [data-testid="stHeader"] {
            background: transparent !important;
        }

        .block-container {
            max-width: 1440px !important;
            padding: 1.5rem 2rem 3rem !important;
        }

        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-heading) !important;
            color: #0B192C !important;
            letter-spacing: -0.02em !important;
            font-weight: 700 !important;
        }

        h1 { font-size: 2.1rem !important; font-weight: 800 !important; }
        h2 { font-size: 1.5rem !important; margin-top: 0.6rem !important; }
        h3 { font-size: 1.2rem !important; }

        p, label, [data-testid="stCaptionContainer"] {
            color: #475569;
            font-family: var(--font-main);
        }

        /* Sidebar Styling - Force bright text contrast */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #071324 0%, #0F233D 60%, #162E50 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #FFFFFF !important;
            font-family: var(--font-main);
        }

        [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            color: #94A3B8 !important;
            font-size: 0.72rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.05em !important;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.12) !important;
            margin: 0.7rem 0 !important;
        }

        /* Sidebar Navigation Radio Buttons */
        [data-testid="stSidebar"] .stRadio > div {
            gap: 5px !important;
        }

        [data-testid="stSidebar"] .stRadio label {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 10px !important;
            padding: 0.6rem 0.85rem !important;
            margin-bottom: 2px !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
        }

        [data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(255, 255, 255, 0.12) !important;
            border-color: rgba(96, 165, 250, 0.35) !important;
            transform: translateX(3px) !important;
        }

        [data-testid="stSidebar"] .stRadio label[data-checked="true"],
        [data-testid="stSidebar"] .stRadio label:has(input:checked) {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
            border-color: #60A5FA !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
            font-weight: 700 !important;
        }

        [data-testid="stSidebar"] .stRadio label[data-checked="true"] p,
        [data-testid="stSidebar"] .stRadio label:has(input:checked) p {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        [data-testid="stSidebar"] .stRadio input[type="radio"] {
            display: none !important;
        }

        /* Sidebar Sign Out Button */
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(239, 68, 68, 0.18) !important;
            border: 1px solid rgba(239, 68, 68, 0.45) !important;
            color: #FCA5A5 !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            min-height: 2.7rem !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: #EF4444 !important;
            color: #FFFFFF !important;
            border-color: #EF4444 !important;
            box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4) !important;
            transform: translateY(-1px) !important;
        }

        /* Modern Card Containers */
        [data-testid="stForm"], 
        [data-testid="stExpander"], 
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 18px !important;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04) !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: 0 8px 26px rgba(15, 23, 42, 0.07) !important;
        }

        /* Main Area Buttons */
        .stButton > button {
            font-family: var(--font-main) !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            padding: 0.55rem 1.25rem !important;
            min-height: 2.6rem !important;
            border: 1px solid #E2E8F0 !important;
            background: white !important;
            color: #0F172A !important;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04) !important;
            transition: all 0.2s ease !important;
        }

        .stButton > button:hover {
            border-color: var(--primary) !important;
            color: var(--primary) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08) !important;
        }

        .stButton > button[kind="primary"], 
        [data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
            color: white !important;
            border: 1px solid #3B82F6 !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
            font-weight: 700 !important;
        }

        .stButton > button[kind="primary"]:hover, 
        [data-testid="stFormSubmitButton"] button:hover {
            background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45) !important;
            color: white !important;
            transform: translateY(-2px) !important;
        }

        /* Inputs & Selectboxes */
        div[data-baseweb="input"] > div, 
        div[data-baseweb="select"] > div, 
        textarea {
            background: white !important;
            border-color: #CBD5E1 !important;
            border-radius: 10px !important;
            font-family: var(--font-main) !important;
            font-size: 0.92rem !important;
            color: #0F172A !important;
        }

        /* Streamlit Metrics */
        [data-testid="stMetric"] {
            background: white !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 14px !important;
            padding: 1.1rem !important;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03) !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06) !important;
            border-color: #BFDBFE !important;
        }

        [data-testid="stMetricLabel"] {
            color: #64748B !important;
            font-size: 0.76rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }

        [data-testid="stMetricValue"] {
            font-family: var(--font-heading) !important;
            color: #0B192C !important;
            font-size: 1.85rem !important;
            font-weight: 800 !important;
        }

        /* Custom Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, #071A3D 0%, #103778 50%, #2563EB 100%);
            border-radius: 20px;
            padding: 2rem 2.2rem;
            color: white;
            box-shadow: 0 16px 36px rgba(11, 25, 44, 0.15);
            margin-bottom: 1.5rem;
        }
        .hero-banner h1 { color: white !important; margin-bottom: 0.3rem !important; }
        .hero-banner p { color: #D6E4F8 !important; font-size: 0.95rem !important; margin: 0 !important; }

        /* Custom Stat Card */
        .stat-box {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 1.1rem;
            box-shadow: 0 2px 8px rgba(15,23,42,0.03);
            text-align: left;
        }
        .stat-box-title {
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748B !important;
        }
        .stat-box-val {
            font-family: var(--font-heading);
            font-size: 1.9rem;
            font-weight: 800;
            color: #0B192C !important;
            margin: 0.15rem 0;
            line-height: 1.1;
        }
        .stat-box-sub {
            font-size: 0.76rem;
            color: #64748B !important;
        }

        /* Login Hero Custom Container */
        .login-hero-container {
            background: linear-gradient(145deg, #071A3D 0%, #0F2E64 45%, #1D4ED8 100%);
            border-radius: 22px;
            padding: 2.6rem 2.4rem;
            color: white;
            box-shadow: 0 20px 45px rgba(7, 26, 61, 0.22);
            min-height: 580px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border: 1px solid rgba(255, 255, 255, 0.12);
        }
        .login-hero-container h1 {
            color: white !important;
            font-size: 2.4rem !important;
            font-weight: 850 !important;
            line-height: 1.15 !important;
            margin: 1rem 0 !important;
        }
        .login-hero-container p {
            color: #CBD5E1 !important;
            font-size: 0.95rem !important;
            line-height: 1.6 !important;
            margin-bottom: 1.5rem !important;
        }
        .login-badge-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.22);
            border-radius: 999px;
            padding: 0.35rem 0.85rem;
            font-size: 0.78rem;
            font-weight: 700;
            color: #93C5FD !important;
        }
        .login-feature-card {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 12px;
            padding: 0.85rem 1rem;
        }
        .login-feature-card strong {
            display: block;
            color: white !important;
            font-size: 0.88rem;
        }
        .login-feature-card span {
            color: #94A3B8 !important;
            font-size: 0.75rem;
        }
        .login-hero-footer {
            border-top: 1px solid rgba(255,255,255,0.14);
            padding-top: 1rem;
            margin-top: 1.5rem;
            display: flex;
            justify-content: space-between;
            color: #93C5FD !important;
            font-size: 0.78rem;
            font-weight: 600;
        }

        /* ================================================= */
        /* RESPONSIVE DESIGN & MOBILE OPTIMIZATIONS          */
        /* ================================================= */
        @media (max-width: 992px) {
            .block-container {
                padding: 1.2rem 1.2rem 2.5rem !important;
            }
            .hero-banner {
                padding: 1.5rem 1.6rem !important;
            }
            .hero-banner h1 {
                font-size: 1.7rem !important;
            }
            .login-hero-container {
                min-height: auto !important;
                padding: 1.8rem 1.5rem !important;
                margin-bottom: 1.2rem !important;
            }
            .login-hero-container h1 {
                font-size: 1.9rem !important;
            }
            .stat-box {
                padding: 0.9rem !important;
            }
            .stat-box-val {
                font-size: 1.6rem !important;
            }
        }

        @media (max-width: 768px) {
            .block-container {
                padding: 0.8rem 0.8rem 2rem !important;
            }
            .hero-banner {
                padding: 1.2rem 1.2rem !important;
                border-radius: 14px !important;
            }
            .hero-banner h1 {
                font-size: 1.45rem !important;
            }
            .login-hero-container {
                padding: 1.4rem 1.2rem !important;
                border-radius: 16px !important;
            }
            .login-hero-container h1 {
                font-size: 1.6rem !important;
            }
            .login-hero-container p {
                font-size: 0.88rem !important;
            }
            .login-feature-card {
                padding: 0.65rem 0.75rem !important;
            }
            .stat-box-val {
                font-size: 1.4rem !important;
            }
            /* Stack columns on small screens */
            [data-testid="column"] {
                min-width: 100% !important;
                flex: 1 1 100% !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# INTERACTIVE SIDEBAR NAVIGATION
# =========================================================

def render_sidebar(role, logout_callback):
    """
    Renders an interactive sidebar navigation menu with live tab switching,
    user profile display, and logout. Returns the currently selected menu item.
    """
    menus = {
        "student": [
            "🏠 Overview",
            "👤 My Profile",
            "🎯 AI Risk Analysis",
            "💡 Recommendations",
            "🔮 What-If Simulator",
            "🛡️ My Interventions",
            "📈 Prediction History",
        ],
        "admin": [
            "🏠 Executive Overview",
            "👥 Student Monitoring",
            "📊 Analytics & Models",
            "🚨 Intervention Center",
            "👨‍🏫 Mentor Assignment",
            "📄 Reports & Export",
        ],
        "mentor": [
            "🏠 Assigned Students",
            "📝 Follow-up Notes",
            "📌 Mentor Guidelines",
        ],
    }

    menu_items = menus.get(role, ["🏠 Dashboard"])
    role_key = f"{role}_nav_selection"

    # Apply pending programmatic navigation before widget creation
    pending_key = f"{role}_pending_nav"
    if pending_key in st.session_state:
        target_nav = st.session_state.pop(pending_key)
        if target_nav in menu_items:
            st.session_state[role_key] = target_nav

    user_name = st.session_state.get("name") or "User"
    campus_id = st.session_state.get("campus_id") or "ID"

    with st.sidebar:
        # Brand Header (Single line HTML)
        st.markdown(
            '<div style="padding: 0.2rem 0 0.8rem 0;"><div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF !important;">🎓 Student<span style="color:#60A5FA !important;">RiskAI</span></div><div style="font-size: 0.72rem; color: #94A3B8 !important; letter-spacing: 0.05em; margin-top: 2px;">Predict • Prevent • Support</div></div>',
            unsafe_allow_html=True
        )

        # User Profile Display (Single line HTML with pure white text)
        st.markdown(
            f'<div style="background: rgba(255,255,255,0.09); border: 1px solid rgba(255,255,255,0.18); border-radius: 12px; padding: 0.8rem 0.95rem; margin-bottom: 0.8rem;"><div style="color: #FFFFFF !important; font-weight: 850; font-size: 1rem; letter-spacing: -0.01em; margin-bottom: 3px;">👤 <span style="color: #FFFFFF !important;">{user_name}</span></div><div style="color: #93C5FD !important; font-size: 0.78rem; font-weight: 700;"><span style="color: #93C5FD !important;">{role.upper()}</span> • <span style="background: #2563EB; border: 1px solid #60A5FA; padding: 2px 7px; border-radius: 5px; color: #FFFFFF !important; font-weight: 800;">{campus_id}</span></div></div>',
            unsafe_allow_html=True
        )

        st.caption("NAVIGATION MENU")

        # Interactive Navigation Radio
        selected_item = st.radio(
            "Select Section",
            menu_items,
            key=role_key,
            label_visibility="collapsed"
        )

        st.divider()

        # Quick Tip (Single line HTML)
        st.markdown(
            '<div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.09); border-radius: 10px; padding: 0.75rem; font-size: 0.75rem; color: #CBD5E1 !important; line-height: 1.45;"><b style="color: #60A5FA !important;">💡 Proactive Support</b><br><span style="color: #E2E8F0 !important;">Early detection & intervention keeps students on track.</span></div>',
            unsafe_allow_html=True
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Logout Button
        if st.button("🚪  Sign Out", key="sidebar_logout_btn", use_container_width=True):
            logout_callback()

    return selected_item


# =========================================================
# REUSABLE UI COMPONENTS (SINGLE-LINE HTML, 100% ROBUST)
# =========================================================

def render_hero(kicker, title, description, badge_text=None):
    """Renders a clean modern hero banner without multiline HTML issues."""
    badge_html = f"<div style='margin-top:0.6rem;'><span style='background:rgba(255,255,255,0.18); padding:4px 12px; border-radius:8px; font-size:0.82rem; font-weight:700; color:#FFFFFF;'>{badge_text}</span></div>" if badge_text else ""
    html = f'<div class="hero-banner"><div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: #93C5FD; font-weight: 700; margin-bottom: 4px;">{kicker}</div><h1>{title}</h1><p>{description}</p>{badge_html}</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_stat_card(title, value, subtitle="", icon="📊"):
    """Renders a sleek stat card using a single-line HTML block."""
    html = f'<div class="stat-box"><div class="stat-box-title">{icon} {title}</div><div class="stat-box-val">{value}</div><div class="stat-box-sub">{subtitle}</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_risk_badge(risk_level, confidence=None):
    """Generates an HTML pill badge for risk levels."""
    r = str(risk_level).lower()
    conf_str = f" ({confidence:.1f}%)" if confidence is not None else ""
    
    if "high" in r:
        return f"<span style='background:#FEF2F2; color:#EF4444; border:1px solid #FCA5A5; padding:3px 10px; border-radius:999px; font-size:0.8rem; font-weight:700;'>🔴 HIGH RISK{conf_str}</span>"
    elif "medium" in r:
        return f"<span style='background:#FFFBEB; color:#B45309; border:1px solid #FCD34D; padding:3px 10px; border-radius:999px; font-size:0.8rem; font-weight:700;'>🟡 MEDIUM RISK{conf_str}</span>"
    else:
        return f"<span style='background:#ECFDF5; color:#10B981; border:1px solid #6EE7B7; padding:3px 10px; border-radius:999px; font-size:0.8rem; font-weight:700;'>🟢 LOW RISK{conf_str}</span>"


def render_login_hero():
    """Renders the stunning high-aesthetic login hero on a single clean block."""
    html = (
        '<div class="login-hero-container">'
        '<div>'
        '<div class="login-badge-pill">✨ AI-Powered Academic Success Platform</div>'
        '<h1>Predict Early.<br><span style="color: #60A5FA;">Prevent Failures.</span><br>Support Every Student.</h1>'
        '<p>StudentRiskAI leverages multi-indicator machine learning and proactive faculty mentoring to identify at-risk learners early and guide them to success.</p>'
        '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; margin-top: 1rem;">'
        '<div class="login-feature-card"><div style="font-size: 1.2rem; margin-bottom: 2px;">🎯</div><strong>95%+ Accuracy</strong><span>Multi-indicator risk model</span></div>'
        '<div class="login-feature-card"><div style="font-size: 1.2rem; margin-bottom: 2px;">🛡️</div><strong>Smart Action</strong><span>Tailored mentor support</span></div>'
        '</div>'
        '</div>'
        '<div class="login-hero-footer"><span>🏫 <b>Institutional Grade</b></span><span>🔒 <b>Secure & Private</b></span><span>⚡ <b>Real-Time ML</b></span></div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def style_plotly_chart(fig, height=340):
    """Applies a clean, modern design system to Plotly charts."""
    fig.update_layout(
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#475569", size=12),
        margin=dict(l=20, r=20, t=35, b=20),
        height=height,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_size=12,
            font_family="Plus Jakarta Sans, sans-serif",
            font_color="#FFFFFF",
            bordercolor="rgba(0,0,0,0)"
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#E2E8F0",
        tickfont=dict(color="#64748B")
    )
    fig.update_yaxes(
        gridcolor="#F1F5F9",
        linecolor="#E2E8F0",
        tickfont=dict(color="#64748B")
    )
    return fig
