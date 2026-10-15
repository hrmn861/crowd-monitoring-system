"""
Tactical C2 KPI Metric Card Component
High-performance obsidian glassmorphic telemetry cards with glowing accents.
"""

from typing import Optional
from app.theme import clean_html

def render_kpi_card_html(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_positive_is_good: bool = True,
    status_glow: Optional[str] = None, # "normal", "busy", "alert", None
    subtext: Optional[str] = None,
    is_stale: bool = False
) -> str:
    """Generates HTML for a high-tech glassmorphic telemetry KPI card."""
    card_classes = ["c2-card", "c2-card-accent"]
    if is_stale:
        card_classes.append("c2-stale")
    if status_glow == "alert":
        card_classes.append("c2-card-alert")

    # Value color & text glow
    if status_glow == "normal":
        val_color = "#10B981"
        val_glow = "text-shadow: 0 0 16px rgba(16, 185, 129, 0.35);"
        pip_color = "#10B981"
    elif status_glow == "alert":
        val_color = "#EF4444"
        val_glow = "text-shadow: 0 0 16px rgba(239, 68, 68, 0.4);"
        pip_color = "#EF4444"
    elif status_glow == "busy":
        val_color = "#F59E0B"
        val_glow = "text-shadow: 0 0 16px rgba(245, 158, 11, 0.35);"
        pip_color = "#F59E0B"
    else:
        val_color = "#F8FAFC"
        val_glow = "text-shadow: 0 0 14px rgba(6, 182, 212, 0.22);"
        pip_color = "#06B6D4"

    delta_html = ""
    if delta:
        delta_color = "#10B981" if delta.startswith("+") and delta_positive_is_good or delta.startswith("-") and not delta_positive_is_good else "#EF4444"
        delta_bg = "rgba(16, 185, 129, 0.12)" if delta_color == "#10B981" else "rgba(239, 68, 68, 0.12)"
        delta_border = "rgba(16, 185, 129, 0.25)" if delta_color == "#10B981" else "rgba(239, 68, 68, 0.25)"
        if delta.startswith("0") or "0%" in delta:
            delta_color = "#94A3B8"
            delta_bg = "rgba(148, 163, 184, 0.1)"
            delta_border = "rgba(148, 163, 184, 0.2)"
        delta_html = f'<span style="font-size: 0.74rem; font-weight: 700; color: {delta_color}; background: {delta_bg}; border: 1px solid {delta_border}; padding: 0.12rem 0.45rem; border-radius: 4px; margin-left: 0.55rem; font-family: JetBrains Mono, monospace;">{delta}</span>'

    subtext_html = f'<div style="font-size: 0.72rem; color: #94A3B8; margin-top: 0.4rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.35rem;">{subtext}</div>' if subtext else ""

    classes_str = " ".join(card_classes)
    return clean_html(
        f'<div class="{classes_str}">'
        f'<div style="display: flex; justify-content: space-between; align-items: center;">'
        f'<div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.09em; color: #06B6D4; font-weight: 700; display: flex; align-items: center; gap: 0.4rem;">'
        f'<span style="width: 6px; height: 6px; border-radius: 50%; background: {pip_color}; box-shadow: 0 0 8px {pip_color}; display: inline-block;"></span>'
        f'<span>{label}</span>'
        f'</div>'
        f'</div>'
        f'<div style="display: flex; align-items: baseline; margin-top: 0.35rem;">'
        f'<span class="telemetry-num" style="font-size: 1.85rem; color: {val_color}; {val_glow}">{value}</span>'
        f'{delta_html}'
        f'</div>'
        f'{subtext_html}'
        f'</div>'
    )
