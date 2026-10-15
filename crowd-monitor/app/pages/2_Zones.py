"""
Crowd Monitor — Zone Topology & Spatial Drilldown (2_Zones.py)
Visualizes floor layout polygons, comparative zone data grid, and interactive zone drilldown.
"""
import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

from app.theme import inject_c2_theme
from app.config import LATEST_FRAME_PATH
from app.components.header import render_top_hud
from app.components.banners import render_global_footer, render_stale_data_banner_if_needed
from app.components.charts import build_zone_schematic_map, build_zone_timeseries_chart
from app.components.status_badge import get_status_badge_html
from app.components.kpi_card import render_kpi_card_html
from app.components.navigation import render_c2_sidebar
from app.db import (
    get_zones,
    get_live_zone_states,
    get_counts_time_series,
    get_all_alerts,
    is_telemetry_stale
)
from app.auth import is_reviewer

st.set_page_config(page_title="Zone Topology // Crowd Monitor C2", page_icon="🗺️", layout="wide")
inject_c2_theme()
render_c2_sidebar()
render_top_hud(page_title="Zones")
render_stale_data_banner_if_needed()

st.markdown(
    """
    <div style="margin-bottom: 0.8rem;">
        <h2 style="color: #F8FAFC; margin-bottom: 0.2rem; font-size: 1.4rem;">
            ZONE SPATIAL TOPOLOGY & CAPACITY AUDITING
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">
            Real-time geometry, capacity ceilings, and micro-trend inspection per camera polygon.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

zones = get_zones()
zone_states = get_live_zone_states()
is_stale, _, _ = is_telemetry_stale()

# 1. Top Section: 2D Spatial Vector Map (Left) & Comparative Data Grid (Right)
col_map, col_table = st.columns([1.2, 1.4])

with col_map:
    st.markdown(
        """
        <div style="font-size: 0.75rem; text-transform: uppercase; color: #06B6D4; font-weight: 700; margin-bottom: 0.35rem;">
            CAMERA CALIBRATION & POLYGON VECTOR TOPOLOGY
        </div>
        """,
        unsafe_allow_html=True
    )
    fig_map = build_zone_schematic_map(zones, zone_states)
    st.plotly_chart(fig_map, use_container_width=True)

with col_table:
    st.markdown(
        """
        <div style="font-size: 0.75rem; text-transform: uppercase; color: #06B6D4; font-weight: 700; margin-bottom: 0.35rem;">
            COMPARATIVE ZONE METRICS MATRIX
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Construct clean presentation DataFrame
    table_rows = []
    for z in zones:
        z_id = z["zone_id"]
        zs = zone_states.get(z_id, {})
        cnt = round(zs.get("final_count", 0))
        cap = z["capacity"]
        dens = zs.get("density_pm2", 0.0)
        pct = (cnt / cap * 100.0) if cap > 0 else 0.0
        table_rows.append({
            "Zone ID": z_id,
            "Designation": z["name"],
            "Floor Area": f"{z['area_m2']} m²",
            "Safe Cap": cap,
            "Est. Count": f"~{cnt}",
            "Density": f"{dens:.2f} /m²",
            "Util %": f"{pct:.0f}%",
            "Trend": zs.get("trend", "flat").upper(),
            "Engine": zs.get("method", "yolo").upper(),
            "Status": zs.get("status", "normal").upper()
        })
    
    df_zones = pd.DataFrame(table_rows)
    st.dataframe(df_zones, use_container_width=True, hide_index=True)

st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 1rem 0;'>", unsafe_allow_html=True)

# 2. Selected Zone Detailed Inspection
st.markdown(
    """
    <div style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: #06B6D4; font-weight: 700; margin-bottom: 0.5rem;">
        DEEP INSPECTOR // DRILLDOWN TELEMETRY
    </div>
    """,
    unsafe_allow_html=True
)

zone_options = [f"{z['zone_id']} - {z['name']}" for z in zones]
selected_choice = st.selectbox("Select Zone to Inspect", zone_options, index=0)
sel_zone_id = selected_choice.split(" - ")[0]

selected_zone_meta = next((z for z in zones if z["zone_id"] == sel_zone_id), None)
selected_zone_state = zone_states.get(sel_zone_id, {})

if selected_zone_meta:
    # Zone Metrics Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            render_kpi_card_html(
                label=f"{sel_zone_id} HEADCOUNT",
                value=f"~{round(selected_zone_state.get('final_count', 0))}",
                subtext=f"Rated capacity: {selected_zone_meta['capacity']}",
                is_stale=is_stale
            ),
            unsafe_allow_html=True
        )
    with c2:
        dens = selected_zone_state.get("density_pm2", 0.0)
        st.markdown(
            render_kpi_card_html(
                label="MEASURED DENSITY",
                value=f"{dens:.2f} /m²",
                subtext=f"Safe limit: {selected_zone_meta['safe_density_limit']:.1f} /m²",
                status_glow="alert" if dens > selected_zone_meta['safe_density_limit'] else "normal",
                is_stale=is_stale
            ),
            unsafe_allow_html=True
        )
    with c3:
        pct = selected_zone_state.get("pct_capacity", 0.0)
        st.markdown(
            render_kpi_card_html(
                label="CAPACITY OCCUPANCY",
                value=f"{pct:.0f}%",
                subtext=f"Floor space: {selected_zone_meta['area_m2']} m²",
                status_glow="busy" if pct > 70 else "normal",
                is_stale=is_stale
            ),
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            render_kpi_card_html(
                label="ALERT THRESHOLD",
                value=f"{selected_zone_meta['alert_threshold']} pers",
                subtext=f"Cooldown: {selected_zone_meta['cooldown_s']}s",
                is_stale=is_stale
            ),
            unsafe_allow_html=True
        )

    # 15-Minute Historical Rolling Window Chart
    now_utc = datetime.now(timezone.utc)
    fifteen_mins_ago = (now_utc - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    now_str = now_utc.strftime("%Y-%m-%d %H:%M:%S")

    ts_data = get_counts_time_series(
        zone_ids=[sel_zone_id],
        start_utc=fifteen_mins_ago,
        end_utc=now_str,
        downsample=False
    )
    
    col_chart, col_history = st.columns([1.6, 1.0])
    with col_chart:
        fig_ts = build_zone_timeseries_chart(
            data=ts_data,
            metric="avg_count",
            threshold_val=selected_zone_meta["alert_threshold"],
            title=f"Zone {sel_zone_id} Rolling 15-Minute Headcount Profile"
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    with col_history:
        st.markdown(
            f"""
            <div style="font-size: 0.75rem; text-transform: uppercase; color: #06B6D4; font-weight: 700; margin-bottom: 0.4rem;">
                ZONE {sel_zone_id} RECENT ANOMALIES
            </div>
            """,
            unsafe_allow_html=True
        )
        zone_alerts = [a for a in get_all_alerts() if a.get("zone_id") == sel_zone_id][:4]
        if zone_alerts:
            for za in zone_alerts:
                st.markdown(
                    f"""
                    <div class="c2-card" style="padding: 0.6rem 0.8rem; margin-bottom: 0.4rem;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-family: JetBrains Mono; font-size: 0.75rem; color: #38BDF8;">{za['ts'].split('.')[0]}</span>
                            {get_status_badge_html(za['status'])}
                        </div>
                        <div style="font-size: 0.78rem; color: #F8FAFC; margin-top: 0.2rem;">{za['reason']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div class="c2-card" style="text-align: center; padding: 1.5rem; color: #64748B;">
                    No recent anomalies recorded for this zone.
                </div>
                """,
                unsafe_allow_html=True
            )

render_global_footer()
