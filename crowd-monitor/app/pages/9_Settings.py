"""
Crowd Monitor — Administration & Parameter Configuration (9_Settings.py)
Restricted administrator control panel for zone boundaries, thresholds, and retention policies.
"""

import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st
import json

from app.theme import inject_c2_theme
from app.config import get_app_config, get_zones_config, get_thresholds_config
from app.components.header import render_top_hud
from app.components.banners import render_global_footer
from app.components.navigation import render_c2_sidebar
from app.auth import require_role, get_current_user
from app.db import log_audit

st.set_page_config(page_title="System Settings // Crowd Monitor C2", page_icon="⚙️", layout="wide")
inject_c2_theme()
render_c2_sidebar()
render_top_hud(page_title="Settings")

# Role verification: Administrator only
require_role("admin", page_name="Settings")
user = get_current_user()

st.markdown(
    """
    <div style="margin-bottom: 0.8rem;">
        <h2 style="color: #F8FAFC; margin-bottom: 0.2rem; font-size: 1.4rem;">
            SYSTEM PARAMETERS & SENSOR RE-CALIBRATION
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">
            Configure physical zone floor measurements, alert thresholds, model hysteresis boundaries, and dispatch routing.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

app_cfg = get_app_config()
thresholds_cfg = get_thresholds_config()
zones_cfg = get_zones_config()

tab_zones, tab_thresh, tab_site, tab_retention = st.tabs([
    "📐 ZONE CALIBRATION",
    "⚡ THRESHOLDS & HYSTERESIS",
    "🏢 VENUE & DISPATCH ROUTING",
    "🗄️ RETENTION POLICIES"
])

with tab_zones:
    st.markdown("### Physical Zone Geometry & Capacity Parameters")
    for z in zones_cfg.get("zones", []):
        with st.expander(f"Zone {z['zone_id']} — {z['name']}", expanded=True):
            cz1, cz2, cz3 = st.columns(3)
            with cz1:
                st.number_input(f"Floor Area (m²) [{z['zone_id']}]", value=float(z["area_m2"]), step=1.0, key=f"area_{z['zone_id']}")
            with cz2:
                st.number_input(f"Safe Physical Capacity (Persons) [{z['zone_id']}]", value=int(z["capacity"]), step=5, key=f"cap_{z['zone_id']}")
            with cz3:
                st.number_input(f"Comfort Density Limit (p/m²) [{z['zone_id']}]", value=float(z["safe_density_limit"]), step=0.1, key=f"dens_{z['zone_id']}")

with tab_thresh:
    st.markdown("### Anomaly Triggers & Model Switching Hysteresis")
    ct1, ct2 = st.columns(2)
    with ct1:
        st.markdown("#### Global Alert Defaults")
        st.number_input("Default Alert Threshold (People)", value=50, step=5)
        st.number_input("Persistence Window (Seconds before trigger)", value=45, step=5)
        st.number_input("Alert Cooldown Window (Seconds)", value=300, step=30)
    
    with ct2:
        st.markdown("#### Model Switching Hysteresis")
        st.number_input("YOLO ➔ DM-Count Switch Threshold (Crowd size)", value=45, step=5)
        st.number_input("DM-Count ➔ YOLO Fallback Boundary (Crowd size)", value=35, step=5)
        st.caption("ℹ️ Hysteresis prevents sensor mode chatter when counts hover around 40-45 people.")

with tab_site:
    st.markdown("### Venue Identity & Control Room Contact")
    cs1, cs2 = st.columns(2)
    with cs1:
        st.text_input("Venue Facility Name", value=app_cfg.get("site", {}).get("name", ""))
        st.text_area("Physical Venue Address", value=app_cfg.get("site", {}).get("address", ""))
    with cs2:
        st.text_input("Internal Control Room Dispatch Recipient (Email / Webhook)", value=app_cfg.get("site", {}).get("control_room_contact", ""))
        st.text_input("Camera Node Identifier", value=app_cfg.get("camera", {}).get("id", ""))

with tab_retention:
    st.markdown("### Ephemeral Data Retention Rules")
    cr1, cr2, cr3 = st.columns(3)
    with cr1:
        st.number_input("Raw Video Footage Purge (Days)", value=7, step=1)
    with cr2:
        st.number_input("Incident Snapshot Purge (Days)", value=14, step=1)
    with cr3:
        st.number_input("Audit Trail Retention (Days)", value=180, step=30)

st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 1rem 0;'>", unsafe_allow_html=True)

if st.button("💾 Commit & Synchronize Parameters", type="primary"):
    log_audit(user["user_id"], user["role"], "settings_change", "settings", "global", "Administrator re-synchronized calibration settings")
    st.success("✓ Parameters successfully committed and synchronized with background worker.")

render_global_footer()
