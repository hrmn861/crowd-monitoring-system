"""
Global HUD Command Header
Displays real-time telemetry heartbeat, camera status, stream mode, active alerts counter,
and user authentication/role selector.
"""

import streamlit as st
from datetime import datetime, timezone
from app.config import get_app_config
from app.db import (
    get_camera_health,
    get_latest_counts_timestamp,
    get_open_alerts_count,
    is_telemetry_stale
)
from app.auth import get_current_user, set_current_user, MOCK_USERS
from app.components.status_badge import get_status_badge_html
from app.theme import clean_html

def render_top_hud(page_title: str = ""):
    """Renders the top Tactical C2 HUD banner."""
    app_cfg = get_app_config()
    site_name = app_cfg.get("site", {}).get("name", "Site Terminal")
    cam_id = app_cfg.get("camera", {}).get("id", "CAM-01")
    mode_name = "SIMULATED LIVE" if app_cfg.get("camera", {}).get("mode") == "simulated_live" else "LIVE STREAM"
    
    health = get_camera_health()
    cam_status = health.get("status", "offline") if health else "offline"
    fps = health.get("fps", 0.0) if health else 0.0
    
    is_stale, age, latest_ts = is_telemetry_stale()
    age_str = f"{int(age)}s ago" if age is not None else "never"
    
    open_alerts = get_open_alerts_count()
    current_user = get_current_user()

    # Layout Header Columns — Give col2 ample room so telemetry badges never wrap
    col1, col2, col3 = st.columns([1.1, 2.3, 1.0], vertical_alignment="center")

    with col1:
        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; gap: 0.85rem;">
                <div style="width: 10px; height: 10px; border-radius: 50%; background: {'#10B981' if cam_status == 'online' and not is_stale else '#EF4444'}; box-shadow: 0 0 10px {'#10B981' if cam_status == 'online' and not is_stale else '#EF4444'};"></div>
                <div>
                    <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #06B6D4; font-weight: 700;">
                        C2 OPERATIONS HUB &bull; {mode_name}
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; letter-spacing: -0.01em; white-space: nowrap;">
                        {site_name} <span style="font-size: 0.8rem; font-weight: 400; color: #94A3B8;">[{cam_id}]</span>
                    </div>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

    with col2:
        # Camera Status & Telemetry Freshness Badges — strictly single row horizontal layout
        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; justify-content: flex-start; gap: 0.45rem; flex-wrap: nowrap; white-space: nowrap; overflow-x: auto;">
                <div>{get_status_badge_html(cam_status, f"CAM {cam_status.upper()}")}</div>
                <div class="c2-badge badge-cyan" style="white-space: nowrap;"><span>⚡</span> {fps:.1f} FPS</div>
                <div class="c2-badge {'badge-alert' if is_stale else 'badge-stale'}" style="white-space: nowrap;"><span>⏱</span> {age_str}</div>
                <div class="c2-badge {'badge-alert' if open_alerts > 0 else 'badge-normal'}" style="white-space: nowrap;">
                    <span>⚠️</span> {open_alerts} REVIEW REQ
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

    with col3:
        # User & Role Switcher
        user_options = list(MOCK_USERS.keys())
        current_idx = 0
        if current_user:
            for idx, k in enumerate(user_options):
                if MOCK_USERS[k]["user_id"] == current_user["user_id"]:
                    current_idx = idx
                    break

        selected_key = st.selectbox(
            "Operator Clearance",
            options=user_options,
            index=current_idx,
            format_func=lambda k: f"{MOCK_USERS[k]['role'].upper()} - {MOCK_USERS[k]['name'].split('(')[0].strip()}",
            label_visibility="collapsed",
            key=f"user_select_{page_title}"
        )
        if selected_key and current_user and selected_key != current_user["user_id"]:
            set_current_user(selected_key)
            st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 0.5rem 0 1rem 0;'>", unsafe_allow_html=True)
