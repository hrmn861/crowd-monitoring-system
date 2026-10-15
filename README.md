# 🛡️ Crowd Monitor — C2 Operations Center Dashboard

**Crowd Monitor** is an industry-grade, decision-support command-and-control (C2) operations dashboard for real-time crowd counting, zone occupancy analysis, and human-in-the-loop review.

---

## 🚀 Key Architectural Features

- **Tactical C2 Obsidian Glassmorphism:** Deep space obsidian background (`#070A0F`), frosted midnight slate panels (`rgba(17, 24, 39, 0.75)` with `backdrop-filter: blur(12px)`), laser accent borders, and monospaced telemetry figures.
- **Strict Human-in-the-Loop Safety:** Every alert is classified as `"Review requested"`—never `"Emergency"`. Automation never directly contacts external emergency dispatch. Reviewers must confirm visual feeds before dispatching official `"Escalation summaries"` exclusively to the venue's internal control room.
- **Role-Based Privacy & Image Lockdown:** Visual camera frames and incident snapshots are strictly gated in code to authorized `reviewer` personnel. Operators and Administrators view locked telemetry schematics and numeric counts, upholding zero-face-storage privacy protocols.
- **High-Concurrency SQLite WAL Integration:** Background workers write continuously (`busy_timeout=5000`, `journal_mode=WAL`) while the dashboard performs non-blocking indexed queries and 1-minute downsampled aggregations.
- **Stale Telemetry Fail-Safe:** If camera packets or heartbeats lapse for $> 10\text{s}$, the dashboard disables normal/green states, renders an outage caution banner, and locks metrics into failsafe mode.

---

## 📁 Project Layout

```
crowd-monitor/
├── app/
│   ├── Home.py                      # Primary Situational Overview Command Center
│   ├── config.py                    # Constants, Paths & Refreshes
│   ├── theme.py                     # Tactical C2 Obsidian CSS & Plotly Styler
│   ├── db.py                        # SQLite WAL Engine & Downsampling Queries
│   ├── auth.py                      # Session State & RBAC Privacy Gate
│   ├── components/                  # Reusable Glassmorphic Components
│   │   ├── header.py                # Global HUD Banner & Telemetry Ticker
│   │   ├── banners.py               # Stale Data Guard & Ethical Disclaimers
│   │   ├── kpi_card.py              # Telemetry Metric Cards with Deltas
│   │   ├── zone_card.py             # Capacity Utilizers & Directional Trends
│   │   ├── frame_viewer.py          # Secure Frame Viewer with RBAC Gating
│   │   ├── status_badge.py          # Semantic Visual Status Badges
│   │   └── charts.py                # Plotly Time-Series & 2D Vector Schematic
│   └── pages/
│       ├── 1_Replay.py              # Timeline Scrubber & Model Overlay Switcher
│       ├── 2_Zones.py               # Spatial Topology & Zone Inspector
│       ├── 3_Density_and_Trends.py  # Downsampled Longitudinal Trend Engine
│       ├── 4_Alerts.py              # Incident Anomaly Triage Desk
│       ├── 5_Escalation.py          # Review-Then-Escalate Manifest Builder
│       ├── 6_Camera_Health.py       # Optical Stream Diagnostics & Heartbeats
│       ├── 7_Evaluation.py          # MAE/MAPE/Bias Matrices & Shadow Mode
│       ├── 8_Methodology_and_Ethics.py # Privacy Lifecycle & CV Formulations
│       ├── 9_Settings.py            # Admin Threshold & Hysteresis Calibration
│       └── 10_Audit_Log.py          # Immutable Audit Trail
├── config/                          # Declarative System Configurations
│   ├── app.json
│   ├── zones.json
│   └── thresholds.json
├── data/outputs/                    # SQLite WAL Database & Rendered Frames
│   ├── crowd.db
│   ├── latest_annotated.jpg
│   └── snapshots/
├── sql/                             # DDL Schema & Query Indexes
│   ├── 001_schema.sql
│   └── 002_indexes.sql
├── src/
│   ├── generate_sample_frame.py     # Atomic JPEG Renderer with HUD Watermarks
│   ├── mock_data.py                 # Telemetry & History Populator
│   └── live_ticker.py               # Simulated 1Hz Background Worker
└── tests/                           # Pytest Test Suite
    ├── test_zones.py
    ├── test_alerts.py
    └── test_db.py
```

---

## ⚡ Quickstart Commands

### 1. Re-seed Mock Operational State
```bash
python -m src.mock_data
```

### 2. Launch the Tactical C2 Dashboard
```bash
streamlit run app/Home.py
```

### 3. (Optional) Run Live Telemetry Ticker in Background
```bash
python -m src.live_ticker
```

### 4. Execute Unit Tests
```bash
python -m pytest
```

---

## 🔒 Personnel Clearance Roles

| Role | Permissions & Capabilities |
| :--- | :--- |
| **`reviewer`** *(Default)* | Full optical camera inspection, snapshot viewing, alert confirmation, incident dismissal, and control room escalation. |
| **`operator`** | Real-time counts, density metrics, tactical polygon schematic wireframes, trends, alert register (visual camera frames locked). |
| **`admin`** | Zone geometric calibration, threshold tuning, hysteresis configuration, and immutable security audit log access. |

*(Use the operator profile dropdown in the top right HUD to seamlessly toggle roles and test the RBAC privacy guards).*
