"""
Mock Data Generator for Crowd Monitor C2 Ops Dashboard
Populates SQLite (WAL mode) with realistic telemetry, zones, alerts, evaluation metrics,
and health heartbeats so the dashboard is immediately interactive.
"""

import os
import json
import sqlite3
import numpy as np
from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.generate_sample_frame import generate_annotated_frame

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "outputs" / "crowd.db"
SNAPSHOTS_DIR = BASE_DIR / "data" / "outputs" / "snapshots"
LATEST_FRAME_PATH = BASE_DIR / "data" / "outputs" / "latest_annotated.jpg"

def populate_mock_data():
    """Builds realistic operational database state."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate visual frames first
    generate_annotated_frame(str(LATEST_FRAME_PATH), is_alert=False)
    snap_1 = str(SNAPSHOTS_DIR / "alert_1_20261015.jpg")
    snap_2 = str(SNAPSHOTS_DIR / "alert_2_20261015.jpg")
    generate_annotated_frame(snap_1, is_alert=True, frame_title="CAM-01 [Z1 ALERT SNAPSHOT]")
    generate_annotated_frame(snap_2, is_alert=False, frame_title="CAM-01 [Z2 CAUTION SNAPSHOT]")

    # 2. Connect to SQLite
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")

    # Apply Schema & Indexes
    schema_file = BASE_DIR / "sql" / "001_schema.sql"
    index_file = BASE_DIR / "sql" / "002_indexes.sql"
    with open(schema_file, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    with open(index_file, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    cursor = conn.cursor()

    # Clear existing state for a fresh demo run
    conn.execute("PRAGMA foreign_keys=OFF;")
    tables_to_clear = [
        "counts", "zone_state", "escalations", "alerts", "camera_health",
        "worker_heartbeat", "eval_samples", "eval_results", "shadow_log", "audit_log", "zones"
    ]
    for tbl in tables_to_clear:
        cursor.execute(f"DELETE FROM {tbl}")
    conn.execute("PRAGMA foreign_keys=ON;")

    # 3. Seed Zones
    zones_data = [
        ("Z1", "North Gate Security Check", 32.5, 65, 2.0, json.dumps([[50, 320], [420, 310], [430, 690], [40, 700]]), 50, 45, 300),
        ("Z2", "Central Escalator Lobby", 26.0, 45, 1.7, json.dumps([[440, 280], [790, 275], [780, 680], [450, 685]]), 38, 30, 240),
        ("Z3", "Exhibition Hall East Corridor", 45.0, 90, 2.0, json.dumps([[810, 250], [1240, 240], [1250, 670], [800, 675]]), 70, 60, 300),
        ("Z4", "Ticket Validation Concourse", 22.0, 35, 1.6, json.dumps([[380, 100], [860, 95], [840, 260], [400, 265]]), 28, 30, 180)
    ]
    cursor.executemany("""
        INSERT INTO zones (zone_id, name, area_m2, capacity, safe_density_limit, polygon, alert_threshold, persistence_s, cooldown_s)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, zones_data)

    # 4. Generate Counts History (spanning past 3 hours down to this second)
    now_utc = datetime.now(timezone.utc)
    counts_batch = []
    
    # 180 time steps (every minute for 3 hours)
    for i in range(180, -1, -1):
        step_dt = now_utc - timedelta(minutes=i)
        ts_str = step_dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        for z_id, _, area, cap, _, _, thresh, _, _ in zones_data:
            # Simulate natural crowd wave
            hour_factor = np.sin((180 - i) / 30.0) * 12.0
            base_count = 34 if z_id == "Z1" else (22 if z_id == "Z2" else (48 if z_id == "Z3" else 15))
            noise = np.random.normal(0, 2.0)
            
            # Elevate Z1 near the end so an alert is actively triggered right now!
            if z_id == "Z1" and i < 8:
                final_cnt = float(thresh + 3 + (8 - i))
            else:
                final_cnt = max(0.0, float(base_count + hour_factor + noise))

            # Simulate model divergence: YOLO undercounts slightly in dense crowds
            yolo_cnt = final_cnt if final_cnt < 45 else final_cnt * 0.88
            dm_cnt = final_cnt if final_cnt >= 35 else final_cnt * 1.08
            dens = final_cnt / area
            method = "dm_count" if final_cnt >= 45 else "yolo"

            counts_batch.append((
                ts_str, "SESS-LIVE-01", float(180 - i), z_id,
                round(yolo_cnt, 1), round(dm_cnt, 1), round(final_cnt, 1),
                round(dens, 2), method
            ))

    cursor.executemany("""
        INSERT INTO counts (ts, session_id, video_offset_s, zone_id, yolo_count, dm_count, final_count, density_pm2, method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, counts_batch)

    # 5. Populate Zone State (Live Snapshot)
    now_str = now_utc.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    state_rows = [
        ("Z1", now_str, 54.0, 1.66, 83.1, "up", "dm_count", "over_threshold"),
        ("Z2", now_str, 34.0, 1.31, 75.6, "up", "yolo", "busy"),
        ("Z3", now_str, 42.0, 0.93, 46.7, "flat", "yolo", "normal"),
        ("Z4", now_str, 16.0, 0.73, 45.7, "down", "yolo", "normal")
    ]
    cursor.executemany("""
        INSERT INTO zone_state (zone_id, ts, final_count, density_pm2, pct_capacity, trend, method, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, state_rows)

    # 6. Populate Realistic Review Alerts
    t_alert1 = (now_utc - timedelta(minutes=4)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    t_alert2 = (now_utc - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    t_alert3 = (now_utc - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    alert_rows = [
        (t_alert1, None, "Z1", "occupancy", "critical", "Count exceeded threshold 50 for 60s (Sustained Ingress Surge)", 65, 54.0, 1.66, snap_1, "review_requested", None, None, None),
        (t_alert2, None, "Z2", "occupancy", "warning", "Rapid density rise (+18 pers within 180s)", 45, 36.0, 1.38, snap_2, "confirmed", "Jane Doe (Lead Reviewer)", (now_utc - timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"), "Escalator queue verified"),
        (t_alert3, (now_utc - timedelta(hours=1, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"), "Z3", "occupancy", "warning", "Exceeded threshold 70 for 35s", 35, 72.0, 1.60, snap_2, "dismissed", "Alex Mercer (Operator)", (now_utc - timedelta(hours=1, minutes=48)).strftime("%Y-%m-%d %H:%M:%S"), "Temporary exhibit entry surge cleared")
    ]
    cursor.executemany("""
        INSERT INTO alerts (ts, ended_ts, zone_id, kind, level, reason, duration_s, count_at_trigger, density_at_trigger, snapshot_path, status, reviewed_by, reviewed_at, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, alert_rows)

    # 7. Seed Sample Escalation
    esc_summary = {
        "title": "Venue Escalation Summary",
        "site": {
            "name": "Pragati Maidan Expo Center",
            "address": "Mathura Road, Railway Colony, New Delhi, Delhi 110001, India"
        },
        "zone": {"id": "Z2", "name": "Central Escalator Lobby", "area_m2": 26.0},
        "count_estimate": 36,
        "density_pm2": 1.38,
        "trend": "up",
        "alert_reason": "Rapid density rise (+18 pers within 180s)",
        "alert_time_utc": t_alert2,
        "escalated_by": "Jane Doe (Lead Reviewer)",
        "escalated_at_utc": (now_utc - timedelta(minutes=38)).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "note": "Escalator stoppage caused brief congestion; security dispatched to restart unit.",
        "disclaimer": "Counts are model estimates. Control room decides whether to call emergency services (112 in India)."
    }
    cursor.execute("""
        INSERT INTO escalations (alert_id, ts, escalated_by, summary_json, snapshot_path, recipient, delivery_status, attempts, sent_at, note)
        VALUES (2, ?, 'Jane Doe (Lead Reviewer)', ?, ?, 'ops-control@pragatimaidan.example.org', 'sent', 1, ?, 'Delivered via internal C2 webhook')
    """, (t_alert2, json.dumps(esc_summary), snap_2, (now_utc - timedelta(minutes=37)).strftime("%Y-%m-%d %H:%M:%S")))

    # 8. Seed Camera Health & Worker Heartbeat
    cursor.execute("""
        INSERT INTO camera_health (ts, camera_id, status, last_frame_ts, fps, dropped_frames, width, height, event)
        VALUES (?, 'CAM-01-ENTRANCE-NORTH', 'online', ?, 3.0, 4, 1280, 720, 'Nominal RTSP stream synch')
    """, (now_str, now_str))

    cursor.execute("""
        INSERT INTO camera_health (ts, camera_id, status, last_frame_ts, fps, dropped_frames, width, height, event)
        VALUES (?, 'CAM-01-ENTRANCE-NORTH', 'degraded', ?, 1.8, 12, 1280, 720, 'Network packet jitter detected')
    """, ((now_utc - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"), (now_utc - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")))

    cursor.execute("""
        INSERT INTO worker_heartbeat (ts, models_loaded, last_sample_ts, write_lag_ms, stage_timings, gpu_mem_mb, notes)
        VALUES (?, 'YOLOv8s: True, DM-Count: True', ?, 34.2, '{"grab_ms": 11.2, "yolo_ms": 32.4, "dm_ms": 18.0, "db_ms": 6.8}', 1650.0, 'Operational nominal')
    """, (now_str, now_str))

    # 9. Seed Evaluation Results Matrix
    eval_rows = [
        ("RUN-2026-OCT", "yolov8s", "Z1", "light", "day", 150, 1.8, 7.2, -0.4, now_str),
        ("RUN-2026-OCT", "yolov8s", "Z1", "medium", "day", 150, 4.6, 14.1, -2.8, now_str),
        ("RUN-2026-OCT", "yolov8s", "Z1", "heavy", "day", 150, 11.2, 26.5, -9.6, now_str),
        ("RUN-2026-OCT", "dm_count", "Z1", "light", "day", 150, 3.9, 15.6, 1.8, now_str),
        ("RUN-2026-OCT", "dm_count", "Z1", "medium", "day", 150, 3.7, 11.4, -0.9, now_str),
        ("RUN-2026-OCT", "dm_count", "Z1", "heavy", "day", 150, 5.4, 13.8, -2.1, now_str)
    ]
    cursor.executemany("""
        INSERT INTO eval_results (run_id, model, zone_id, density_band, condition, n, mae, mape, bias, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, eval_rows)

    # 10. Seed Shadow Log
    shadow_rows = []
    for s_idx in range(50):
        s_ts = (now_utc - timedelta(hours=s_idx // 5)).strftime("%Y-%m-%d %H:%M:%S")
        is_false = 1 if s_idx % 18 == 0 else 0
        shadow_rows.append((s_idx + 1, s_ts, "Z1" if s_idx % 2 == 0 else "Z2", 1, 1 if not is_false else 0, is_false, 0))
    cursor.executemany("""
        INSERT INTO shadow_log (alert_id, observer_ts, zone_id, human_observer_flag, in_time, false_alert, missed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, shadow_rows)

    # 11. Seed Audit Logs
    audit_rows = [
        ((now_utc - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"), "rev_01", "reviewer", "login", "auth", None, "Session initiated from console IP 10.0.4.12"),
        ((now_utc - timedelta(hours=3, minutes=15)).strftime("%Y-%m-%d %H:%M:%S"), "rev_01", "reviewer", "view_frame", "Home", "latest_annotated.jpg", "Visual camera telemetry verified"),
        ((now_utc - timedelta(hours=1, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"), "ops_02", "operator", "dismiss", "alerts", "3", "Dismissed transient peak"),
        ((now_utc - timedelta(minutes=38)).strftime("%Y-%m-%d %H:%M:%S"), "rev_01", "reviewer", "escalate", "escalation", "2", "Dispatched Incident Summary #1 to control room")
    ]
    cursor.executemany("""
        INSERT INTO audit_log (ts, user_id, role, action, page, target_id, details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, audit_rows)

    conn.commit()
    conn.close()
    print("✓ Operational SQLite database and mock telemetry successfully generated at:", DB_PATH)

if __name__ == "__main__":
    populate_mock_data()
