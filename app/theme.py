"""
Tactical C2 Obsidian Theme & Styling Engine for Crowd Monitor
Provides custom CSS injection and Plotly figure styling for a state-of-the-art
Aerospace / Situational Awareness Command & Control Operations Center UI.
"""

import streamlit as st
import plotly.graph_objects as go

# Design System Color Tokens
COLOR_CANVAS_BG = "#070A0F"
COLOR_PANEL_BG = "rgba(17, 24, 39, 0.75)"
COLOR_PANEL_SOLID = "#0F172A"
COLOR_BORDER = "rgba(255, 255, 255, 0.08)"
COLOR_BORDER_HOVER = "rgba(6, 182, 212, 0.35)"

COLOR_CYAN_PRIMARY = "#06B6D4"
COLOR_CYAN_GLOW = "rgba(6, 182, 212, 0.15)"
COLOR_INDIGO_ACCENT = "#6366F1"

# Semantic Status Colors
COLOR_NORMAL_EMERALD = "#10B981"
COLOR_NORMAL_BG = "rgba(16, 185, 129, 0.12)"

COLOR_BUSY_AMBER = "#F59E0B"
COLOR_BUSY_BG = "rgba(245, 158, 11, 0.12)"

COLOR_ALERT_CRIMSON = "#EF4444"
COLOR_ALERT_BG = "rgba(239, 68, 68, 0.15)"

COLOR_STALE_SLATE = "#64748B"
COLOR_STALE_BG = "rgba(100, 116, 139, 0.15)"

TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#94A3B8"
TEXT_MUTED = "#64748B"

FONTS_UI = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONTS_MONO = "'JetBrains Mono', 'Roboto Mono', 'SF Mono', Consolas, monospace"

def clean_html(html_str: str) -> str:
    """Removes all indentation and internal empty lines so Streamlit/CommonMark never renders it as a code block."""
    if not html_str:
        return ""
    return "".join(line.strip() for line in html_str.strip().splitlines() if line.strip())

def inject_c2_theme():
    """Injects high-performance Tactical C2 Obsidian glassmorphism stylesheet."""
    custom_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* Global Root Resets & Canvas */
    .stApp {{
        background: radial-gradient(circle at 50% 0%, #0F172A 0%, {COLOR_CANVAS_BG} 75%);
        color: {TEXT_PRIMARY};
        font-family: {FONTS_UI};
    }}

    /* Top Streamlit Header and Toolbar adjustments */
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}
    
    /* Tactical Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0A0E17 0%, #060910 100%) !important;
        border-right: 1px solid rgba(6, 182, 212, 0.18) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
    }}
    
    /* Hide Default Streamlit Nav Menu Completely */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavSeparator"],
    [data-testid="stSidebarNavLinkContainer"],
    [data-testid="stSidebarNavLink"],
    nav[data-testid="stSidebarNav"],
    div[data-testid="stSidebarNav"],
    ul[data-testid="stSidebarNavItems"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        max-height: 0 !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: none !important;
        opacity: 0 !important;
    }}

    /* Custom Tactical C2 Navigation Links */
    div[data-testid="stSidebarContent"] a[data-testid="stPageLink-NavLink"] {{
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-left: 3px solid transparent !important;
        border-radius: 6px !important;
        padding: 0.55rem 0.85rem !important;
        margin-bottom: 0.35rem !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        color: #E2E8F0 !important;
        font-weight: 500 !important;
        font-size: 0.86rem !important;
        text-decoration: none !important;
    }}

    div[data-testid="stSidebarContent"] a[data-testid="stPageLink-NavLink"]:hover {{
        background: rgba(30, 41, 59, 0.85) !important;
        border-color: rgba(6, 182, 212, 0.35) !important;
        border-left: 3px solid #06B6D4 !important;
        box-shadow: 0 0 16px rgba(6, 182, 212, 0.25) !important;
        transform: translateX(4px) !important;
        color: #38BDF8 !important;
    }}

    /* Active Nav Link Highlight */
    div[data-testid="stSidebarContent"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {{
        background: linear-gradient(90deg, rgba(6, 182, 212, 0.18) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        border: 1px solid rgba(6, 182, 212, 0.35) !important;
        border-left: 3px solid #06B6D4 !important;
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.2), inset 0 0 10px rgba(6, 182, 212, 0.08) !important;
        color: #38BDF8 !important;
        font-weight: 600 !important;
    }}

    /* Category Nav Dividers */
    .nav-section-header {{
        font-size: 0.68rem;
        font-weight: 700;
        color: #06B6D4;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-top: 1.1rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-family: 'JetBrains Mono', monospace;
    }}
    .nav-section-header::after {{
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(6, 182, 212, 0.3), transparent);
    }}

    /* Global Container Padding */
    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 98% !important;
    }}

    /* Glassmorphic Tactical Cards */
    .c2-card {{
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.85) 0%, rgba(10, 15, 26, 0.92) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.85rem;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }}

    .c2-card:hover {{
        border-color: rgba(6, 182, 212, 0.45);
        box-shadow: 0 6px 24px -2px rgba(6, 182, 212, 0.2);
        transform: translateY(-1px);
    }}

    /* Top Laser Accent for Primary Cards */
    .c2-card-accent {{
        border: 1px solid rgba(6, 182, 212, 0.22) !important;
    }}

    .c2-card-accent::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #06B6D4 0%, #6366F1 50%, #38BDF8 100%);
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
    }}

    /* Alert Pulse Card */
    .c2-card-alert {{
        border: 1px solid rgba(239, 68, 68, 0.55) !important;
        background: linear-gradient(180deg, rgba(239, 68, 68, 0.16) 0%, rgba(17, 24, 39, 0.9) 100%) !important;
        animation: pulseAlert 2.5s infinite;
    }}

    @keyframes pulseAlert {{
        0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.35); }}
        70% {{ box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
    }}

    /* Tactical Telemetry Failsafe / Hold State */
    .c2-stale {{
        border: 1px solid rgba(245, 158, 11, 0.45) !important;
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
        box-shadow: inset 0 0 16px rgba(245, 158, 11, 0.08), 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        opacity: 0.95 !important;
        position: relative;
    }}

    .c2-stale::after {{
        content: 'PAUSED / HELD';
        position: absolute;
        top: 6px;
        right: 8px;
        font-family: {FONTS_MONO};
        font-size: 0.58rem;
        font-weight: 700;
        color: #F59E0B;
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 3px;
        padding: 0.1rem 0.35rem;
        letter-spacing: 0.05em;
        z-index: 2;
    }}

    /* Monospace Telemetry Numbers */
    .telemetry-num {{
        font-family: {FONTS_MONO};
        font-weight: 700;
        letter-spacing: -0.03em;
    }}

    /* Badges */
    .c2-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.2rem 0.55rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-family: {FONTS_MONO};
    }}

    .badge-normal {{
        background: {COLOR_NORMAL_BG};
        color: {COLOR_NORMAL_EMERALD};
        border: 1px solid rgba(16, 185, 129, 0.25);
    }}

    .badge-busy {{
        background: {COLOR_BUSY_BG};
        color: {COLOR_BUSY_AMBER};
        border: 1px solid rgba(245, 158, 11, 0.25);
    }}

    .badge-alert {{
        background: {COLOR_ALERT_BG};
        color: {COLOR_ALERT_CRIMSON};
        border: 1px solid rgba(239, 68, 68, 0.35);
        animation: badgeGlow 2s infinite ease-in-out;
    }}

    @keyframes badgeGlow {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}

    .badge-stale {{
        background: {COLOR_STALE_BG};
        color: {COLOR_STALE_SLATE};
        border: 1px solid rgba(100, 116, 139, 0.25);
    }}

    .badge-cyan {{
        background: {COLOR_CYAN_GLOW};
        color: {COLOR_CYAN_PRIMARY};
        border: 1px solid rgba(6, 182, 212, 0.3);
    }}

    /* Linear Capacity Meter Bar */
    .capacity-track {{
        width: 100%;
        height: 6px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 999px;
        overflow: hidden;
        margin-top: 0.45rem;
    }}
    .capacity-fill {{
        height: 100%;
        border-radius: 999px;
        transition: width 0.4s ease;
    }}

    /* Global Stale & Offline Banner */
    .stale-banner {{
        background: linear-gradient(90deg, #7F1D1D 0%, #1E1B4B 100%);
        border: 1px solid #DC2626;
        color: #FEE2E2;
        padding: 0.75rem 1.25rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 500;
        font-size: 0.9rem;
    }}

    /* Locked Telemetry Placeholder */
    .locked-placeholder {{
        background: rgba(15, 23, 42, 0.9);
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        padding: 2.5rem 1.5rem;
        text-align: center;
        color: {TEXT_SECONDARY};
    }}
    .locked-icon {{
        font-size: 2.2rem;
        color: {COLOR_CYAN_PRIMARY};
        margin-bottom: 0.5rem;
    }}

    /* Buttons Override */
    .stButton > button {{
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: {TEXT_PRIMARY} !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        border-color: {COLOR_CYAN_PRIMARY} !important;
        color: {COLOR_CYAN_PRIMARY} !important;
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.25) !important;
    }}

    /* Primary Call to Action Button */
    .btn-action-primary button {{
        background: linear-gradient(135deg, {COLOR_CYAN_PRIMARY} 0%, {COLOR_INDIGO_ACCENT} 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
    }}
    .btn-action-primary button:hover {{
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.4) !important;
    }}

    /* Footer Disclaimer */
    .c2-footer {{
        border-top: 1px solid {COLOR_BORDER};
        padding: 1.25rem 0 0.5rem 0;
        margin-top: 2.5rem;
        font-size: 0.75rem;
        color: {TEXT_MUTED};
        text-align: center;
        line-height: 1.5;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def style_fig(fig: go.Figure, height: int = 320, title: str = "") -> go.Figure:
    """Applies Tactical C2 Obsidian aesthetic to Plotly figures."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else None,
            font=dict(family="Inter", size=14, color=TEXT_PRIMARY),
            x=0.01,
            y=0.96
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(11, 17, 30, 0.5)",
        height=height,
        margin=dict(l=45, r=25, t=40 if title else 25, b=35),
        font=dict(family="JetBrains Mono", size=11, color=TEXT_SECONDARY),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0F172A",
            bordercolor=COLOR_BORDER_HOVER,
            font=dict(family="JetBrains Mono", size=11, color=TEXT_PRIMARY)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            zeroline=False,
            showline=True,
            linecolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(size=10, color=TEXT_MUTED)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            zeroline=False,
            showline=True,
            linecolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(size=10, color=TEXT_MUTED)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=TEXT_SECONDARY),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    return fig
