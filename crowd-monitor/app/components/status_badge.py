"""
Status Badge Component
Renders high-visibility semantic status badges for Tactical C2 Obsidian UI.
"""

def get_status_badge_html(status: str, custom_label: str = "") -> str:
    """Returns HTML for color-coded status badge with status icon."""
    status_lower = (status or "").lower()
    
    if status_lower in ("normal", "online", "confirmed"):
        label = custom_label or ("Online" if "line" in status_lower else "Normal")
        icon = "●"
        css_class = "badge-normal"
    elif status_lower in ("busy", "degraded", "sending"):
        label = custom_label or ("Degraded" if "line" in status_lower else "Busy")
        icon = "▲"
        css_class = "badge-busy"
    elif status_lower in ("over_threshold", "review_requested", "alert", "offline", "failed"):
        label = custom_label or ("Review requested" if "review" in status_lower or "threshold" in status_lower else "Offline")
        icon = "◆"
        css_class = "badge-alert"
    else:
        label = custom_label or "No Data"
        icon = "■"
        css_class = "badge-stale"

    return f'<span class="c2-badge {css_class}"><span>{icon}</span> {label}</span>'
