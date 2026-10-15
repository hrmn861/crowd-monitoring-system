"""
Crowd Monitor — Immutable Governance & Security Audit Trail (10_Audit_Log.py)
Tamper-evident audit register tracking all logins, optical frame inspections, incident confirmations,
and dispatch events.
"""
import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st
import pandas as pd

from app.theme import inject_c2_theme
from app.components.header import render_top_hud
from app.components.banners import render_global_footer
from app.components.kpi_card import render_kpi_card_html
from app.components.navigation import render_c2_sidebar
from app.auth import require_role
from app.db import get_audit_logs

st.set_page_config(page_title="Audit Trail // Crowd Monitor C2", page_icon="📜", layout="wide")
inject_c2_theme()
render_c2_sidebar()
render_top_hud(page_title="Audit Log")

# Admin role only
require_role("admin", page_name="Audit Log")

st.markdown(
    """
    <div style="margin-bottom: 0.8rem;">
        <h2 style="color: #F8FAFC; margin-bottom: 0.2rem; font-size: 1.4rem;">
            SECURITY AUDIT LOG & COMPLIANCE REGISTER
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">
            Immutable chronological record of operator sessions, optical inspections, alert adjudications, and system mutations.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

logs = get_audit_logs(limit=150)

# Summary Cards
total_logs = len(logs)
frame_views = len([l for l in logs if l["action"] == "view_frame"])
escalations = len([l for l in logs if l["action"] == "escalate"])
denied = len([l for l in logs if l["action"] == "access_denied"])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_kpi_card_html("TOTAL AUDIT EVENTS", str(total_logs), subtext="Recorded in database"), unsafe_allow_html=True)
with c2:
    st.markdown(render_kpi_card_html("FRAME VIEW AUDITS", str(frame_views), subtext="Gated visual inspections"), unsafe_allow_html=True)
with c3:
    st.markdown(render_kpi_card_html("ESCALATION ACTIONS", str(escalations), subtext="Dispatches to control room"), unsafe_allow_html=True)
with c4:
    st.markdown(render_kpi_card_html("ACCESS DENIED FLAGS", str(denied), status_glow="alert" if denied > 0 else "normal", subtext="RBAC policy interventions"), unsafe_allow_html=True)

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# Filter Controls
with st.container():
    f_user, f_action, f_btn = st.columns([1.5, 1.5, 1], vertical_alignment="center")
    with f_user:
        all_users = list(set(l["user_id"] for l in logs)) if logs else []
        sel_user = st.selectbox("Filter by Personnel ID", ["ALL"] + all_users)
    with f_action:
        all_actions = list(set(l["action"] for l in logs)) if logs else []
        sel_action = st.selectbox("Filter by Action Type", ["ALL"] + all_actions)
    with f_btn:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh Log", use_container_width=True):
            st.rerun()

filtered_logs = logs
if sel_user != "ALL":
    filtered_logs = [l for l in filtered_logs if l["user_id"] == sel_user]
if sel_action != "ALL":
    filtered_logs = [l for l in filtered_logs if l["action"] == sel_action]

if filtered_logs:
    df_logs = pd.DataFrame(filtered_logs)[["id", "ts", "user_id", "role", "action", "page", "target_id", "details"]]
    df_logs["ts"] = df_logs["ts"].apply(lambda t: t.split(".")[0] if isinstance(t, str) else t)
    st.dataframe(df_logs, use_container_width=True, hide_index=True)
    
    csv_bytes = df_logs.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Audit Register (CSV)",
        data=csv_bytes,
        file_name="crowd_monitor_audit_trail.csv",
        mime="text/csv"
    )
else:
    st.info("No audit entries match the current filter criteria.")

render_global_footer()
