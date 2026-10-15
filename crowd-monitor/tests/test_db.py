"""
Unit Tests for Database Access and WAL Concurrency
"""

import pytest
import sqlite3
from app.db import (
    get_zones,
    get_live_zone_states,
    get_total_headcount_summary,
    get_open_alerts_count,
    is_telemetry_stale
)

def test_db_read_zones():
    zones = get_zones()
    assert len(zones) >= 4
    zone_ids = [z["zone_id"] for z in zones]
    assert "Z1" in zone_ids
    assert "Z2" in zone_ids

def test_db_zone_states():
    states = get_live_zone_states()
    assert "Z1" in states
    assert states["Z1"]["final_count"] > 0
    assert states["Z1"]["status"] in ("normal", "busy", "over_threshold", "no_data")

def test_headcount_summary():
    summary = get_total_headcount_summary()
    assert summary["total_now"] > 0
    assert summary["max_density"] >= 0.0

def test_telemetry_staleness_logic():
    # Insert a fresh row at now_utc
    from app.db import get_db
    from datetime import datetime, timezone
    now_utc_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    with get_db(read_only=False) as conn:
        conn.execute("""
            INSERT INTO counts (ts, session_id, video_offset_s, zone_id, yolo_count, dm_count, final_count, density_pm2, method)
            VALUES (?, 'TEST-SESS', 0.0, 'Z1', 10.0, 10.0, 10.0, 0.31, 'yolo')
        """, (now_utc_str,))

    # Now it should be fresh (< 10s)
    is_stale, age, latest_ts = is_telemetry_stale()
    assert is_stale is False
    assert age is not None
    assert age < 10.0

