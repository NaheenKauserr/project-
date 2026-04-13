"""
Genesis AI Chatbot — Company Data Analysis Platform
MAIN APPLICATION ENTRY POINT — Phase 2 (Advanced Features)

Module integration map:
  Module 1  →  data_upload, dataset_profiling, data_quality
  Module 2  →  chatbot (NLP query, context memory, suggestions)
  Module 3  →  analytics (insights, recommendations, predictive engine)
  Module 4  →  dashboard (THIS FILE orchestrates the dashboard tab)
  Module 5  →  system (RBAC, voice, email scheduler — plugs in here)

Usage:
    streamlit run main_app.py
"""

import streamlit as st
import sys, os

# ── Path setup so all module folders are importable ──────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for folder in ["", "analytics", "chatbot", "dashboard", "nlp", "data"]:
    p = os.path.join(BASE_DIR, folder)
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Page config (must be first Streamlit call) ───────────────
st.set_page_config(
    page_title="Genesis AI | Company Data Analysis",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Safe imports ─────────────────────────────────────────────
def _safe(fn):
    try: return fn()
    except Exception as e:
        st.warning(f"Module import warning: {e}")
        return None

# Module 1
from module1.file_upload        import file_upload_section
from module1.dataset_profiling  import dataset_profiling_section
from module1.data_quality       import data_quality_section

# Module 4 — dashboard (new)
from dashboard import dashboard_section, render_sidebar, init_session_state, apply_dashboard_css

# Module 2 — chatbot (optional, graceful fallback)
try:
    from chatbot.chatbot_engine import render_chatbot_page
    HAS_CHATBOT = True
except Exception:
    HAS_CHATBOT = False

# Module 5 — system features (optional)
try:
    from system.rbac import check_access
    HAS_RBAC = True
except Exception:
    HAS_RBAC = False

# ── Global CSS patch (dark theme) ────────────────────────────
apply_dashboard_css()
init_session_state()

# ── Session defaults ─────────────────────────────────────────
if "logged_in"  not in st.session_state: st.session_state["logged_in"]  = False
if "user_role"  not in st.session_state: st.session_state["user_role"]  = "viewer"
if "user_name"  not in st.session_state: st.session_state["user_name"]  = ""

# ─────────────────────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────────────────────

USERS = {
    "admin" : {"password": "genesis123", "role": "admin",   "display": "NK (Admin)"},
    "analyst": {"password": "analyst123", "role": "analyst", "display": "Analyst User"},
    "viewer" : {"password": "view123",    "role": "viewer",  "display": "View-Only User"},
}

def login_page():
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0E1117, #1a0a2e) !important; }
    </style>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:2rem 0 1rem;">
            <div style="font-size:3.5rem">🤖</div>
            <h1 style="color:#A855F7;font-size:2rem;margin:0.3rem 0">Genesis AI</h1>
            <p style="color:#94A3B8;font-size:0.9rem">Company Data Analysis Platform</p>
        </div>""", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g. admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("🔐 Login", use_container_width=True, type="primary")

        if submitted:
            if username in USERS and USERS[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["user_name"] = USERS[username]["display"]
                st.session_state["user_role"] = USERS[username]["role"]
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

        st.markdown("""
        <div style="text-align:center;margin-top:1.5rem;font-size:0.78rem;color:#64748B">
            Demo credentials: admin / genesis123 &nbsp;|&nbsp; analyst / analyst123 &nbsp;|&nbsp; viewer / view123
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# MAIN APP (post-login)
# ─────────────────────────────────────────────────────────────

def main_app():
    role = st.session_state["user_role"]
    df   = st.session_state.get("uploaded_df")

    # ── Sidebar navigation ────────────────────────────────────
    with st.sidebar:
        st.markdown(f"👋 **{st.session_state['user_name']}** `[{role}]`")
        st.divider()

        # Navigation
        pages_all = [
            "📁 Data Upload",
            "📊 Dataset Profiling",
            "🔍 Data Quality",
            "📈 Analytics Dashboard",   # ← Module 4 (new)
            "🤖 AI Chatbot",
            "⚙️ System Settings",
        ]
        # Role-based page access
        if role == "viewer":
            pages = [p for p in pages_all if p not in ["⚙️ System Settings"]]
        else:
            pages = pages_all

        page = st.radio("Navigate:", pages, key="nav_page")

        st.divider()

        # Dataset info + filters (from Module 4's render_sidebar)
        render_sidebar(df)

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["logged_in","user_name","user_role","uploaded_df","file_name",
                      "chat_history","kpis_cache","insights_cache"]:
                st.session_state[k] = None if k not in ["logged_in"] else False
            st.rerun()

    # ── Page routing ──────────────────────────────────────────

    if page == "📁 Data Upload":
        file_upload_section()

    elif page == "📊 Dataset Profiling":
        if df is None:
            st.warning("⚠️ Please upload a dataset first.")
        else:
            dataset_profiling_section(df)

    elif page == "🔍 Data Quality":
        if df is None:
            st.warning("⚠️ Please upload a dataset first.")
        else:
            data_quality_section(df)

    elif page == "📈 Analytics Dashboard":
        # ── The new Module 4 dashboard
        dashboard_section()

    elif page == "🤖 AI Chatbot":
        if df is None:
            st.warning("⚠️ Please upload a dataset first.")
        elif HAS_CHATBOT:
            render_chatbot_page()
        else:
            st.info("Chatbot module not available in this environment.")
            st.markdown("The AI chatbot (Module 2) will appear here when integrated.")

    elif page == "⚙️ System Settings":
        if role != "admin":
            st.error("🔒 Access denied. Admin only.")
        else:
            st.title("⚙️ System Settings")
            st.info("Module 5 features (RBAC, Voice Chatbot, Email Scheduler) plug in here.")
            st.markdown("""
            **Available in Phase 2 — Module 5:**
            - Role-Based Access Control ✅ (active — see login roles above)
            - Voice-Based Chatbot Interaction 🔧 (Manu & Anoosha)
            - Email Report Scheduler 🔧 (Manu & Anoosha)
            """)


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

if not st.session_state["logged_in"]:
    login_page()
else:
    main_app()
