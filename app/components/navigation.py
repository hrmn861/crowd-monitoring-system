"""
Tactical C2 Obsidian Navigation System (app/components/navigation.py)
Interactive mission-control sidebar navigation with emojis, categorized section headers,
real-time alert counters, and clearance-aware link indicators.
"""

import streamlit as st
from app.auth import get_current_user, is_reviewer, is_admin
from app.db import get_open_alerts_count, get_camera_health, is_telemetry_stale
from app.theme import clean_html

def render_c2_sidebar():
    """Renders the comprehensive Tactical C2 Operations navigation bar in the sidebar."""
    with st.sidebar:
        user = get_current_user()
        role = user.get("role", "operator") if user else "operator"
        open_alerts = get_open_alerts_count()
        health = get_camera_health()
        cam_status = health.get("status", "offline") if health else "offline"
        is_stale, _, _ = is_telemetry_stale()
        is_online = (cam_status == "online" and not is_stale)

        # 1. Mission Control Header Card
        status_color = "#10B981" if is_online else "#EF4444"
        beacon_glow = f"0 0 10px {status_color}"
        st.markdown(
            clean_html(f"""
            <div style="padding: 0.6rem 0.2rem 0.8rem 0.2rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 0.65rem;">
                    <div style="font-size: 1.6rem; filter: drop-shadow(0 0 8px rgba(6, 182, 212, 0.4));">🛡️</div>
                    <div>
                        <div style="font-size: 1.05rem; font-weight: 800; letter-spacing: -0.02em; color: #F8FAFC;">
                            CROWD MONITOR
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #06B6D4; letter-spacing: 0.08em; font-weight: 600;">
                            C2 OPERATIONS DESK
                        </div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 0.65rem; background: rgba(15, 23, 42, 0.7); padding: 0.3rem 0.6rem; border-radius: 4px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; align-items: center; gap: 0.4rem;">
                        <div style="width: 7px; height: 7px; border-radius: 50%; background: {status_color}; box-shadow: {beacon_glow};"></div>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #94A3B8; font-weight: 600;">
                            {'OPTICAL RTSP: NOMINAL' if is_online else 'STREAM: INTERRUPTED'}
                        </span>
                    </div>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #06B6D4; font-weight: 700;">
                        v2.4
                    </span>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        # 2. Section: SITUATIONAL SENSORS
        st.markdown('<div class="nav-section-header"><span>📡</span> SITUATIONAL SENSORS</div>', unsafe_allow_html=True)
        st.page_link("Home.py", label="Situational Overview", icon="🛡️")
        st.page_link("pages/1_Replay.py", label="Incident Replay", icon="⏪")
        st.page_link("pages/2_Zones.py", label="Zone Topology", icon="🗺️")

        # 3. Section: INCIDENT ADJUDICATION
        st.markdown('<div class="nav-section-header"><span>🚨</span> INCIDENT ADJUDICATION</div>', unsafe_allow_html=True)
        alert_label = f"Alert Triage Desk ({open_alerts})" if open_alerts > 0 else "Alert Triage Desk"
        st.page_link("pages/4_Alerts.py", label=alert_label, icon="⚠️" if open_alerts > 0 else "🚨")
        
        # Escalation link
        if is_reviewer():
            st.page_link("pages/5_Escalation.py", label="Escalation Dispatch", icon="📡")
        else:
            st.page_link("pages/5_Escalation.py", label="Escalation Dispatch (Locked)", icon="🔒", disabled=False)

        # 4. Section: ANALYTICS & DIAGNOSTICS
        st.markdown('<div class="nav-section-header"><span>📊</span> ANALYTICS & HEALTH</div>', unsafe_allow_html=True)
        st.page_link("pages/3_Density_and_Trends.py", label="Density & Trends", icon="📈")
        st.page_link("pages/6_Camera_Health.py", label="Hardware & Diagnostics", icon="🖥️")
        st.page_link("pages/7_Evaluation.py", label="Model Accuracy & Bias", icon="⚖️")

        # 5. Section: GOVERNANCE & COMPLIANCE
        st.markdown('<div class="nav-section-header"><span>📜</span> GOVERNANCE & AUDIT</div>', unsafe_allow_html=True)
        st.page_link("pages/8_Methodology_and_Ethics.py", label="Ethics & Methodology", icon="📖")
        
        if is_admin():
            st.page_link("pages/9_Settings.py", label="System Calibration", icon="⚙️")
            st.page_link("pages/10_Audit_Log.py", label="Security Audit Trail", icon="📜")
        else:
            st.page_link("pages/9_Settings.py", label="System Calibration (Admin)", icon="🔒")
            st.page_link("pages/10_Audit_Log.py", label="Audit Trail (Admin)", icon="🔒")

        # 6. Sidebar Personnel Footer Card
        role_badge_col = "#10B981" if role == "reviewer" else ("#06B6D4" if role == "operator" else "#818CF8")
        st.markdown(
            clean_html(f"""
            <div style="margin-top: 1.5rem; padding: 0.75rem; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.68rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">
                        ACTIVE CLEARANCE
                    </span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 700; color: {role_badge_col}; background: rgba(255,255,255,0.06); padding: 0.1rem 0.4rem; border-radius: 3px;">
                        {role.upper()}
                    </span>
                </div>
                <div style="font-size: 0.85rem; font-weight: 600; color: #F8FAFC; margin-top: 0.25rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    {user.get('name', 'Operator')}
                </div>
                <div style="font-size: 0.7rem; color: #64748B; margin-top: 0.15rem;">
                    Terminal IP: 10.0.4.12 &bull; SSL
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )
