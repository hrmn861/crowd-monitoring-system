"""
Crowd Monitor — Simulated Live Telemetry Ticker
Simulates the live worker loop by injecting fresh 1-second zone counts, updating zone_state,
and writing worker heartbeats to SQLite (WAL mode).
"""

import time
import sqlite3
import numpy as np
from datetime import datetime, timezone
from pathlib import Path

from app.config import DB_PATH
from app.db import get_zones

def run_ticker(interval_s: float = 1.0):
    print(f"[*] Starting live telemetry ticker. Updating crowd counts every {interval_s}s...")
    zones = get_zones()
    step = 0

    while True:
        now_utc = datetime.now(timezone.utc)
        now_str = now_utc.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        conn = sqlite3.connect(str(DB_PATH), timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        cursor = conn.cursor()

        try:
            for z in zones:
                z_id = z["zone_id"]
                area = z["area_m2"]
                cap = z["capacity"]
                thresh = z["alert_threshold"]

                # Generate dynamic wave
                wave = np.sin((step + int(z_id[-1]) * 10) / 15.0) * 8.0
                base = 38 if z_id == "Z1" else (24 if z_id == "Z2" else (45 if z_id == "Z3" else 14))
                count = max(5.0, round(base + wave + np.random.normal(0, 1.2), 1))
                dens = round(count / area, 2)
                pct = round(count / cap * 100.0, 1)
                trend = "up" if wave > 2 else ("down" if wave < -2 else "flat")
                status = "over_threshold" if count >= thresh else ("busy" if pct >= 70 else "normal")
                method = "dm_count" if count >= 45 else "yolo"

                # Insert into counts
                cursor.execute("""
                    INSERT INTO counts (ts, session_id, video_offset_s, zone_id, yolo_count, dm_count, final_count, density_pm2, method)
                    VALUES (?, 'SESS-LIVE-RUN', ?, ?, ?, ?, ?, ?, ?)
                """, (now_str, float(step), z_id, count if method == 'yolo' else count*0.9, count if method == 'dm_count' else count*1.1, count, dens, method))

                # Update zone_state
                cursor.execute("""
                    INSERT OR REPLACE INTO zone_state (zone_id, ts, final_count, density_pm2, pct_capacity, trend, method, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (z_id, now_str, count, dens, pct, trend, method, status))

            # Update worker heartbeat
            cursor.execute("""
                INSERT INTO worker_heartbeat (ts, models_loaded, last_sample_ts, write_lag_ms, stage_timings, gpu_mem_mb, notes)
                VALUES (?, 'YOLOv8s: True, DM-Count: True', ?, 28.4, '{"grab_ms": 10.5, "yolo_ms": 31.0, "db_ms": 5.2}', 1620.0, 'Live stream active')
            """, (now_str, now_str))

            # Update camera health
            cursor.execute("""
                INSERT INTO camera_health (ts, camera_id, status, last_frame_ts, fps, dropped_frames, width, height, event)
                VALUES (?, 'CAM-01-ENTRANCE-NORTH', 'online', ?, 3.0, 0, 1280, 720, 'Nominal FPS packet')
            """, (now_str, now_str))

            conn.commit()
            step += 1
        except Exception as e:
            print(f"[Ticker Error] {e}")
        finally:
            conn.close()

        time.sleep(interval_s)

if __name__ == "__main__":
    run_ticker()
