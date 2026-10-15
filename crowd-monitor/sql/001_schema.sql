-- Crowd Monitor Database Schema (001_schema.sql)
-- SQLite WAL Mode Contract between Backend Worker and Frontend Dashboard

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS zones (
    zone_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    area_m2 REAL NOT NULL,
    capacity INTEGER NOT NULL,
    safe_density_limit REAL NOT NULL,
    polygon TEXT NOT NULL, -- JSON array of points [[x, y], ...]
    alert_threshold INTEGER NOT NULL,
    persistence_s INTEGER NOT NULL,
    cooldown_s INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    mode TEXT NOT NULL CHECK(mode IN ('simulated_live', 'live', 'offline_batch')),
    started_at TEXT NOT NULL,
    ended_at TEXT
);

CREATE TABLE IF NOT EXISTS counts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL, -- UTC YYYY-MM-DD HH:MM:SS.SSS
    session_id TEXT,
    video_offset_s REAL,
    zone_id TEXT NOT NULL REFERENCES zones(zone_id),
    yolo_count REAL,
    dm_count REAL,
    final_count REAL NOT NULL,
    density_pm2 REAL NOT NULL,
    method TEXT NOT NULL CHECK(method IN ('yolo', 'dm_count', 'ensemble'))
);

CREATE TABLE IF NOT EXISTS zone_state (
    zone_id TEXT PRIMARY KEY REFERENCES zones(zone_id),
    ts TEXT NOT NULL,
    final_count REAL NOT NULL,
    density_pm2 REAL NOT NULL,
    pct_capacity REAL NOT NULL,
    trend TEXT CHECK(trend IN ('up', 'down', 'flat')),
    method TEXT NOT NULL,
    status TEXT CHECK(status IN ('normal', 'busy', 'over_threshold', 'no_data'))
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    ended_ts TEXT,
    zone_id TEXT REFERENCES zones(zone_id),
    kind TEXT NOT NULL CHECK(kind IN ('occupancy', 'health')),
    level TEXT NOT NULL DEFAULT 'warning', -- advisory, warning, critical
    reason TEXT NOT NULL,
    duration_s INTEGER DEFAULT 0,
    count_at_trigger REAL,
    density_at_trigger REAL,
    snapshot_path TEXT,
    status TEXT NOT NULL DEFAULT 'review_requested' CHECK(status IN ('review_requested', 'confirmed', 'dismissed', 'escalated')),
    reviewed_by TEXT,
    reviewed_at TEXT,
    note TEXT
);

CREATE TABLE IF NOT EXISTS escalations (
    esc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER REFERENCES alerts(alert_id),
    ts TEXT NOT NULL,
    escalated_by TEXT NOT NULL,
    summary_json TEXT NOT NULL,
    snapshot_path TEXT,
    recipient TEXT NOT NULL,
    delivery_status TEXT NOT NULL DEFAULT 'requested' CHECK(delivery_status IN ('requested', 'sending', 'sent', 'failed')),
    attempts INTEGER DEFAULT 0,
    last_error TEXT,
    sent_at TEXT,
    note TEXT
);

CREATE TABLE IF NOT EXISTS camera_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    camera_id TEXT NOT NULL,
    status TEXT CHECK(status IN ('online', 'degraded', 'offline')),
    last_frame_ts TEXT,
    fps REAL,
    dropped_frames INTEGER DEFAULT 0,
    width INTEGER,
    height INTEGER,
    event TEXT
);

CREATE TABLE IF NOT EXISTS worker_heartbeat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    models_loaded TEXT,
    last_sample_ts TEXT,
    write_lag_ms REAL,
    stage_timings TEXT, -- JSON breakdown: grab, yolo, dm, db, render
    gpu_mem_mb REAL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS config_version (
    id INTEGER PRIMARY KEY CHECK(id = 1),
    version INTEGER NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eval_samples (
    frame_id TEXT,
    zone_id TEXT REFERENCES zones(zone_id),
    true_count REAL NOT NULL,
    true_count_2 REAL, -- second annotator for agreement check
    yolo_count REAL,
    dm_count REAL,
    density_band TEXT NOT NULL CHECK(density_band IN ('light', 'medium', 'heavy')),
    condition TEXT NOT NULL, -- day, night, glare, dense
    split TEXT NOT NULL CHECK(split IN ('train', 'test')),
    PRIMARY KEY (frame_id, zone_id)
);

CREATE TABLE IF NOT EXISTS eval_results (
    run_id TEXT,
    model TEXT NOT NULL,
    zone_id TEXT,
    density_band TEXT,
    condition TEXT,
    n INTEGER NOT NULL,
    mae REAL NOT NULL,
    mape REAL NOT NULL,
    bias REAL NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shadow_log (
    alert_id INTEGER,
    observer_ts TEXT NOT NULL,
    zone_id TEXT REFERENCES zones(zone_id),
    human_observer_flag INTEGER NOT NULL, -- 1 if human observer flagged concern
    in_time INTEGER NOT NULL DEFAULT 0,
    false_alert INTEGER NOT NULL DEFAULT 0,
    missed INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('reviewer', 'operator', 'admin')),
    active INTEGER DEFAULT 1,
    last_login TEXT,
    password_hash TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    action TEXT NOT NULL, -- login, logout, view_frame, confirm, dismiss, escalate, settings_change, access_denied
    page TEXT NOT NULL,
    target_id TEXT,
    details TEXT
);
