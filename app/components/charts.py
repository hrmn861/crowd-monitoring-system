"""
Plotly Chart Builders for Tactical C2 Obsidian Dashboard
Constructs high-contrast time-series, model comparisons, uptime strips, and polygon maps.
"""

from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import pandas as pd
from app.theme import (
    style_fig,
    COLOR_CYAN_PRIMARY,
    COLOR_INDIGO_ACCENT,
    COLOR_NORMAL_EMERALD,
    COLOR_BUSY_AMBER,
    COLOR_ALERT_CRIMSON,
    COLOR_STALE_SLATE
)

ZONE_PALETTE = {
    "Z1": "#06B6D4", # Cyan
    "Z2": "#8B5CF6", # Violet
    "Z3": "#10B981", # Emerald
    "Z4": "#F59E0B"  # Amber
}

def build_zone_timeseries_chart(
    data: List[Dict[str, Any]],
    metric: str = "avg_count", # avg_count or avg_density
    threshold_val: Optional[float] = None,
    alerts: Optional[List[Dict[str, Any]]] = None,
    title: str = "Zone Occupancy Telemetry (1-Min Downsampled)"
) -> go.Figure:
    """Builds multi-zone time-series curve with threshold lines and alert markers."""
    fig = go.Figure()
    
    if not data:
        fig.add_annotation(
            text="No telemetry data recorded in this time window",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color="#64748B")
        )
        return style_fig(fig, title=title)

    df = pd.DataFrame(data)
    df["bucket_ts"] = pd.to_datetime(df["bucket_ts"])
    
    zones = df["zone_id"].unique()
    for z_id in sorted(zones):
        z_df = df[df["zone_id"] == z_id].sort_values("bucket_ts")
        color = ZONE_PALETTE.get(z_id, COLOR_CYAN_PRIMARY)
        fig.add_trace(go.Scatter(
            x=z_df["bucket_ts"],
            y=z_df[metric],
            mode="lines",
            name=f"Zone {z_id}",
            line=dict(color=color, width=2.2),
            connectgaps=False, # Enforce gap on offline periods
            hovertemplate=f"<b>Zone {z_id}</b>: %{{y:.1f}}<extra></extra>"
        ))

    # Add alert threshold reference line if specified
    if threshold_val is not None:
        fig.add_hline(
            y=threshold_val,
            line=dict(color=COLOR_ALERT_CRIMSON, width=1.5, dash="dash"),
            annotation_text=f"Trigger Threshold ({threshold_val})",
            annotation_position="top right",
            annotation_font=dict(color=COLOR_ALERT_CRIMSON, size=10)
        )

    # Add Alert markers as vertical ticks
    if alerts:
        for a in alerts:
            alert_ts = pd.to_datetime(a["ts"])
            fig.add_vline(
                x=alert_ts,
                line=dict(color="rgba(239, 68, 68, 0.4)", width=1, dash="dot")
            )

    y_label = "Headcount (~People)" if metric == "avg_count" else "Density (people/m²)"
    fig.update_layout(yaxis_title=y_label)
    return style_fig(fig, height=340, title=title)

def build_model_comparison_chart(data: List[Dict[str, Any]], zone_id: str) -> go.Figure:
    """Renders YOLO vs DM-Count side-by-side comparison for a selected zone."""
    fig = go.Figure()
    if not data:
        return style_fig(fig, title=f"Model Comparison: Zone {zone_id}")

    df = pd.DataFrame(data)
    df = df[df["zone_id"] == zone_id].sort_values("bucket_ts")
    df["bucket_ts"] = pd.to_datetime(df["bucket_ts"])

    # YOLO curve
    fig.add_trace(go.Scatter(
        x=df["bucket_ts"],
        y=df["avg_yolo"],
        mode="lines",
        name="YOLOv8s (Detection)",
        line=dict(color=COLOR_CYAN_PRIMARY, width=2),
        hovertemplate="YOLO: %{y:.1f}<extra></extra>"
    ))

    # DM-Count curve
    fig.add_trace(go.Scatter(
        x=df["bucket_ts"],
        y=df["avg_dm"],
        mode="lines",
        name="DM-Count (Density Map)",
        line=dict(color=COLOR_INDIGO_ACCENT, width=2, dash="dash"),
        hovertemplate="DM-Count: %{y:.1f}<extra></extra>"
    ))

    # Threshold switch marker
    fig.add_hline(
        y=45,
        line=dict(color="#F59E0B", width=1, dash="dot"),
        annotation_text="Hysteresis Switch Threshold (~45)",
        annotation_position="top left",
        annotation_font=dict(size=9, color="#F59E0B")
    )

    fig.update_layout(yaxis_title="Estimated Count")
    return style_fig(fig, height=300, title=f"Sensor Model Divergence (YOLO vs. DM-Count) — Zone {zone_id}")

def build_density_band_error_chart(eval_data: List[Dict[str, Any]]) -> go.Figure:
    """Grouped bar chart showing MAE and MAPE by density band."""
    fig = go.Figure()
    if not eval_data:
        return style_fig(fig, title="Model Accuracy Metrics")

    df = pd.DataFrame(eval_data)
    models = df["model"].unique()
    bands = ["light", "medium", "heavy"]

    for model_name in models:
        m_df = df[df["model"] == model_name]
        band_maes = [m_df[m_df["density_band"] == b]["mae"].mean() if not m_df[m_df["density_band"] == b].empty else 0 for b in bands]
        color = COLOR_CYAN_PRIMARY if "yolo" in model_name.lower() else COLOR_INDIGO_ACCENT
        
        fig.add_trace(go.Bar(
            x=[b.capitalize() for b in bands],
            y=band_maes,
            name=f"{model_name.upper()} (MAE)",
            marker_color=color,
            opacity=0.85
        ))

    fig.update_layout(
        barmode="group",
        yaxis_title="Mean Absolute Error (People)",
        xaxis_title="Crowd Density Band"
    )
    return style_fig(fig, height=280, title="Stratified Error by Crowd Density Band")

def build_uptime_strip_chart(health_events: List[Dict[str, Any]]) -> go.Figure:
    """Builds a continuous timeline strip of camera health throughout the day."""
    fig = go.Figure()
    
    # Simple simulated 24-hour visual strip
    times = pd.date_range(end=pd.Timestamp.now(tz="UTC"), periods=24, freq="h")
    # All nominal except brief outage
    statuses = ["Online"] * 24
    statuses[14] = "Degraded"
    statuses[15] = "Offline"
    
    color_map = {"Online": COLOR_NORMAL_EMERALD, "Degraded": COLOR_BUSY_AMBER, "Offline": COLOR_ALERT_CRIMSON}
    colors = [color_map[s] for s in statuses]

    fig.add_trace(go.Bar(
        x=times,
        y=[1] * 24,
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0.5)", width=1)),
        showlegend=False,
        hovertemplate="Time: %{x|%H:%M}<br>Status: %{text}<extra></extra>",
        text=statuses
    ))

    fig.update_layout(
        yaxis=dict(visible=False, showticklabels=False),
        xaxis=dict(title=None, tickformat="%H:%M"),
        margin=dict(l=10, r=10, t=10, b=25)
    )
    return style_fig(fig, height=90, title="")

def build_zone_schematic_map(zones: List[Dict[str, Any]], zone_states: Dict[str, Any]) -> go.Figure:
    """Builds a 2D Tactical Vector schematic of zone polygons with dynamic occupancy fills."""
    fig = go.Figure()
    
    for z in zones:
        z_id = z.get("zone_id", "Z?")
        name = z.get("name", "Zone")
        poly = z.get("polygon", [])
        state = zone_states.get(z_id, {})
        status = state.get("status", "normal")
        count = round(state.get("final_count", 0))
        density = state.get("density_pm2", 0.0)

        if not poly or len(poly) < 3:
            continue

        # Close polygon loop
        xs = [pt[0] for pt in poly] + [poly[0][0]]
        ys = [pt[1] for pt in poly] + [poly[0][1]]
        # Invert y for camera coordinate space
        ys_inv = [720 - y for y in ys]

        if status == "over_threshold":
            fillcolor = "rgba(239, 68, 68, 0.35)"
            linecolor = COLOR_ALERT_CRIMSON
        elif status == "busy":
            fillcolor = "rgba(245, 158, 11, 0.3)"
            linecolor = COLOR_BUSY_AMBER
        else:
            fillcolor = "rgba(6, 182, 212, 0.2)"
            linecolor = COLOR_CYAN_PRIMARY

        fig.add_trace(go.Scatter(
            x=xs,
            y=ys_inv,
            fill="toself",
            fillcolor=fillcolor,
            line=dict(color=linecolor, width=2.5),
            name=f"{z_id}: {name}",
            text=f"<b>{z_id} - {name}</b><br>Count: ~{count}<br>Density: {density:.2f}/m²<br>Status: {status.upper()}",
            hoverinfo="text",
            mode="lines"
        ))

        # Centroid for label
        cx = sum(pt[0] for pt in poly) / len(poly)
        cy_inv = 720 - (sum(pt[1] for pt in poly) / len(poly))
        fig.add_annotation(
            x=cx, y=cy_inv,
            text=f"<b>{z_id}</b><br>~{count}",
            showarrow=False,
            font=dict(family="JetBrains Mono", size=12, color="#FFFFFF"),
            bgcolor="rgba(15, 23, 42, 0.8)",
            bordercolor=linecolor,
            borderwidth=1
        )

    fig.update_layout(
        xaxis=dict(range=[0, 1280], visible=False, showgrid=False),
        yaxis=dict(range=[0, 720], visible=False, showgrid=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=5, r=5, t=10, b=10),
        showlegend=False
    )
    return style_fig(fig, height=350, title="Tactical Zone Vector Schematic (1280x720)")
