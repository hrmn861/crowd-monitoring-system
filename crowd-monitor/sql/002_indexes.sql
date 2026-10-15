-- Crowd Monitor Database Indexes (002_indexes.sql)

CREATE INDEX IF NOT EXISTS idx_counts_zone_ts ON counts(zone_id, ts);
CREATE INDEX IF NOT EXISTS idx_counts_ts ON counts(ts);
CREATE INDEX IF NOT EXISTS idx_counts_session ON counts(session_id, video_offset_s);
CREATE INDEX IF NOT EXISTS idx_alerts_ts ON alerts(ts);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_zone ON alerts(zone_id);
CREATE INDEX IF NOT EXISTS idx_health_ts ON camera_health(ts);
CREATE INDEX IF NOT EXISTS idx_heartbeat_ts ON worker_heartbeat(ts);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(ts);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_esc_status ON escalations(delivery_status);
CREATE INDEX IF NOT EXISTS idx_eval_results_run ON eval_results(run_id);
