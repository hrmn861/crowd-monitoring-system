"""
Crowd Monitor — Incident Alert Triage Desk (4_Alerts.py)
Auditing and triaging occupancy and system health anomalies with human-in-the-loop review.
"""
import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st
import pandas as pd
from datetime import datetime, timezone

from app.theme import inject_c2_theme
from app.config import SNAPSHOTS_DIR
from app.components.header import render_top_hud
from app.components.banners import render_global_footer, render_stale_data_banner_if_needed
from app.components.status_badge import get_status_badge_html
from app.components.kpi_card import render_kpi_card_html
from app.components.frame_viewer import render_secure_frame_viewer
from app.components.navigation import render_c2_sidebar
from app.db import (
    get_all_alerts,
    get_alert_by_id,
    update_alert_review,
    get_zones,
    log_audit
)
from app.auth import is_reviewer, get_current_user

st.set_page_config(page_title="Incident Alerts // Crowd Monitor C2", page_icon="🚨", layout="wide")
inject_c2_theme()
render_c2_sidebar()
render_top_hud(page_title="Alerts")
render_stale_data_banner_if_needed()

st.markdown(
    """
    <div style="margin-bottom: 0.8rem;">
        <h2 style="color: #F8FAFC; margin-bottom: 0.2rem; font-size: 1.4rem;">
            INCIDENT AUDIT & REVIEW REQUEST TRIAGE DESK
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">
            Human-in-the-loop verification desk for occupancy surges and camera health anomalies.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

all_alerts = get_all_alerts()
user = get_current_user()

# 1. Summary Metrics Ribbon
open_cnt = len([a for a in all_alerts if a["status"] == "review_requested"])
conf_cnt = len([a for a in all_alerts if a["status"] == "confirmed"])
dism_cnt = len([a for a in all_alerts if a["status"] == "dismissed"])
escl_cnt = len([a for a in all_alerts if a["status"] == "escalated"])

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        render_kpi_card_html("AWAITING TRIAGE", f"{open_cnt}", status_glow="alert" if open_cnt > 0 else "normal", subtext="Action required"),
        unsafe_allow_html=True
    )
with m2:
    st.markdown(
        render_kpi_card_html("CONFIRMED (PENDING ESCALATION)", f"{conf_cnt}", status_glow="busy" if conf_cnt > 0 else None, subtext="Validated by reviewer"),
        unsafe_allow_html=True
    )
with m3:
    st.markdown(
        render_kpi_card_html("ESCALATED TO CONTROL ROOM", f"{escl_cnt}", subtext="Incident packages dispatched"),
        unsafe_allow_html=True
    )
with m4:
    st.markdown(
        render_kpi_card_html("DISMISSED (FALSE / CLEARED)", f"{dism_cnt}", subtext="Logged with operator note"),
        unsafe_allow_html=True
    )

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# 2. Tabs: Occupancy vs System Health
tab_occ, tab_health = st.tabs(["👥 OCCUPANCY ANOMALIES", "🖥️ SYSTEM HEALTH EVENTS"])

with tab_occ:
    occ_alerts = [a for a in all_alerts if a["kind"] == "occupancy"]
    if not occ_alerts:
        st.info("No occupancy alerts recorded.")
    else:
        # Split into list table (Left) and Inspector Drawer (Right)
        col_list, col_inspect = st.columns([1.3, 1.3])

        with col_list:
            st.markdown(
                """
                <div style="font-size: 0.75rem; text-transform: uppercase; color: #06B6D4; font-weight: 700; margin-bottom: 0.35rem;">
                    INCIDENT STREAM REGISTER
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Format rows for quick visual selection
            alert_labels = [f"#{a['alert_id']} | {a['ts'].split('.')[0]} | {a.get('zone_id', 'Z?')} | {a['status'].upper()}" for a in occ_alerts]
            selected_idx = st.selectbox("Select Incident to Triage", range(len(alert_labels)), format_func=lambda i: alert_labels[i])
            active_alert = occ_alerts[selected_idx]

            # Brief summary cards list
            for a in occ_alerts[:6]:
                is_sel = (a["alert_id"] == active_alert["alert_id"])
                border_style = "border-color: #06B6D4; box-shadow: 0 0 10px rgba(6,182,212,0.25);" if is_sel else ""
                st.markdown(
                    f"""
                    <div class="c2-card {'c2-card-alert' if a['status'] == 'review_requested' else ''}" style="padding: 0.65rem 0.9rem; margin-bottom: 0.4rem; {border_style}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-family: JetBrains Mono; font-size: 0.75rem; color: #38BDF8;">
                                #{a['alert_id']} &bull; {a['ts'].split('.')[0]}
                            </span>
                            {get_status_badge_html(a['status'])}
                        </div>
                        <div style="font-weight: 600; font-size: 0.88rem; color: #F8FAFC; margin-top: 0.2rem;">
                            {a.get('zone_name') or a.get('zone_id')} &bull; ~{round(a.get('count_at_trigger') or 0)} people
                        </div>
                        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.15rem;">
                            {a['reason']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col_inspect:
            st.markdown(
                """
                <div style="font-size: 0.75rem; text-transform: uppercase; color: #06B6D4; font-weight: 700; margin-bottom: 0.35rem;">
                    INCIDENT EVIDENCE & TRIAGE DRAWER
                </div>
                """,
                unsafe_allow_html=True
            )

            a_id = active_alert["alert_id"]
            a_zone = active_alert.get("zone_name") or active_alert.get("zone_id") or "Zone"
            a_status = active_alert["status"]
            snap_path = active_alert.get("snapshot_path")

            st.markdown(
                f"""
                <div class="c2-card c2-card-accent" style="margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 1rem; font-weight: 700; color: #F8FAFC;">
                            INCIDENT #{a_id} // {a_zone}
                        </span>
                        {get_status_badge_html(a_status)}
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem; margin-top: 0.6rem; font-family: JetBrains Mono; font-size: 0.8rem;">
                        <div>
                            <span style="color: #94A3B8; font-size: 0.7rem;">TRIGGER COUNT:</span><br>
                            <span style="color: #F8FAFC; font-weight: 700;">~{round(active_alert.get('count_at_trigger') or 0)} pers</span>
                        </div>
                        <div>
                            <span style="color: #94A3B8; font-size: 0.7rem;">TRIGGER DENSITY:</span><br>
                            <span style="color: #38BDF8; font-weight: 700;">{active_alert.get('density_at_trigger') or 0.0:.2f} /m²</span>
                        </div>
                        <div>
                            <span style="color: #94A3B8; font-size: 0.7rem;">DURATION:</span><br>
                            <span style="color: #F59E0B; font-weight: 700;">{active_alert.get('duration_s', 0)}s</span>
                        </div>
                    </div>
                    <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.4rem;">
                        <b>Rule Triggered:</b> <code>{active_alert['reason']}</code>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Snapshot Image (Gated to Reviewer)
            render_secure_frame_viewer(
                image_path=snap_path,
                caption=f"INCIDENT SNAPSHOT CAPTURED AT TRIGGER #{a_id}",
                show_controls=False,
                key_suffix=f"snap_{a_id}"
            )

            # Reviewer Triage Action Bar
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            if is_reviewer():
                st.markdown(
                    """
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: #38BDF8; font-weight: 700; margin-bottom: 0.3rem;">
                        SAFETY REVIEWER AUTHORIZATION ACTIONS
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                reviewer_note = st.text_input("Reviewer Audit Log Note", value="", placeholder="e.g., Congestion verified at turnstiles", key=f"note_{a_id}")
                
                c_btn_conf, c_btn_dism, c_btn_esc = st.columns([1, 1, 1.2])
                with c_btn_conf:
                    if st.button("✓ Confirm Incident", key=f"conf_{a_id}", use_container_width=True):
                        update_alert_review(a_id, "confirmed", user["name"], reviewer_note)
                        log_audit(user["user_id"], user["role"], "confirm", "alerts", str(a_id), reviewer_note)
                        st.success(f"Incident #{a_id} Confirmed.")
                        st.rerun()

                with c_btn_dism:
                    if st.button("✕ Dismiss Alert", key=f"dism_{a_id}", use_container_width=True):
                        update_alert_review(a_id, "dismissed", user["name"], reviewer_note or "Dismissed by reviewer")
                        log_audit(user["user_id"], user["role"], "dismiss", "alerts", str(a_id), reviewer_note)
                        st.info(f"Alert #{a_id} Dismissed.")
                        st.rerun()

                with c_btn_esc:
                    is_disabled = (a_status != "confirmed")
                    if st.button("🚨 Proceed to Escalate", key=f"esc_{a_id}", disabled=is_disabled, use_container_width=True):
                        st.session_state["target_escalation_alert_id"] = a_id
                        st.switch_page("pages/5_Escalation.py")
                
                if a_status != "confirmed":
                    st.caption("ℹ️ Safety Policy: You must confirm the incident before escalation is unlocked.")
            else:
                st.info("🔒 Incident confirmation and escalation require 'Safety Reviewer' clearance.")

with tab_health:
    health_alerts = [a for a in all_alerts if a["kind"] == "health"]
    if health_alerts:
        for ha in health_alerts:
            st.markdown(
                f"""
                <div class="c2-card" style="padding: 0.8rem 1rem; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-family: JetBrains Mono; font-size: 0.8rem; color: #F59E0B;">
                            HEALTH ANOMALY #{ha['alert_id']} &bull; {ha['ts']}
                        </span>
                        {get_status_badge_html(ha['status'])}
                    </div>
                    <div style="font-size: 0.9rem; font-weight: 600; color: #F8FAFC; margin-top: 0.3rem;">
                        {ha['reason']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.success("No system health or camera anomalies logged.")

render_global_footer()
