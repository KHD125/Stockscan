"""
Multibagger Discovery System — Quantum Elite UI Components
=========================================================
State-of-the-art Glassmorphism design system.
Fused Inter & Outfit typography with Aurora gradients.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from config import COLORS, TIER_COLORS, CONVICTION_TIERS, UI


def inject_css():
    """Inject the Quantum Elite Design System."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@300;700;900&display=swap');

    /* ── Core Reset ── */
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-color: #050505;
        color: #E2E8F0;
    }}

    h1, h2, h3, .hero-title, .sb-brand-title {{
        font-family: 'Outfit', sans-serif !important;
    }}

    /* ── Glassmorphism Utility ── */
    .glass-card {{
        background: rgba(23, 23, 23, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }}

    /* ── Hero Banner (Elite Aurora) ── */
    .hero-banner {{
        text-align: center; padding: 3.5rem 2rem;
        background: radial-gradient(circle at 0% 0%, rgba(228,179,65,0.15) 0%, transparent 40%),
                    radial-gradient(circle at 100% 100%, rgba(139,92,246,0.15) 0%, transparent 40%),
                    linear-gradient(135deg, #0A0A0A 0%, #171717 100%);
        border: 1px solid rgba(255,215,0,0.2);
        border-radius: 24px; margin-bottom: 2rem;
        position: relative; overflow: hidden;
    }}
    .hero-banner::after {{
        content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
        animation: shine 8s infinite;
    }}
    @keyframes shine {{ 0% {{ left: -100%; }} 20% {{ left: 100%; }} 100% {{ left: 100%; }} }}

    .hero-icon {{ font-size: 4rem; margin-bottom: 1rem; filter: drop-shadow(0 0 20px rgba(228,179,65,0.4)); }}
    .hero-title {{
        font-size: 3.5rem; font-weight: 900; letter-spacing: -1px; line-height: 1;
        background: linear-gradient(to right, #FFFFFF 0%, #94A3B8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }}
    .hero-sub {{
        font-size: 1rem; color: #94A3B8; letter-spacing: 4px; text-transform: uppercase;
        font-weight: 600; margin-bottom: 1.5rem;
    }}

    /* ── Metric Cockpit ── */
    .m-strip {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 2rem; }}
    .m-chip {{
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px; padding: 20px 10px; text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .m-chip:hover {{ 
        background: rgba(255,255,255,0.06); 
        border-color: rgba(255,255,255,0.2);
        transform: translateY(-4px) scale(1.02);
    }}
    .m-val {{ font-family: 'Outfit'; font-size: 2rem; font-weight: 800; line-height: 1; margin-bottom: 6px; }}
    .m-lbl {{ font-size: 0.7rem; color: #64748B; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }}
    
    .m-gold {{ border-bottom: 4px solid {COLORS['gold']}; }}
    .m-green {{ border-bottom: 4px solid {COLORS['green']}; }}
    .m-blue {{ border-bottom: 4px solid {COLORS['blue']}; }}
    .m-purple {{ border-bottom: 4px solid {COLORS['purple']}; }}

    /* ── Stock Cards (Glass-Evolution) ── */
    .stock-card {{
        background: rgba(30, 30, 30, 0.4);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 18px; padding: 24px; margin-bottom: 12px;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        position: relative; overflow: hidden;
    }}
    .stock-card:hover {{
        background: rgba(40, 40, 40, 0.6);
        border-color: rgba(255,255,255,0.15);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        transform: translateX(8px);
    }}
    .stock-card::before {{
        content: ''; position: absolute; left: 0; top: 0; height: 100%; width: 4px;
        background: var(--card-accent);
    }}

    /* ── Custom Sidebar ── */
    section[data-testid="stSidebar"] {{
        background-color: #0A0A0A !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }}
    .sb-brand {{
        padding: 30px 20px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 20px;
    }}
    .sb-brand-title {{
        font-size: 1.4rem; font-weight: 900; 
        background: linear-gradient(120deg, #FFFFFF, #64748B);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}

    /* ── Progress Bars ── */
    div[data-testid="stProgress"] > div > div > div > div {{
        background-image: linear-gradient(90deg, {COLORS['blue']}, {COLORS['green']});
        border-radius: 10px;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: transparent;
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 12px 24px;
        border: 1px solid rgba(255,255,255,0.05);
        font-weight: 600;
        transition: all 0.3s;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: rgba(255,215,0,0.1) !important;
        border-color: rgba(255,215,0,0.3) !important;
        color: {COLORS['gold']} !important;
    }}

    /* ── Pills ── */
    .pill {{
        padding: 4px 12px; border-radius: 20px; font-size: 0.65rem; font-weight: 800;
        text-transform: uppercase; letter-spacing: 0.5px; border: 1px solid transparent;
    }}
    .pill-tsunami {{ background: rgba(139,92,246,0.15); border-color: rgba(139,92,246,0.4); color: #C084FC; }}
    .pill-alpha {{ background: rgba(228,179,65,0.15); border-color: rgba(228,179,65,0.4); color: {COLORS['gold']}; }}
    </style>
    """, unsafe_allow_html=True)


def render_hero_banner(total_stocks: int, gate_passed: int, tier1_count: int):
    """Render the Quantum Elite hero banner."""
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-icon">💎</div>
        <h1 class="hero-title">SYSTEMATIC ARCHITECT</h1>
        <p class="hero-sub">The Quantamental Discovery Workstation</p>
        <div style="display:flex; justify-content:center; gap:10px;">
            <span class="pill pill-alpha">v{UI['version']}</span>
            <span class="pill pill-alpha" style="background:rgba(255,255,255,0.05); border-color:rgba(255,255,255,0.1); color:#94A3B8;">
                {total_stocks} STOCKS AUDITED
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_strip(metrics: list):
    """Render a cockpit-style metric strip."""
    chips = ""
    for val, label, cls in metrics:
        chips += f'<div class="m-chip {cls}"><div class="m-val">{val}</div><div class="m-lbl">{label}</div></div>'
    st.markdown(f'<div class="m-strip">{chips}</div>', unsafe_allow_html=True)


def render_stock_card(row: pd.Series, show_scores: bool = True):
    """Render an Elite stock card with glassmorphism."""
    tier = int(row.get("conviction_tier", 5))
    tc = TIER_COLORS.get(tier, TIER_COLORS[5])
    accent = tc['text']

    pills = ""
    if row.get("tsunami_signal", 0) == 1:
        pills += '<span class="pill pill-tsunami">🌊 TSUNAMI SIGNAL</span>'
    if row.get("promoter_buying", 0) == 1:
        pills += '<span class="pill pill-alpha">PROMOTER BUYING</span>'
    
    card_html = f"""
    <div class="stock-card" style="--card-accent: {accent};">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-family:'Outfit'; font-weight:800; font-size:1.4rem; color:#FFF;">
                    #{int(row.get('rank', 0))} · {row.get('name', 'N/A')}
                </div>
                <div style="font-size:0.8rem; color:#64748B; margin-top:4px; font-weight:500;">
                    {row.get('sector', '')} | {row.get('industry', '')} | ₹{row.get('market_cap', 0):,.0f} Cr
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'Outfit'; font-size:2.4rem; font-weight:900; color:{accent}; line-height:1;">
                    {row.get('composite_score', 0):.0f}
                </div>
                <div style="font-size:0.65rem; color:#64748B; font-weight:800; letter-spacing:1px;">SCORE</div>
            </div>
        </div>
        <div style="margin-top:16px; display:flex; gap:8px;">{pills}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_tier_summary(df: pd.DataFrame):
    """Render premium tier cards."""
    cols = st.columns(len(CONVICTION_TIERS))
    for col, tier_cfg in zip(cols, CONVICTION_TIERS):
        tier_num = tier_cfg["tier"]
        count = (df["conviction_tier"] == tier_num).sum()
        tc = TIER_COLORS[tier_num]
        
        with col:
            st.markdown(f"""
            <div class="m-chip" style="border-bottom: 4px solid {tc['text']}; min-height:120px;">
                <div style="font-size:1.5rem; margin-bottom:8px;">{tier_cfg['emoji']}</div>
                <div class="m-val" style="color:{tc['text']};">{count}</div>
                <div class="m-lbl">{tier_cfg['label']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_sidebar_brand():
    """Render the elite sidebar brand."""
    st.markdown(f"""
    <div class="sb-brand">
        <div style="font-size:2.5rem; margin-bottom:10px;">🛡️</div>
        <div class="sb-brand-title">SYSTEMATIC<br>ARCHITECT</div>
        <div style="font-size:0.6rem; color:#64748B; letter-spacing:2px; font-weight:800; margin-top:10px;">
            ALPHA DISCOVERY ENGINE
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_radar_chart(row: pd.Series, title: str = "Quality Spectrum") -> go.Figure:
    """Create a high-contrast radar chart."""
    categories = ['Moat', 'Growth', 'Cash', 'Margin', 'Balance Sheet']
    values = [
        row.get("moat_score", 0),
        row.get("growth_score", 0),
        row.get("cash_score", 0),
        row.get("margin_score", 0),
        row.get("balance_sheet_score", 0),
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(255, 215, 0, 0.05)',
        line=dict(color=COLORS['gold'], width=2),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.1)', showticklabels=False),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(size=10, color='#94A3B8'))
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=30, l=30, r=30),
        height=300
    )
    return fig
