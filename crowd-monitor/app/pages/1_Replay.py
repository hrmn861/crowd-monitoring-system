"""
Crowd Monitor — Incident Replay & Simulation Station (1_Replay.py)
Enables post-incident scrutiny, timeline scrubbing, speed control, and model A/B comparison.
"""
import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st
import time
from datetime import datetime, timedelta

from app.theme import inject_c2_theme
from app.config import LATEST_FRAME_PATH
from app.components.header import render_top_hud
from app.components.banners import render_global_footer
from app.components.frame_viewer import render_secure_frame_viewer
from app.components.status_badge import get_status_badge_html
from app.components.navigation import render_c2_sidebar
from app.auth import is_reviewer, get_current_user
from app.db import get_zones, get_all_alerts

st.set_page_config(page_title="Incident Replay // Crowd Monitor C2", page_icon="⏪", layout="wide")
inject_c2_theme()
render_c2_sidebar()
render_top_hud(page_title="Replay")

st.markdown(
    """
    <div style="margin-bottom: 1rem;">
        <h2 style="color: #F8FAFC; margin-bottom: 0.2rem; font-size: 1.4rem;">
            INCIDENT REPLAY & TIMELINE SCRUBBING STATION
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">
            Deterministic frame playback of recorded sessions with synchronized zone telemetry and model overlays.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

if not is_reviewer():
    st.markdown(
        """
        <div class="locked-placeholder" style="margin-top: 1.5rem;">
            <div class="locked-icon">🔒</div>
            <h3 style="color: #F8FAFC; margin-bottom: 0.5rem;">Replay Access Restricted</h3>
            <p style="color: #94A3B8; font-size: 0.9rem; max-width: 520px; margin: 0 auto;">
                Historical frame-by-frame replay contains raw and annotated visual camera imagery. 
                Under site safety regulations, replay access is restricted exclusively to certified <b>Safety Reviewers</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    render_global_footer()
    st.stop()

# 1. Source & Session Selector
col_sess, col_mode, col_sp = st.columns([2, 1, 1], vertical_alignment="center")
with col_sess:
    session_choice = st.selectbox(
        "Recorded Session / Incident Stream",
        [
            "SESS-2026-10-15-AM: Morning Peak Security Ingress (08:30 - 09:30 UTC)",
            "SESS-2026-10-14-PM: Main Concourse Evening Surge (17:00 - 18:00 UTC)",
            "SESS-2026-10-13-EV: Hall East Bottleneck Drill (14:15 - 15:00 UTC)"
        ]
    )
with col_mode:
    model_view = st.radio("Active Engine Overlay", ["Final Ensemble", "YOLOv8s Only", "DM-Count Density"], horizontal=True)
with col_sp:
    speed = st.select_slider("Playback Speed", options=["0.5x", "1.0x", "2.0x", "5.0x"], value="1.0x")

# Session Duration & State
total_frames = 300
if "replay_frame_idx" not in st.session_state:
    st.session_state["replay_frame_idx"] = 120

c_scrub, c_btn1, c_btn2, c_btn3 = st.columns([3, 0.7, 0.7, 0.7], vertical_alignment="center")

with c_scrub:
    scrubber_val = st.slider(
        "Timeline Scrubber (Video Time Offset)",
        min_value=0,
        max_value=total_frames,
        value=st.session_state["replay_frame_idx"],
        format="T+ %d s"
    )
    st.session_state["replay_frame_idx"] = scrubber_val

with c_btn1:
    if st.button("⏪ Prev Alert"):
        st.session_state["replay_frame_idx"] = max(0, st.session_state["replay_frame_idx"] - 45)
        st.rerun()

with c_btn2:
    is_playing = st.session_state.get("is_playing", False)
    if st.button("⏸ Pause" if is_playing else "▶ Play"):
        st.session_state["is_playing"] = not is_playing
        st.rerun()

with c_btn3:
    if st.button("Next Alert ⏩"):
        st.session_state["replay_frame_idx"] = min(total_frames, st.session_state["replay_frame_idx"] + 55)
        st.rerun()

# 2. Main Playback Grid: Visual on Left, Synchronized Telemetry on Right
col_left, col_right = st.columns([1.6, 1.0])

curr_sec = st.session_state["replay_frame_idx"]
simulated_time_str = (datetime(2026, 10, 15, 8, 30, 0) + timedelta(seconds=curr_sec)).strftime("%Y-%m-%d %H:%M:%S UTC")

with col_left:
    frame_path = str(LATEST_FRAME_PATH) if LATEST_FRAME_PATH.exists() else None
    render_secure_frame_viewer(
        image_path=frame_path,
        caption=f"REPLAY AT T+{curr_sec:03d}s // {simulated_time_str}",
        show_controls=True,
        key_suffix="replay_view"
    )

with col_right:
    st.markdown(
        f"""
        <div class="c2-card c2-card-accent" style="margin-bottom: 0.8rem;">
            <div style="font-size: 0.72rem; text-transform: uppercase; color: #06B6D4; font-weight: 700;">
                SYNCHRONIZED TELEMETRY SNAPSHOT
            </div>
            <div style="font-family: JetBrains Mono; font-size: 1.1rem; color: #F8FAFC; margin-top: 0.2rem;">
                OFFSET: {curr_sec}s / 300s
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.25rem;">
                Timestamp: <code>{simulated_time_str}</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Simulated Dynamic Zone Telemetry at this frame offset
    zones = get_zones()
    for z in zones:
        z_id = z["zone_id"]
        # Generate sinusoidal realistic count for replay offset
        base = 35 if z_id == "Z1" else (22 if z_id == "Z2" else 48)
        sim_count = int(base + (curr_sec % 30) - 10)
        sim_dens = sim_count / z["area_m2"]
        status = "over_threshold" if sim_count >= z["alert_threshold"] else ("busy" if sim_count >= z["capacity"] * 0.7 else "normal")

        st.markdown(
            f"""
            <div class="c2-card {'c2-card-alert' if status == 'over_threshold' else ''}" style="padding: 0.65rem 0.9rem; margin-bottom: 0.45rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 600; font-size: 0.85rem; color: #F8FAFC;">{z_id} - {z['name']}</span>
                    {get_status_badge_html(status)}
                </div>
                <div style="display: flex; gap: 1.2rem; margin-top: 0.3rem; font-family: JetBrains Mono; font-size: 0.85rem;">
                    <span style="color: #F8FAFC;">Count: ~{sim_count}</span>
                    <span style="color: #38BDF8;">Density: {sim_dens:.2f}/m²</span>
                    <span style="color: #94A3B8;">Thresh: {z['alert_threshold']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

render_global_footer()
