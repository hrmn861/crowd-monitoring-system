"""
Authentication, Session Management & Role-Based Access Control (RBAC)
Enforces privacy boundaries and least-privilege access rules across the C2 dashboard.
"""

import streamlit as st
from app.db import log_audit

# Standard Demo Operational Personnel
MOCK_USERS = {
    "rev_01": {
        "user_id": "rev_01",
        "name": "Jane Doe (Lead Reviewer)",
        "email": "j.doe@pragatimaidan.example.org",
        "role": "reviewer"
    },
    "ops_02": {
        "user_id": "ops_02",
        "name": "Alex Mercer (Console Operator)",
        "email": "a.mercer@pragatimaidan.example.org",
        "role": "operator"
    },
    "adm_03": {
        "user_id": "adm_03",
        "name": "Col. Rajesh Singh (Venue Admin)",
        "email": "r.singh@pragatimaidan.example.org",
        "role": "admin"
    }
}

def init_auth():
    """Initializes user session state with default reviewer role if unset."""
    if "user" not in st.session_state:
        # Default to lead reviewer for development / preview
        st.session_state["user"] = MOCK_USERS["rev_01"]
        log_audit(
            user_id=st.session_state["user"]["user_id"],
            role=st.session_state["user"]["role"],
            action="login",
            page="init",
            details="Automated C2 session start"
        )

def get_current_user():
    init_auth()
    return st.session_state.get("user")

def set_current_user(user_key: str):
    if user_key in MOCK_USERS:
        st.session_state["user"] = MOCK_USERS[user_key]
        log_audit(
            user_id=st.session_state["user"]["user_id"],
            role=st.session_state["user"]["role"],
            action="switch_identity",
            page="auth",
            details=f"Switched role to {st.session_state['user']['role']}"
        )

def is_reviewer() -> bool:
    user = get_current_user()
    return user and user.get("role") == "reviewer"

def is_admin() -> bool:
    user = get_current_user()
    return user and user.get("role") == "admin"

def require_role(*allowed_roles, page_name: str = "current_page"):
    """
    Enforces RBAC on the current page. If unauthorized, logs the access violation
    to the immutable audit log and halts execution immediately.
    """
    user = get_current_user()
    if not user:
        st.error("Authentication Required. Please sign in to access the Operations Center.")
        st.stop()
    
    current_role = user.get("role")
    if current_role not in allowed_roles:
        log_audit(
            user_id=user["user_id"],
            role=current_role,
            action="access_denied",
            page=page_name,
            details=f"Attempted access to {page_name} requiring {allowed_roles}"
        )
        st.markdown(
            f"""
            <div class="locked-placeholder" style="margin-top: 2rem;">
                <div class="locked-icon">🔒</div>
                <h3 style="color: #F8FAFC; margin-bottom: 0.5rem;">Access Restricted by Security Policy</h3>
                <p style="color: #94A3B8; font-size: 0.95rem; max-width: 500px; margin: 0 auto;">
                    This section requires <b>{' / '.join(allowed_roles).upper()}</b> clearance. 
                    Your current assigned credential is <b>{current_role.upper()}</b>. 
                    All unauthorized access attempts are recorded in the system audit register.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.stop()
