"""
Banners and Global Footer components
"""

import streamlit as st
from app.config import GLOBAL_FOOTER_DISCLAIMER, SAFETY_JURISDICTION_NOTE
from app.db import is_telemetry_stale, get_camera_health
from app.theme import clean_html

def render_stale_data_banner_if_needed():
    """Renders high-visibility alert banner if telemetry is stale or camera offline."""
    is_stale, age, latest_ts = is_telemetry_stale()
    health = get_camera_health()
    camera_status = health["status"] if health else "offline"

    if is_stale or camera_status == "offline":
        age_str = f"{int(age)}s ago" if age else "unknown"
        col_banner, col_btn = st.columns([3.8, 1.2], vertical_alignment="center")
        with col_banner:
            st.markdown(
                clean_html(f"""
                <div class="stale-banner" style="margin-bottom: 0;">
                    <span style="font-size: 1.4rem;">⚠️</span>
                    <div>
                        <b>TELEMETRY OUTAGE / STALE STREAM DETECTED:</b> 
                        No fresh counting packets received for <b>{age_str}</b>. 
                        The camera feed or background worker process may be offline. 
                        <i>Telemetry metrics below are locked in failsafe mode. Do not interpret flat counts as zero crowd.</i>
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )
        with col_btn:
            if st.button("⚡ Resume Live Feed", width="stretch", key="btn_resume_live_feed"):
                from app.db import inject_fresh_simulated_tick
                inject_fresh_simulated_tick()
                st.rerun()

def render_global_footer():
    """Renders mandatory ethical and safety disclaimer at the bottom of every page."""
    st.markdown(
        clean_html(f"""
        <div class="c2-footer">
            <p><b>SAFETY NOTICE:</b> {GLOBAL_FOOTER_DISCLAIMER}</p>
            <p style="margin-top: 0.25rem;"><b>JURISDICTION:</b> {SAFETY_JURISDICTION_NOTE}</p>
            <p style="margin-top: 0.25rem; opacity: 0.7;">Crowd Monitor System v2.4 (Decision-Support Protocol) | Zero Face Storage | Zero Biometric Profiling</p>
        </div>
        """),
        unsafe_allow_html=True
    )
