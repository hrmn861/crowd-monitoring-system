"""
Crowd Monitor — Human-in-the-Loop Escalation Center (5_Escalation.py)
Strict safety protocol: review, confirm against live optical stream, then build official escalation package.
"""
import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timezone

from app.theme import inject_c2_theme
from app.config import get_app_config, GLOBAL_FOOTER_DISCLAIMER, SAFETY_JURISDICTION_NOTE
from app.components.header import render_top_hud
from app.components.banners import render_global_footer, render_stale_data_banner_if_needed
from app.components.status_badge import get_status_badge_html
from app.components.frame_viewer import render_secure_frame_viewer
from app.components.navigation import render_c2_sidebar
from app.db import (
    get_all_alerts,
    get_alert_by_id,
    insert_escalation_request,
    get_escalations,
    retry_escalation,
    log_audit
)
from app.auth import require_role, get_current_user

st.set_page_config(page_title="Escalation Center // Crowd Monitor C2", page_icon="📡", layout="wide")
inject_c2_theme()
render_c2_sidebar()
render_top_hud(page_title="Escalation")
render_stale_data_banner_if_needed()

# Safety clearance gate
require_role("reviewer", page_name="Escalation Desk")
user = get_current_user()
app_cfg = get_app_config()

st.markdown(
    """
    <div style="margin-bottom: 0.8rem;">
        <h2 style="color: #F8FAFC; margin-bottom: 0.2rem; font-size: 1.4rem;">
            INCIDENT ESCALATION & CONTROL ROOM DISPATCH CENTER
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">
            Mandatory human-in-the-loop review-then-escalate protocol. Automation never directly alerts external emergency services.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

all_alerts = get_all_alerts()
confirmed_alerts = [a for a in all_alerts if a["status"] in ("confirmed", "review_requested")]

# 1. Review Queue & Active Selection
col_queue, col_workspace = st.columns([1.1, 1.7])

with col_queue:
    st.markdown(
        """
        <div style="font-size: 0.75rem; text-transform: uppercase; color: #06B6D4; font-weight: 700; margin-bottom: 0.4rem;">
            1. PENDING VERIFICATION QUEUE
        </div>
        """,
        unsafe_allow_html=True
    )
    if not confirmed_alerts:
        st.markdown(
            """
            <div class="c2-card" style="text-align: center; padding: 2rem 1rem; color: #64748B;">
                ✓ No active alerts pending verification or escalation.
            </div>
            """,
            unsafe_allow_html=True
        )
        active_alert = None
    else:
        # Check if pre-selected via session state
        target_id = st.session_state.get("target_escalation_alert_id")
        def_idx = 0
        if target_id:
            for idx, a in enumerate(confirmed_alerts):
                if a["alert_id"] == target_id:
                    def_idx = idx
                    break

        alert_opts = [f"#{a['alert_id']} | {a['zone_id']} | {a['status'].upper()}" for a in confirmed_alerts]
        chosen_idx = st.selectbox("Select Alert to Process", range(len(alert_opts)), index=def_idx, format_func=lambda i: alert_opts[i])
        active_alert = confirmed_alerts[chosen_idx]

        for a in confirmed_alerts:
            is_active = (active_alert and a["alert_id"] == active_alert["alert_id"])
            border_css = "border-color: #06B6D4; box-shadow: 0 0 10px rgba(6,182,212,0.25);" if is_active else ""
            st.markdown(
                f"""
                <div class="c2-card" style="padding: 0.65rem 0.85rem; margin-bottom: 0.4rem; {border_css}">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-family: JetBrains Mono; font-size: 0.75rem; color: #38BDF8;">#{a['alert_id']} &bull; {a['ts'].split('.')[0]}</span>
                        {get_status_badge_html(a['status'])}
                    </div>
                    <div style="font-weight: 600; font-size: 0.85rem; color: #F8FAFC; margin-top: 0.2rem;">
                        {a.get('zone_name') or a['zone_id']} (~{round(a.get('count_at_trigger') or 0)} people)
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

with col_workspace:
    st.markdown(
        """
        <div style="font-size: 0.75rem; text-transform: uppercase; color: #06B6D4; font-weight: 700; margin-bottom: 0.4rem;">
            2. ESCALATION MANIFEST BUILDER & SIGN-OFF
        </div>
        """,
        unsafe_allow_html=True
    )

    if not active_alert:
        st.info("Select an alert from the queue to initiate escalation review.")
    else:
        a_id = active_alert["alert_id"]
        is_already_confirmed = (active_alert["status"] == "confirmed")
        
        # Build escalation payload preview dictionary
        site_info = app_cfg.get("site", {})
        recipient_target = site_info.get("control_room_contact", "ops-control@pragatimaidan.example.org")
        
        summary_payload = {
            "title": "Venue Escalation Summary",
            "site": {
                "name": site_info.get("name", "Site Terminal"),
                "address": site_info.get("address", "Venue Location Address")
            },
            "zone": {
                "id": active_alert.get("zone_id"),
                "name": active_alert.get("zone_name"),
                "area_m2": active_alert.get("area_m2", 30.0)
            },
            "count_estimate": round(active_alert.get("count_at_trigger") or 0),
            "density_pm2": round(active_alert.get("density_at_trigger") or 0.0, 2),
            "trend": "up",
            "alert_reason": active_alert.get("reason"),
            "alert_time_utc": active_alert.get("ts"),
            "escalated_by": user["name"],
            "escalated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "note": "",
            "disclaimer": "Counts are model estimates. Venue control room decides whether to contact emergency services (112 in India)."
        }

        # Snapshot display
        render_secure_frame_viewer(
            image_path=active_alert.get("snapshot_path"),
            caption=f"EVIDENCE ATTACHMENT FOR ALERT #{a_id}",
            show_controls=False,
            key_suffix=f"esc_snap_{a_id}"
        )

        st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)
        
        # Incident Manifest Card
        st.markdown(
            f"""
            <div class="c2-card c2-card-accent" style="padding: 1rem;">
                <div style="font-family: JetBrains Mono; font-size: 0.72rem; color: #06B6D4; text-transform: uppercase;">
                    OFFICIAL DISPATCH MANIFEST // VENUE CONTROL ROOM ONLY
                </div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC; margin-top: 0.2rem;">
                    {site_info.get('name')} &bull; Zone {active_alert.get('zone_id')}
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.25rem;">
                    Address: {site_info.get('address')}
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.6rem; font-family: JetBrains Mono; font-size: 0.82rem;">
                    <div>Estimated Crowd: <b style="color: #F8FAFC;">~{summary_payload['count_estimate']} people</b></div>
                    <div>Measured Density: <b style="color: #38BDF8;">{summary_payload['density_pm2']:.2f} /m²</b></div>
                    <div>Recipient: <b style="color: #818CF8;">{recipient_target}</b></div>
                    <div>Authorized Reviewer: <b style="color: #10B981;">{user['name']}</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Operator Affirmation Form
        reviewer_note = st.text_area("Reviewer Observations / Dispatch Instructions", placeholder="e.g. Ingress queue backing up towards exterior security gates; steward intervention recommended.", key=f"esc_note_{a_id}")
        summary_payload["note"] = reviewer_note

        legal_affirmation = st.checkbox(
            "I verify that I have inspected the live camera feed, confirmed this condition represents a genuine crowd management concern, and hereby authorize this escalation summary dispatch to the venue control room.",
            value=False,
            key=f"legal_chk_{a_id}"
        )

        btn_dispatch = st.button(
            "🚀 Dispatch Escalation Summary to Control Room",
            disabled=(not legal_affirmation),
            type="primary",
            use_container_width=True
        )

        if btn_dispatch:
            esc_id = insert_escalation_request(
                alert_id=a_id,
                escalated_by=user["name"],
                summary_dict=summary_payload,
                snapshot_path=active_alert.get("snapshot_path"),
                recipient=recipient_target,
                note=reviewer_note
            )
            log_audit(user["user_id"], user["role"], "escalate", "escalation", str(a_id), f"Dispatched Escalation #{esc_id}")
            st.success(f"✓ Escalation Package #{esc_id} successfully dispatched to {recipient_target}.")
            time.sleep(1)
            st.rerun()

st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)

# 3. Escalation History Register
st.markdown(
    """
    <div style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: #06B6D4; font-weight: 700; margin-bottom: 0.5rem;">
        3. ESCALATION AUDIT LOG & DISPATCH REGISTER
    </div>
    """,
    unsafe_allow_html=True
)

esc_history = get_escalations(limit=20)
if esc_history:
    hist_rows = []
    for e in esc_history:
        hist_rows.append({
            "Esc ID": f"#{e['esc_id']}",
            "Timestamp": e["ts"].split(".")[0],
            "Alert ID": f"#{e['alert_id']}",
            "Zone": e.get("zone_name") or e.get("zone_id") or "Z?",
            "Escalated By": e["escalated_by"],
            "Target Recipient": e["recipient"],
            "Status": e["delivery_status"].upper(),
            "Attempts": e["attempts"]
        })
    df_esc = pd.DataFrame(hist_rows)
    st.dataframe(df_esc, use_container_width=True, hide_index=True)
else:
    st.info("No prior escalations logged.")

render_global_footer()
