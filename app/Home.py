"""
Crowd Monitor — Tactical C2 Operations Center (Home / Overview)
Primary situational awareness cockpit for real-time crowd counting and zone occupancy review.
"""
import sys
import os
from pathlib import Path

# Ensure project root directory is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

from app.theme import inject_c2_theme, clean_html
from app.config import (
    get_app_config,
    LATEST_FRAME_PATH,
    GLOBAL_FOOTER_DISCLAIMER
)
from app.db import (
    init_db_if_needed,
    get_zones,
    get_live_zone_states,
    get_total_headcount_summary,
    get_open_alerts_count,
    get_recent_alerts,
    is_telemetry_stale,
    get_camera_health
)
from app.components.header import render_top_hud
from app.components.banners import render_stale_data_banner_if_needed, render_global_footer
from app.components.kpi_card import render_kpi_card_html
from app.components.zone_card import render_zone_card_html
from app.components.frame_viewer import render_secure_frame_viewer
from app.components.status_badge import get_status_badge_html
from app.components.navigation import render_c2_sidebar
from app.auth import get_current_user

# Set page config
st.set_page_config(
    page_title="Crowd Monitor C2 Ops",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom Obsidian Design System & Sidebar Navigation
inject_c2_theme()
init_db_if_needed()
render_c2_sidebar()

# Top Command HUD
render_top_hud(page_title="Overview")

# Stale / Outage Check
render_stale_data_banner_if_needed()
is_stale, age, latest_ts = is_telemetry_stale()

# Main Telemetry Fragment
@st.fragment(run_every=3)
def render_live_telemetry_grid():
    app_cfg = get_app_config()
    if app_cfg.get("camera", {}).get("mode") == "simulated_live":
        from app.db import inject_fresh_simulated_tick
        inject_fresh_simulated_tick()

    stale_active, _, _ = is_telemetry_stale()
    summary = get_total_headcount_summary()
    open_alerts = get_open_alerts_count()
    health = get_camera_health()
    cam_status = health.get("status", "offline") if health else "offline"
    zones = get_zones()
    zone_states = get_live_zone_states()
    recent_alerts = get_recent_alerts(limit=5)

    # 1. Headline Tactical KPI Ribbon
    k1, k2, k3, k4, k5 = st.columns(5)
    
    with k1:
        delta_str = f"{'+' if summary['delta_5m'] > 0 else ''}{summary['delta_5m']} vs 5m" if not stale_active else "0"
        st.markdown(
            render_kpi_card_html(
                label="TOTAL ESTIMATED CROWD",
                value=f"~{summary['total_now']}",
                delta=delta_str,
                delta_positive_is_good=False,
                subtext="Ensemble model sum across zones",
                is_stale=stale_active
            ),
            unsafe_allow_html=True
        )

    with k2:
        alert_zones = summary["alert_zones"]
        status_glow = "alert" if alert_zones > 0 else "normal"
        st.markdown(
            render_kpi_card_html(
                label="ANOMALOUS ZONES",
                value=f"{alert_zones} / {len(zones)}",
                status_glow=status_glow if not stale_active else None,
                subtext="Exceeding normal flow rate",
                is_stale=stale_active
            ),
            unsafe_allow_html=True
        )

    with k3:
        max_dens = summary["max_density"]
        dens_glow = "alert" if max_dens >= 2.0 else ("busy" if max_dens >= 1.5 else "normal")
        st.markdown(
            render_kpi_card_html(
                label="PEAK DENSITY INDEX",
                value=f"{max_dens:.2f}",
                subtext="People per square metre (m²)",
                status_glow=dens_glow if not stale_active else None,
                is_stale=stale_active
            ),
            unsafe_allow_html=True
        )

    with k4:
        # Determine dominant active inference engine
        active_engine = "YOLOv8s + DM-Count"
        st.markdown(
            render_kpi_card_html(
                label="INFERENCE PIPELINE",
                value="HYBRID",
                subtext="Dynamic Hysteresis Switch (45)",
                is_stale=stale_active
            ),
            unsafe_allow_html=True
        )

    with k5:
        st.markdown(
            render_kpi_card_html(
                label="ACTIVE REVIEW REQUESTS",
                value=f"{open_alerts}",
                status_glow="alert" if open_alerts > 0 else "normal",
                subtext="Awaiting reviewer triage",
                is_stale=stale_active
            ),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # 2. Zone Telemetry Status Strip
    st.markdown(
        clean_html("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
            <span style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: #06B6D4; font-weight: 700;">
                LIVE ZONE TOPOLOGY TELEMETRY
            </span>
            <span style="font-size: 0.75rem; color: #94A3B8;">Auto-refreshing every 3s</span>
        </div>
        """),
        unsafe_allow_html=True
    )

    if zones:
        z_cols = st.columns(len(zones))
        for idx, z in enumerate(zones):
            z_id = z["zone_id"]
            z_state = zone_states.get(z_id, {
                "zone_id": z_id,
                "name": z["name"],
                "final_count": 0,
                "capacity": z["capacity"],
                "density_pm2": 0.0,
                "safe_density_limit": z["safe_density_limit"],
                "trend": "flat",
                "status": "no_data",
                "method": "yolo"
            })
            with z_cols[idx]:
                st.markdown(render_zone_card_html(z_state, is_stale=stale_active), unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # 3. Two-Column Situational Layout
    col_visual, col_alerts = st.columns([1.5, 1.0])

    with col_visual:
        st.markdown(
            clean_html("""
            <div style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: #06B6D4; font-weight: 700; margin-bottom: 0.4rem;">
                OPTICAL SENSOR FEED & ZONE MAPPING
            </div>
            """),
            unsafe_allow_html=True
        )
        frame_file = str(LATEST_FRAME_PATH) if LATEST_FRAME_PATH.exists() else None
        render_secure_frame_viewer(
            image_path=frame_file,
            caption="CAM-01 Atrium Sensor (Active Polygon Overlay)",
            zones=zones,
            show_controls=True,
            key_suffix="home_feed"
        )

    with col_alerts:
        st.markdown(
            clean_html(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <span style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: #EF4444; font-weight: 700;">
                    RECENT REVIEW REQUESTS
                </span>
                <span class="c2-badge {'badge-alert' if open_alerts > 0 else 'badge-normal'}">
                    {open_alerts} PENDING
                </span>
            </div>
            """),
            unsafe_allow_html=True
        )

        if recent_alerts:
            for alert in recent_alerts:
                a_id = alert["alert_id"]
                a_ts = alert["ts"].split(".")[0]
                a_zone = alert.get("zone_name") or alert.get("zone_id") or "General"
                a_reason = alert["reason"]
                a_status = alert["status"]
                
                st.markdown(
                    clean_html(f"""
                    <div class="c2-card {'c2-card-alert' if a_status == 'review_requested' else ''}" style="padding: 0.8rem 1rem; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-family: JetBrains Mono; font-size: 0.75rem; color: #38BDF8;">{a_ts}</span>
                            {get_status_badge_html(a_status)}
                        </div>
                        <div style="font-size: 0.88rem; font-weight: 600; color: #F8FAFC; margin-top: 0.3rem;">
                            {a_zone}
                        </div>
                        <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 0.2rem;">
                            Trigger: <code>{a_reason}</code>
                        </div>
                    </div>
                    """),
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                clean_html("""
                <div class="c2-card" style="text-align: center; padding: 2rem 1rem; color: #64748B;">
                    <div style="font-size: 1.8rem; color: #10B981;">✓</div>
                    <div style="font-size: 0.9rem; font-weight: 600; color: #94A3B8; margin-top: 0.35rem;">
                        ALL ZONES NOMINAL
                    </div>
                    <div style="font-size: 0.75rem; color: #64748B;">No open review requests at this time.</div>
                </div>
                """),
                unsafe_allow_html=True
            )
        
        st.markdown(
            clean_html("""
            <div style="text-align: right; margin-top: 0.5rem;">
                <a href="/Alerts" target="_self" style="color: #06B6D4; font-size: 0.8rem; text-decoration: none; font-weight: 600;">
                    Open Full Incident Triage Desk →
                </a>
            </div>
            """),
            unsafe_allow_html=True
        )

# Render main loop
render_live_telemetry_grid()

# Mandatory Ethical Footer
render_global_footer()
