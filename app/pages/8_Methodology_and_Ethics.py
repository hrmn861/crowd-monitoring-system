"""
Crowd Monitor — Methodology, Ethics & Safety Governance (8_Methodology_and_Ethics.py)
Transparent declaration of system methodology, computer vision architecture, privacy safeguards,
and operational limitations.
"""
import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

from app.theme import inject_c2_theme
from app.components.header import render_top_hud
from app.components.banners import render_global_footer
from app.components.navigation import render_c2_sidebar

st.set_page_config(page_title="Methodology & Ethics // Crowd Monitor C2", page_icon="📖", layout="wide")
inject_c2_theme()
render_c2_sidebar()
render_top_hud(page_title="Methodology")

st.markdown(
    """
    <div style="margin-bottom: 1rem;">
        <h2 style="color: #F8FAFC; margin-bottom: 0.2rem; font-size: 1.4rem;">
            SYSTEM METHODOLOGY, ETHICS & SAFETY ARCHITECTURE
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">
            Foundational decision-support principles, mathematical formulations, privacy guarantees, and documented limitations.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛡️ SAFETY & ESCALATION PROTOCOL",
    "👁️ VISION PIPELINE & MODELS",
    "🔒 PRIVACY & RETENTION SCHEDULE",
    "⚠️ KNOWN TECHNICAL LIMITATIONS",
    "📐 MATHEMATICAL METRICS"
])

with tab1:
    st.markdown(
        """
        ### Safety Procedure: Review, Then Escalate
        Direct transmission of automated alerts to civil emergency services was strictly rejected during system architecture design:
        1. **Model Uncertainty:** Computer vision models inevitably undercount, overcount, or misinterpret non-human objects and complex shadows. Automated emergency reports waste critical civic responder resources.
        2. **Context Blindness:** A crowded zone does not inherently signify a stampede or hazard. Only trained human reviewers possessing contextual familiarity can determine if flow is orderly or dangerous.
        3. **Strict Human Gate:** Every automated trigger is categorized as `"Review requested"`—never an emergency. The system functions solely as an attentional decision-support tool.
        4. **Jurisdiction Boundary:** Escalation packages are addressed solely to the **venue's internal operations control room**. The control room retains sole authority to contact external emergency authorities (112 in India).
        """
    )

with tab2:
    st.markdown(
        """
        ### Dual-Model Hybrid Vision Architecture
        Crowd counting switches between two complementary deep learning paradigms using a hysteresis loop:
        
        - **Ultralytics YOLOv8s (Object Detection):**
          - Deployed for lightly filled zones ($< 45$ people).
          - Detects individual bounding boxes. A person is counted in a zone if the bottom-center of their bounding box (approximate floor footing) lies inside the polygon:
            $$\\text{pointInPolygon}( (\\frac{x_1 + x_2}{2}, y_2), \\text{Polygon}_z ) \\ge 0$$
        
        - **DM-Count / CSRNet (Density Map Regression):**
          - Engaged when crowds exceed the 45-person threshold or severe overlapping occlusion occurs.
          - Regresses a continuous density map over the full frame. Counts per zone are integrated by masking:
            $$\\text{Count}_z = \\iint_{\\text{Polygon}_z} D(x, y) \\, dx \\, dy$$
        
        - **Hysteresis Switching to Prevent Chatter:**
          - Switch from YOLO to DM-Count when zone count $\\ge 45$.
          - Switch back to YOLO only when DM-Count drops and remains below $35$.
        """
    )

with tab3:
    st.markdown(
        """
        ### Privacy Safeguards & Data Lifecycle
        - **Zero Biometric Extraction:** No face detection, facial recognition, or demographic profiling is implemented.
        - **Data Minimization:** By default, only aggregate numbers, timestamps, and zone states are permanently persisted.
        - **Ephemeral Storage & Retention Limits:**
          - Raw video footage is purged automatically after **7 days**.
          - Incident review snapshots are purged after **14 days**.
          - High-frequency count telemetry is downsampled to 1-minute averages after **3 days** and purged after **90 days**.
          - User audit trails are archived after **180 days**.
        - **Optical Privacy Masking:** Reviewers have the option to enable real-time Gaussian face-blurring on any saved incident frame.
        """
    )

with tab4:
    st.markdown(
        """
        ### Documented Engineering Failure Modes
        The Crowd Monitor system is bounded by physical and optical constraints:
        - **Foreground Occlusion:** In dense crowds viewed from low angles, individuals behind tall persons are physically obscured from camera line-of-sight. Counts degrade proportionally to density.
        - **Optical Glare & Night Lighting:** Low lux conditions and heavy glare reduce contrast, producing elevated false-negative detection rates.
        - **Perspective Distortion:** People distant from the lens occupy fewer pixels; distant people require higher resolution or optical zoom to prevent undercounting.
        - **Single Viewpoint Constraint:** A single camera cannot monitor blind spots behind architectural pillars or around hallway bends.
        """
    )

with tab5:
    st.markdown(
        """
        ### Accuracy Formulations
        - **Mean Absolute Error (MAE):**
          $$\\text{MAE} = \\frac{1}{N} \\sum_{i=1}^N | \\hat{y}_i - y_i |$$
        - **Mean Absolute Percentage Error (MAPE):**
          $$\\text{MAPE} = \\frac{1}{N} \\sum_{i=1}^N \\frac{| \\hat{y}_i - y_i |}{y_i} \\times 100\\%$$
        - **Model Bias (Directional Skew):**
          $$\\text{Bias} = \\frac{1}{N} \\sum_{i=1}^N (\\hat{y}_i - y_i)$$
          *(Negative bias indicates systemic undercounting under high occlusion).*
        """
    )

render_global_footer()
