"""
Application Configuration Loader for Crowd Monitor C2 Ops Dashboard
Loads configuration, defines database and output paths, and establishes project constants.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

# Root Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = DATA_DIR / "outputs"
SNAPSHOTS_DIR = OUTPUTS_DIR / "snapshots"
DB_PATH = OUTPUTS_DIR / "crowd.db"
LATEST_FRAME_PATH = OUTPUTS_DIR / "latest_annotated.jpg"

# Refresh Intervals (in seconds)
REFRESH_OVERVIEW_S = 3
REFRESH_ZONES_S = 3
REFRESH_ALERTS_S = 5
REFRESH_HEALTH_S = 3
REFRESH_ESCALATION_S = 5
STALE_DATA_THRESHOLD_S = 10.0

# Mandatory Footer Disclaimer
GLOBAL_FOOTER_DISCLAIMER = (
    "Counts are model estimates and can be wrong, especially in dense crowds. "
    "Alerts are requests for a person to check the live feed. "
    "This tool supports staff and does not replace safety procedures."
)

SAFETY_JURISDICTION_NOTE = (
    "Control room decides whether to call the emergency services (112 in India)."
)

def _load_json_or_fallback(filename: str, fallback_dict: Dict[str, Any]) -> Dict[str, Any]:
    file_path = CONFIG_DIR / filename
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Config] Error loading {filename}: {e}. Using defaults.")
    return fallback_dict

def get_app_config() -> Dict[str, Any]:
    return _load_json_or_fallback("app.json", {
        "site": {
            "name": "Pragati Maidan Expo Center",
            "address": "Mathura Road, New Delhi, India",
            "control_room_contact": "control-room@pragatimaidan.example.org"
        },
        "camera": {
            "id": "CAM-01-ENTRANCE-NORTH",
            "name": "North Gate Atrium Overview",
            "mode": "simulated_live"
        }
    })

def get_zones_config() -> Dict[str, Any]:
    return _load_json_or_fallback("zones.json", {"zones": []})

def get_thresholds_config() -> Dict[str, Any]:
    return _load_json_or_fallback("thresholds.json", {
        "defaults": {
            "alert_threshold": 50,
            "persistence_s": 60,
            "cooldown_s": 300
        }
    })
