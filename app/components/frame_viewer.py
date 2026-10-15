"""
Secure Frame Viewer Component with Mandatory RBAC Privacy Enforcement
Gates visual camera frames strictly to authorized 'reviewer' personnel.
Operators and Admins receive an interactive schematic wireframe / privacy locked card.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import streamlit as st
from PIL import Image

from app.auth import is_reviewer, get_current_user
from app.db import log_audit
from app.theme import clean_html

def render_secure_frame_viewer(
    image_path: Optional[str],
    caption: str = "Real-Time Camera Feed",
    zones: Optional[List[Dict[str, Any]]] = None,
    show_controls: bool = True,
    key_suffix: str = "main"
):
    """
    Renders the live or recorded camera frame if the signed-in user has the
    'reviewer' role. Otherwise renders an airtight privacy-locked HUD wireframe.
    """
    user = get_current_user()
    role = user.get("role") if user else "guest"

    if is_reviewer():
        # User is an authorized Safety Reviewer
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                st.image(img, caption=f"SECURE FEED // {caption}", use_container_width=True)
                
                # Audit log frame inspection (throttled in production)
                if f"view_logged_{key_suffix}" not in st.session_state:
                    st.session_state[f"view_logged_{key_suffix}"] = True
                    log_audit(
                        user_id=user["user_id"],
                        role=role,
                        action="view_frame",
                        page="viewer",
                        target_id=Path(image_path).name,
                        details="Inspected secure visual telemetry frame"
                    )
            except Exception as e:
                st.warning(f"Error loading frame: {e}")
        else:
            # Fallback placeholder when no physical frame has been dumped yet
            st.markdown(
                clean_html("""
                <div class="locked-placeholder" style="border-style: solid; border-color: rgba(6, 182, 212, 0.3);">
                    <div style="font-size: 2.2rem; color: #06B6D4;">📡</div>
                    <div style="font-weight: 700; color: #F8FAFC; margin-top: 0.5rem;">AWAITING STREAM SYNC</div>
                    <p style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.25rem;">
                        No annotated frame found in <code>data/outputs/latest_annotated.jpg</code>.<br>
                        Run the mock generator or backend worker to start streaming.
                    </p>
                </div>
                """),
                unsafe_allow_html=True
            )

        if show_controls:
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                st.toggle("Zone Boundaries", value=True, key=f"tgl_poly_{key_suffix}")
            with c2:
                st.toggle("Detections / Centroids", value=True, key=f"tgl_pts_{key_suffix}")
            with c3:
                st.toggle("Density Heatmap", value=False, key=f"tgl_heat_{key_suffix}")

    else:
        # Non-reviewer (Operator / Admin) - Strictly Privacy-Gated
        st.markdown(
            clean_html(f"""
            <div class="locked-placeholder">
                <div class="locked-icon">🔒</div>
                <div style="font-family: JetBrains Mono; font-size: 0.75rem; color: #F59E0B; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;">
                    PRIVACY RESTRICTION ACTIVE
                </div>
                <div style="font-size: 1.05rem; font-weight: 600; color: #F8FAFC; margin-top: 0.35rem;">
                    Visual Camera Frames Gated to Safety Reviewers
                </div>
                <p style="font-size: 0.82rem; color: #94A3B8; max-width: 480px; margin: 0.5rem auto 0 auto; line-height: 1.4;">
                    Under the <i>Crowd Monitor Ethics & Privacy Standard</i>, live video frames and incident snapshots 
                    are visible exclusively to certified <b>Safety Reviewers</b>. 
                    Your account (<code>{role.upper()}</code>) has full access to numerical counts, density metrics, 
                    and zone telemetry charts below.
                </p>
                <div style="margin-top: 1rem;">
                    <span class="c2-badge badge-stale">SCHEMATIC TELEMETRY ACTIVE</span>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )
