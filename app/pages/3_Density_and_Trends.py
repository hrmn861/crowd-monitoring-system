"""
Crowd Monitor — Density & Historical Trend Analytics (3_Density_and_Trends.py)
Deep longitudinal analytics, daily 1-min downsampling, model divergence analysis, and CSV export.
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
from app.components.header import render_top_hud
from app.components.banners import render_global_footer, render_stale_data_banner_if_needed
from app.components.charts import (
    build_zone_timeseries_chart,
    build_model_comparison_chart,
    build_uptime_strip_chart
)
from app.components.kpi_card import render_kpi_card_html
from app.components.navigation import render_c2_sidebar
from app.db import (
    get_zones,
    get_live_zone_states,
    get_counts_time_series,
    get_all_alerts,
    get_camera_health_events,
    is_telemetry_stale
)

st.set_page_config(page_title="Density & Trends // Crowd Monitor C2", page_icon="📈", layout="wide")
inject_c2_theme()
render_c2_sidebar()
render_top_hud(page_title="Trends")
render_stale_data_banner_if_needed()

st.markdown(
    """
    <div style="margin-bottom: 0.8rem;">
        <h2 style="color: #F8FAFC; margin-bottom: 0.2rem; font-size: 1.4rem;">
            DENSITY DYNAMICS & LONGITUDINAL TREND ENGINE
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">
            1-minute downsampled time-series, historical build-up patterns, and sensor model cross-validation.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

zones = get_zones()
zone_states = get_live_zone_states()
is_stale, _, _ = is_telemetry_stale()

# 1. Live Indicator Row (Keep page anchored to live state)
st.markdown(
    """
    <div style="font-size: 0.72rem; text-transform: uppercase; color: #06B6D4; font-weight: 700; margin-bottom: 0.3rem;">
        ACTIVE SENSOR TELEMETRY ANCHOR (REAL-TIME)
    </div>
    """,
    unsafe_allow_html=True
)
if zones:
    z_cols = st.columns(len(zones))
    for idx, z in enumerate(zones):
        z_id = z["zone_id"]
        zs = zone_states.get(z_id, {})
        with z_cols[idx]:
            st.markdown(
                f"""
                <div class="c2-card" style="padding: 0.5rem 0.8rem; margin-bottom: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #94A3B8;">
                        <span style="font-weight: 700; color: #06B6D4;">{z_id}</span>
                        <span>{zs.get('trend', 'flat').upper()}</span>
                    </div>
                    <div style="font-family: JetBrains Mono; font-size: 1.1rem; color: #F8FAFC; margin-top: 0.15rem;">
                        ~{round(zs.get('final_count', 0))} <span style="font-size: 0.75rem; color: #64748B;">({zs.get('density_pm2', 0.0):.2f}/m²)</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# 2. Control Bar
with st.container():
    st.markdown("<div class='c2-card' style='padding: 1rem;'>", unsafe_allow_html=True)
    c_date, c_range, c_zone, c_metric = st.columns([1.2, 1.2, 1.5, 1])
    
    with c_date:
        selected_date = st.date_input("Analysis Date", value=datetime.now(timezone.utc).date())
    
    with c_range:
        time_range = st.selectbox("Temporal Window", ["Today (Full Day)", "Past 1 Hour", "Past 15 Minutes", "Custom Range"])
    
    with c_zone:
        all_z_ids = [z["zone_id"] for z in zones]
        selected_zones = st.multiselect("Active Zones Filter", options=all_z_ids, default=all_z_ids)
    
    with c_metric:
        metric_choice = st.radio("Primary Metric", ["Headcount (~People)", "Density (p/m²)"], horizontal=True)
        metric_col = "avg_count" if "Headcount" in metric_choice else "avg_density"

    c_chk1, c_chk2, c_chk3, c_btn = st.columns([1, 1, 1, 1], vertical_alignment="center")
    with c_chk1:
        show_threshold = st.checkbox("Overlay Alert Threshold", value=True)
    with c_chk2:
        show_alerts = st.checkbox("Overlay Alert Incidents", value=True)
    with c_chk3:
        compare_models = st.checkbox("Show Model Divergence", value=True)
    with c_btn:
        load_data = st.button("⚡ Query Telemetry", type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Determine Time Boundaries
now_utc = datetime.now(timezone.utc)
if time_range == "Past 15 Minutes":
    start_utc = (now_utc - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    end_utc = now_utc.strftime("%Y-%m-%d %H:%M:%S")
    downsample = False
elif time_range == "Past 1 Hour":
    start_utc = (now_utc - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    end_utc = now_utc.strftime("%Y-%m-%d %H:%M:%S")
    downsample = False
else:
    # Full day (1-min downsampled)
    start_utc = f"{selected_date.strftime('%Y-%m-%d')} 00:00:00"
    end_utc = f"{selected_date.strftime('%Y-%m-%d')} 23:59:59"
    downsample = True

# Fetch Time-Series Data
ts_data = get_counts_time_series(
    zone_ids=selected_zones,
    start_utc=start_utc,
    end_utc=end_utc,
    downsample=downsample
)
alerts_list = get_all_alerts() if show_alerts else []

# 3. Peak Summary Cards
if ts_data:
    df_ts = pd.DataFrame(ts_data)
    peak_count = round(df_ts["avg_count"].max()) if not df_ts.empty else 0
    peak_row = df_ts.loc[df_ts["avg_count"].idxmax()] if not df_ts.empty else None
    peak_time = peak_row["bucket_ts"].split(" ")[-1] if peak_row is not None else "--:--"
    peak_zone = peak_row["zone_id"] if peak_row is not None else "Z?"
    peak_dens = df_ts["avg_density"].max() if not df_ts.empty else 0.0

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown(
            render_kpi_card_html("SESSION PEAK CROWD", f"~{peak_count}", subtext=f"Logged at {peak_time} ({peak_zone})"),
            unsafe_allow_html=True
        )
    with p2:
        st.markdown(
            render_kpi_card_html("MAXIMUM DENSITY", f"{peak_dens:.2f} /m²", subtext=f"Peak zone: {peak_zone}"),
            unsafe_allow_html=True
        )
    with p3:
        st.markdown(
            render_kpi_card_html("RECORDED SAMPLES", f"{len(df_ts)} points", subtext="Downsampled 1-min buckets"),
            unsafe_allow_html=True
        )
    with p4:
        st.markdown(
            render_kpi_card_html("ACTIVE ALERT TRIGGERS", f"{len(alerts_list)} events", subtext="Recorded during window"),
            unsafe_allow_html=True
        )

# 4. Primary Longitudinal Chart
st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
fig_ts = build_zone_timeseries_chart(
    data=ts_data,
    metric=metric_col,
    threshold_val=50.0 if show_threshold else None,
    alerts=alerts_list,
    title=f"Multi-Zone Time-Series Profile // {time_range}"
)
st.plotly_chart(fig_ts, use_container_width=True)

# 5. Model Divergence Analysis (YOLO vs DM-Count)
if compare_models and selected_zones:
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    comp_zone = selected_zones[0]
    fig_comp = build_model_comparison_chart(data=ts_data, zone_id=comp_zone)
    st.plotly_chart(fig_comp, use_container_width=True)

# 6. Stream Continuity & Camera Uptime Ribbon
st.markdown(
    """
    <div style="font-size: 0.75rem; text-transform: uppercase; color: #06B6D4; font-weight: 700; margin-top: 1rem; margin-bottom: 0.2rem;">
        STREAM CONTINUITY & CAMERA UPTIME TIMELINE
    </div>
    """,
    unsafe_allow_html=True
)
fig_uptime = build_uptime_strip_chart(get_camera_health_events())
st.plotly_chart(fig_uptime, use_container_width=True)

# 7. Data Export
if ts_data:
    df_export = pd.DataFrame(ts_data)
    csv_bytes = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Telemetry Window (CSV)",
        data=csv_bytes,
        file_name=f"crowd_telemetry_{selected_date}.csv",
        mime="text/csv"
    )

render_global_footer()
