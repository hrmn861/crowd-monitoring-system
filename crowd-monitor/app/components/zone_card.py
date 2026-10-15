"""
Zone Summary Card Component
Displays live zone density, capacity utilization bar, model mode, and trend dynamics.
"""

from typing import Dict, Any
from app.components.status_badge import get_status_badge_html
from app.theme import clean_html

def render_zone_card_html(zone_data: Dict[str, Any], is_stale: bool = False) -> str:
    """Renders HTML for a single zone status card."""
    zone_id = zone_data.get("zone_id", "Z?")
    name = zone_data.get("name", "Zone")
    count = round(zone_data.get("final_count", 0))
    capacity = zone_data.get("capacity", 50)
    density = zone_data.get("density_pm2", 0.0)
    safe_limit = zone_data.get("safe_density_limit", 2.0)
    pct = min(100.0, max(0.0, (count / capacity * 100.0) if capacity > 0 else 0.0))
    trend = zone_data.get("trend", "flat")
    status = zone_data.get("status", "normal")
    method = zone_data.get("method", "yolo").upper()

    # Trend symbol and color
    if trend == "up":
        trend_sym = "↑ RISING"
        trend_col = "#EF4444" if pct > 75 else "#F59E0B"
    elif trend == "down":
        trend_sym = "↓ EASING"
        trend_col = "#10B981"
    else:
        trend_sym = "→ STEADY"
        trend_col = "#94A3B8"

    # Fill color for capacity bar
    if pct >= 90 or status == "over_threshold":
        fill_col = "linear-gradient(90deg, #F59E0B, #EF4444)"
    elif pct >= 70 or status == "busy":
        fill_col = "linear-gradient(90deg, #10B981, #F59E0B)"
    else:
        fill_col = "linear-gradient(90deg, #06B6D4, #10B981)"

    card_classes = ["c2-card", "c2-card-accent"]
    if is_stale:
        card_classes.append("c2-stale")
    if status in ("over_threshold", "review_requested"):
        card_classes.append("c2-card-alert")
    classes_str = " ".join(card_classes)

    badge_html = get_status_badge_html(status)

    return clean_html(
        f'<div class="{classes_str}" style="margin-bottom: 0.75rem;">'
        f'<div style="display: flex; justify-content: space-between; align-items: flex-start;">'
        f'<div style="display: flex; align-items: center; gap: 0.45rem;">'
        f'<span style="font-family: JetBrains Mono, monospace; font-size: 0.72rem; color: #38BDF8; font-weight: 800; background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.35); padding: 0.12rem 0.45rem; border-radius: 4px;">{zone_id}</span>'
        f'<span style="font-size: 0.92rem; font-weight: 700; color: #F8FAFC;">{name}</span>'
        f'</div>'
        f'<div>{badge_html}</div>'
        f'</div>'
        f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-top: 0.8rem; background: rgba(15, 23, 42, 0.45); padding: 0.5rem 0.65rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.04);">'
        f'<div><div style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Estimated Count</div>'
        f'<div class="telemetry-num" style="font-size: 1.4rem; color: #F8FAFC; margin-top: 0.1rem;">~{count} <span style="font-size: 0.75rem; color: #64748B; font-weight: 400;">/ {capacity} cap</span></div></div>'
        f'<div><div style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Density</div>'
        f'<div class="telemetry-num" style="font-size: 1.4rem; color: #38BDF8; text-shadow: 0 0 12px rgba(56, 189, 248, 0.35); margin-top: 0.1rem;">{density:.2f} <span style="font-size: 0.75rem; color: #64748B; font-weight: 400;">/m²</span></div></div>'
        f'</div>'
        f'<div style="margin-top: 0.8rem;">'
        f'<div style="display: flex; justify-content: space-between; font-size: 0.7rem; font-family: JetBrains Mono, monospace; color: #94A3B8; margin-bottom: 0.3rem;">'
        f'<span>OCCUPANCY: <b style="color: #F8FAFC;">{pct:.0f}%</b></span><span style="color: {trend_col}; font-weight: 700;">{trend_sym}</span>'
        f'</div>'
        f'<div class="capacity-track" style="height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden;"><div class="capacity-fill" style="width: {pct}%; height: 100%; background: {fill_col}; box-shadow: 0 0 10px rgba(6, 182, 212, 0.4); border-radius: 3px;"></div></div>'
        f'</div>'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.7rem; font-size: 0.7rem; color: #94A3B8; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.4rem;">'
        f'<span>Safe Limit: <b style="color: #E2E8F0;">{safe_limit:.1f}/m²</b></span>'
        f'<span style="font-family: JetBrains Mono, monospace; font-size: 0.65rem; font-weight: 700; color: #818CF8; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); padding: 0.1rem 0.4rem; border-radius: 4px;">ENGINE: {method}</span>'
        f'</div>'
        f'</div>'
    )
