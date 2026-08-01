# ============================================================
# Coffee Powder Packing Readiness Dashboard
# "Roastery Control Room" — Industrial HMI Edition (v2 — fixed)
#
# Features:
# - Moisture monitoring
# - TCS3200 color analysis
# - DHT22 temperature & humidity
# - Quality decision
# - Recovery recommendation
# - CSV batch logging
# - Instrument-panel UI: animated readiness gauge, live LED,
#   status tiles, styled history table, Plotly trend charts
#
# Arduino Format:
#
# moisture,r,g,b,temp,humidity,status
#
# Example:
# 500,409,582,474,34.4,35.7,PASS
#
# ============================================================

import streamlit as st
import pandas as pd
import os
import sys
import time
import math
import re
from datetime import datetime

import plotly.graph_objects as go

# Add project root path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(PROJECT_ROOT)

from backend.serial_reader import read_from_arduino

from backend.logic import (
    classify_moisture,
    classify_color,
    combine_status,
    calculate_readiness_score,
    generate_recommendation,
    calculate_confidence,
    parse_arduino_line
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Coffee Quality Analyzer",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# GLOBAL CONFIG
# ============================================================

CSV_FILE = "readings.csv"
DEFAULT_PORT = "COM3"
REFRESH_INTERVAL = 5

# ------------------------------------------------------------
# DESIGN TOKENS — "Roastery Control Room"
# ------------------------------------------------------------
BG_DEEP        = "#0F0C0A"
BG_PANEL       = "#1B1512"
BG_PANEL_RAISE = "#241D18"
BORDER         = "#3A2F27"
COPPER         = "#C97C3D"
GOLD           = "#E8B366"
TEAL           = "#5FB8A8"
PASS_C         = "#4CAF7D"
WARN_C         = "#E8A93D"
HOLD_C         = "#E5533D"
TEXT_HI        = "#F3EAE0"
TEXT_MID       = "#B8A99B"
TEXT_LOW       = "#7A6D62"

STATUS_META = {
    "PASS": {"color": PASS_C, "icon": "●", "label": "Quality Accepted"},
    "WARN": {"color": WARN_C, "icon": "▲", "label": "Attention Required"},
    "HOLD": {"color": HOLD_C, "icon": "■", "label": "Quality Hold"},
}

# ============================================================
# HTML SAFETY HELPER
# ------------------------------------------------------------
# Streamlit's markdown renderer follows CommonMark: any line
# indented 4+ spaces gets treated as a *code block* instead of
# raw HTML. Multi-line f-strings that mirror Python's own
# indentation trigger this, which is why sections of the UI
# were showing raw <div> text instead of rendering. Every
# dynamic HTML string is passed through this before it reaches
# st.markdown so indentation can never break rendering again.
# ============================================================

def html(markup: str) -> str:
    collapsed = re.sub(r"\s+", " ", markup.strip())
    collapsed = re.sub(r">\s+<", "><", collapsed)
    return collapsed


def render_html(markup: str):
    st.markdown(html(markup), unsafe_allow_html=True)

# ============================================================
# CSV STRUCTURE
# ============================================================

CSV_COLUMNS = [
    "timestamp", "batch_id", "time_min",
    "moisture_raw", "red", "green", "blue",
    "temperature", "humidity",
    "moisture_status", "color_status", "final_status",
    "readiness_score", "confidence",
    "issue", "recommendation"
]

# ============================================================
# INITIAL CSV CREATION
# ============================================================

def create_csv_if_missing():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv(CSV_FILE, index=False)

# ============================================================
# SAVE SENSOR READING
# ============================================================

def save_reading(data):
    create_csv_if_missing()
    df = pd.DataFrame([data])
    df.to_csv(CSV_FILE, mode="a", header=False, index=False)

# ============================================================
# QUALITY ANALYSIS ENGINE
# ============================================================

def analyze_quality(moisture, r, g, b, temperature, humidity):
    moisture_result = classify_moisture(moisture)
    color_result = classify_color(r, g, b)
    final_status = combine_status(moisture_result, color_result)
    score = calculate_readiness_score(moisture_result, color_result)
    confidence = calculate_confidence(moisture_result, color_result)
    recommendation = generate_recommendation(
        moisture_result, color_result, temperature, humidity
    )
    return {
        "moisture_status": moisture_result,
        "color_status": color_result,
        "final_status": final_status,
        "score": score,
        "confidence": confidence,
        "issue": recommendation["issue"],
        "recommendation": recommendation["recommendation"]
    }

# ============================================================
# ARDUINO DATA READER
# ============================================================

def get_live_data(port):
    try:
        raw = read_from_arduino(port)
        parsed = parse_arduino_line(raw)
        if parsed:
            return parsed
        return None
    except Exception as e:
        st.error(f"Arduino connection error: {e}")
        return None

# ============================================================
# SESSION STATE
# ============================================================

if "live_data" not in st.session_state:
    st.session_state.live_data = None

if "running" not in st.session_state:
    st.session_state.running = False

create_csv_if_missing()

# ============================================================
# GLOBAL STYLE INJECTION
# ============================================================

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {{
    --bg-deep: {BG_DEEP};
    --bg-panel: {BG_PANEL};
    --bg-raised: {BG_PANEL_RAISE};
    --border: {BORDER};
    --copper: {COPPER};
    --gold: {GOLD};
    --teal: {TEAL};
    --pass: {PASS_C};
    --warn: {WARN_C};
    --hold: {HOLD_C};
    --text-hi: {TEXT_HI};
    --text-mid: {TEXT_MID};
    --text-low: {TEXT_LOW};
}}

@media (prefers-reduced-motion: reduce) {{
    * {{ animation: none !important; transition: none !important; }}
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background:
        radial-gradient(circle at 15% 0%, rgba(201,124,61,0.06), transparent 40%),
        radial-gradient(circle at 85% 10%, rgba(232,179,102,0.05), transparent 45%),
        var(--bg-deep);
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 42px 42px;
    z-index: 0;
}}

#MainMenu, footer, header {{ visibility: hidden; }}

/* ---------- SIDEBAR — CONSOLE PANEL ---------- */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, var(--bg-panel), var(--bg-deep));
    border-right: 1px solid var(--border);
}}
[data-testid="stSidebar"] .block-container {{ padding-top: 1.6rem; }}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{
    color: var(--text-mid) !important;
    font-family: 'Inter', sans-serif;
}}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-hi) !important;
    letter-spacing: 0.02em;
}}
[data-testid="stSidebar"] .stTextInput input {{
    background: var(--bg-raised);
    border: 1px solid var(--border);
    color: var(--gold);
    font-family: 'JetBrains Mono', monospace;
    border-radius: 6px;
}}
[data-testid="stSidebar"] hr {{ border-color: var(--border); }}

.console-chip {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-low);
    border-left: 2px solid var(--copper);
    padding-left: 8px;
    margin: 0.4rem 0 0.6rem 0;
}}

/* ---------- HEADER STRIP ---------- */
.machine-strip {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 18px;
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-low);
    font-size: 0.78rem;
    margin-bottom: 14px;
    animation: fadeSlide 0.6s ease both;
}}
.led {{
    width: 9px; height: 9px; border-radius: 50%;
    display: inline-block; margin-right: 8px;
    background: var(--text-low);
}}
.led.on {{
    background: var(--pass);
    box-shadow: 0 0 8px var(--pass), 0 0 2px var(--pass);
    animation: pulse 1.6s ease-in-out infinite;
}}
.led.off {{ background: var(--hold); }}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.35; }}
}}

/* ---------- HERO BANNER ---------- */
.hero-banner {{
    position: relative;
    overflow: hidden;
    padding: 34px 38px;
    border-radius: 16px;
    background: linear-gradient(120deg, #24160C 0%, #3B2413 55%, #5A3419 100%);
    border: 1px solid #4a3320;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    animation: fadeSlide 0.7s ease both;
}}
.hero-banner::after {{
    content: "";
    position: absolute; top: -40%; right: -10%;
    width: 340px; height: 340px; border-radius: 50%;
    background: radial-gradient(circle, rgba(232,179,102,0.18), transparent 70%);
}}
.hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.15rem;
    color: var(--text-hi);
    margin: 0;
    letter-spacing: -0.01em;
}}
.hero-sub {{
    font-family: 'Inter', sans-serif;
    color: #D9C6B4;
    margin-top: 6px;
    font-size: 0.95rem;
}}
.hero-tag {{
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    color: var(--gold);
    border: 1px solid rgba(232,179,102,0.4);
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 14px;
}}

@keyframes fadeSlide {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ---------- SECTION LABEL ---------- */
.section-label {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.05rem;
    color: var(--text-hi);
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 14px 0;
}}
.section-label .bar {{
    width: 4px; height: 18px; border-radius: 2px;
    background: linear-gradient(180deg, var(--copper), var(--gold));
}}

/* ---------- GAUGE ---------- */
.gauge-wrap {{
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
}}
.gauge-center {{ position: absolute; text-align: center; }}
.gauge-number {{
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 2.5rem;
    color: var(--text-hi);
    line-height: 1;
}}
.gauge-label {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    color: var(--text-low);
    margin-top: 4px;
}}
.gauge-svg circle.value-arc {{ transition: stroke-dasharray 1.1s cubic-bezier(0.22, 1, 0.36, 1); }}

/* ---------- STATUS DIAL CARDS ---------- */
.dial-card {{
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    height: 100%;
    animation: fadeSlide 0.8s ease both;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}}
.dial-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 22px rgba(0,0,0,0.35); }}
.dial-eyebrow {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-low);
    margin-bottom: 10px;
}}
.dial-value {{
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 1.9rem;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.status-dot {{
    width: 13px; height: 13px; border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 10px currentColor;
}}

/* ---------- INSTRUMENT TILES ---------- */
.tile-row {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
}}
.tile {{
    position: relative;
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 16px 14px 16px;
    overflow: hidden;
    animation: fadeSlide 0.8s ease both;
    transition: transform 0.25s ease, border-color 0.25s ease;
}}
.tile:hover {{ transform: translateY(-3px); border-color: var(--copper); }}
.tile-accent {{ position: absolute; top: 0; left: 0; right: 0; height: 3px; }}
.tile-icon {{ font-size: 1.1rem; opacity: 0.85; }}
.tile-label {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-low);
    margin: 8px 0 4px 0;
}}
.tile-value {{
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-size: 1.5rem;
    color: var(--text-hi);
}}
.tile-unit {{ font-size: 0.85rem; color: var(--text-mid); margin-left: 3px; }}

/* ---------- ALERT / RECOMMENDATION PANELS ---------- */
.info-panel {{
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-left: 3px solid var(--copper);
    border-radius: 10px;
    padding: 18px 20px;
    height: 100%;
    animation: fadeSlide 0.8s ease both;
}}
.info-panel.good {{ border-left-color: var(--pass); }}
.info-panel-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-low);
    margin-bottom: 8px;
}}
.info-panel-body {{
    font-family: 'Inter', sans-serif;
    color: var(--text-hi);
    font-size: 1rem;
    line-height: 1.5;
}}

/* ---------- BREAKDOWN CARDS ---------- */
.mini-card {{
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 18px;
    text-align: center;
    animation: fadeSlide 0.8s ease both;
}}
.mini-label {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-low);
    margin-bottom: 8px;
}}
.mini-badge {{
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 1.05rem;
    padding: 5px 16px;
    border-radius: 20px;
}}

/* ---------- SWATCH ---------- */
.swatch-ring {{
    width: 70px; height: 70px; border-radius: 50%;
    border: 3px solid var(--border);
    box-shadow: inset 0 0 20px rgba(0,0,0,0.4);
}}

/* ---------- FOOTER NAMEPLATE ---------- */
.nameplate {{
    text-align: center;
    padding: 22px;
    margin-top: 10px;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--bg-panel);
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-low);
    font-size: 0.78rem;
    letter-spacing: 0.05em;
}}
.nameplate b {{ color: var(--gold); }}

/* ---------- RE-THEME NATIVE STREAMLIT ALERT BOXES ---------- */
[data-testid="stAlert"] {{
    background: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
    border-left: 3px solid var(--copper) !important;
    border-radius: 10px !important;
    color: var(--text-hi) !important;
}}
[data-testid="stAlert"] p {{ color: var(--text-hi) !important; }}
[data-testid="stAlert"] svg {{ fill: var(--gold) !important; }}

[data-testid="stDataFrame"] {{
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
}}

hr {{ border-color: var(--border) !important; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SMALL HELPERS FOR CUSTOM COMPONENTS
# ============================================================

def status_meta(status):
    return STATUS_META.get(status, {"color": TEXT_LOW, "icon": "○", "label": status})


def render_gauge(score, color, size=210):
    r = 80
    circumference = 2 * math.pi * r
    arc_fraction = 270 / 360
    track_len = circumference * arc_fraction
    value_len = circumference * arc_fraction * (max(0, min(100, score)) / 100)
    markup = f"""
    <div class="gauge-wrap">
      <svg class="gauge-svg" viewBox="0 0 200 200" width="{size}" height="{size}">
        <circle cx="100" cy="100" r="{r}" fill="none" stroke="{BG_PANEL_RAISE}"
          stroke-width="14" stroke-linecap="round"
          stroke-dasharray="{track_len:.2f} {circumference:.2f}"
          transform="rotate(135 100 100)"></circle>
        <circle class="value-arc" cx="100" cy="100" r="{r}" fill="none" stroke="{color}"
          stroke-width="14" stroke-linecap="round"
          stroke-dasharray="{value_len:.2f} {circumference:.2f}"
          transform="rotate(135 100 100)"
          style="filter:drop-shadow(0 0 7px {color})"></circle>
      </svg>
      <div class="gauge-center">
        <div class="gauge-number">{score}</div>
        <div class="gauge-label">READINESS</div>
      </div>
    </div>
    """
    return html(markup)


def render_tile(icon, label, value, unit, accent):
    markup = f"""
    <div class="tile">
      <div class="tile-accent" style="background:{accent}"></div>
      <div class="tile-icon">{icon}</div>
      <div class="tile-label">{label}</div>
      <div class="tile-value">{value}<span class="tile-unit">{unit}</span></div>
    </div>
    """
    return html(markup)


def render_mini(label, value, color):
    markup = f"""
    <div class="mini-card">
      <div class="mini-label">{label}</div>
      <div class="mini-badge" style="background:{color}22; color:{color}; border:1px solid {color}55;">{value}</div>
    </div>
    """
    return html(markup)

# ============================================================
# SIDEBAR — CONSOLE
# ============================================================

with st.sidebar:
    render_html("""
        <div style="text-align:center; margin-bottom:6px;">
            <div style="font-size:2rem;">☕</div>
            <h2 style="margin:4px 0 0 0;">Coffee AI Analyzer</h2>
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:#7A6D62;">
                CONTROL CONSOLE
            </div>
        </div>
    """)

    st.divider()

    render_html('<div class="console-chip">Device Settings</div>')
    port = st.text_input("Arduino Port", value=DEFAULT_PORT, label_visibility="visible")

    st.divider()

    render_html('<div class="console-chip">Live Monitoring</div>')
    live_mode = st.toggle("Enable Live Mode", value=False)
    st.caption("Dashboard automatically receives Arduino sensor readings.")

    st.divider()

    render_html('<div class="console-chip">Batch Information</div>')
    batch_id = st.text_input("Batch ID", value="COFFEE-001")

    st.divider()
    st.caption("Arduino UNO · TCS3200 · Moisture · DHT22")

# ============================================================
# MACHINE HEADER STRIP
# ============================================================

led_class = "on" if live_mode else "off"
mode_text = "LIVE FEED" if live_mode else "DEMO / STANDBY"

render_html(f"""
    <div class="machine-strip">
        <div><span class="led {led_class}"></span>{mode_text}</div>
        <div>PORT: {port}</div>
        <div>BATCH: {batch_id}</div>
        <div>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
    </div>
""")

# ============================================================
# DASHBOARD HERO
# ============================================================

render_html("""
    <div class="hero-banner">
        <h1 class="hero-title">☕ Coffee Powder Packing Readiness Analyzer</h1>
        <p class="hero-sub">Multi-Sensor Quality Inspection System — Moisture · Color · Climate</p>
        <span class="hero-tag">INDUSTRY 4.0 · REAL-TIME QC</span>
    </div>
""")

st.write("")

# ============================================================
# LIVE DATA ACQUISITION
# ============================================================

if live_mode:
    with st.spinner("Reading sensors..."):
        sensor_data = get_live_data(port)
        if sensor_data:
            st.session_state.live_data = sensor_data

# ============================================================
# DEMO DATA
# ============================================================

if st.session_state.live_data is None:
    demo = st.checkbox("🧪 Demo Factory Sample", value=True)
    if demo:
        st.session_state.live_data = {
            "moisture": 500,
            "red": 409,
            "green": 582,
            "blue": 474,
            "temperature": 34.2,
            "humidity": 60.5,
            "arduino_status": "PASS"
        }

# ============================================================
# PROCESS CURRENT DATA
# ============================================================

data = st.session_state.live_data
result = None

if data:
    result = analyze_quality(
        data["moisture"], data["red"], data["green"], data["blue"],
        data["temperature"], data["humidity"]
    )
    final_status = result["final_status"]
    score = result["score"]
    confidence = result["confidence"]

    meta = status_meta(final_status)

    # --------------------------------------------------------
    # HERO ROW — GAUGE + DIAL CARDS  (signature element)
    # --------------------------------------------------------
    render_html('<div class="section-label"><span class="bar"></span>Current Quality Decision</div>')

    g1, g2, g3 = st.columns([1.1, 1, 1])

    with g1:
        render_html(render_gauge(score, meta["color"]))

    with g2:
        render_html(f"""
            <div class="dial-card">
                <div class="dial-eyebrow">Final Status</div>
                <div class="dial-value">
                    <span class="status-dot" style="background:{meta['color']}; color:{meta['color']};"></span>
                    <span style="color:{meta['color']};">{final_status}</span>
                </div>
                <div style="margin-top:10px; color:var(--text-mid); font-size:0.85rem;">{meta['label']}</div>
            </div>
        """)

    with g3:
        render_html(f"""
            <div class="dial-card">
                <div class="dial-eyebrow">AI Confidence</div>
                <div class="dial-value" style="color:var(--gold);">{confidence}%</div>
                <div style="margin-top:10px; color:var(--text-mid); font-size:0.85rem;">Model certainty on this batch reading</div>
            </div>
        """)

    # --------------------------------------------------------
    # SENSOR INSTRUMENT TILES
    # --------------------------------------------------------
    render_html('<div class="section-label"><span class="bar"></span>Sensor Monitoring</div>')

    tiles_html = '<div class="tile-row">' + "".join([
        render_tile("💧", "Moisture", data["moisture"], "", COPPER),
        render_tile("🌡", "Temperature", data["temperature"], "°C", GOLD),
        render_tile("💦", "Humidity", data["humidity"], "%", TEAL),
        render_tile("🔴", "Red Channel", data["red"], "", HOLD_C),
        render_tile("🟢", "Green / Blue", f"{data['green']} / {data['blue']}", "", PASS_C),
    ]) + '</div>'
    render_html(tiles_html)

    # --------------------------------------------------------
    # DETECTED CONDITION / RECOMMENDATION
    # --------------------------------------------------------
    render_html('<div class="section-label"><span class="bar"></span>Diagnostics</div>')

    d1, d2 = st.columns(2)
    with d1:
        render_html(f"""
            <div class="info-panel">
                <div class="info-panel-title">🔍 Detected Condition</div>
                <div class="info-panel-body">{result['issue']}</div>
            </div>
        """)
    with d2:
        render_html(f"""
            <div class="info-panel good">
                <div class="info-panel-title">🛠 Recovery Recommendation</div>
                <div class="info-panel-body">{result['recommendation']}</div>
            </div>
        """)

    # --------------------------------------------------------
    # SAVE CURRENT READING
    # --------------------------------------------------------
    reading = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "batch_id": batch_id,
        "time_min": int(time.time() / 60),
        "moisture_raw": data["moisture"],
        "red": data["red"],
        "green": data["green"],
        "blue": data["blue"],
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "moisture_status": classify_moisture(data["moisture"]),
        "color_status": classify_color(data["red"], data["green"], data["blue"]),
        "final_status": result["final_status"],
        "readiness_score": result["score"],
        "confidence": result["confidence"],
        "issue": result["issue"],
        "recommendation": result["recommendation"]
    }
    save_reading(reading)

    # --------------------------------------------------------
    # QUALITY BREAKDOWN
    # --------------------------------------------------------
    render_html('<div class="section-label"><span class="bar"></span>Quality Analysis Details</div>')

    q1, q2, q3 = st.columns(3)
    m_status = classify_moisture(data["moisture"])
    c_status = classify_color(data["red"], data["green"], data["blue"])

    with q1:
        mm = status_meta(m_status)
        render_html(render_mini("Moisture Condition", m_status, mm["color"]))
    with q2:
        cm = status_meta(c_status)
        render_html(render_mini("Color Condition", c_status, cm["color"]))
    with q3:
        fm = status_meta(result["final_status"])
        render_html(render_mini("Final Decision", result["final_status"], fm["color"]))

# ============================================================
# DATA HISTORY
# ============================================================

render_html('<div class="section-label"><span class="bar"></span>Production Monitoring History</div>')

try:
    history = pd.read_csv(CSV_FILE)

    if len(history) > 0:
        def highlight_status(val):
            m = status_meta(str(val))
            return f"background-color:{m['color']}22; color:{m['color']}; font-weight:600;"

        status_cols = [c for c in ["moisture_status", "color_status", "final_status"] if c in history.columns]
        display_df = history.tail(10).copy()
        styled = display_df.style.applymap(highlight_status, subset=status_cols)
        st.dataframe(styled, width="stretch", hide_index=True)
    else:
        st.info("No readings logged yet — history will populate as batches are analyzed.")
except Exception:
    st.warning("No historical data available.")

# ============================================================
# SENSOR TREND GRAPH (Plotly, control-room themed)
# ============================================================

render_html('<div class="section-label"><span class="bar"></span>Sensor Trend Analysis</div>')

def style_fig(fig, height=280):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT_MID, size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                     font=dict(color=TEXT_MID)),
        xaxis=dict(showgrid=False, zeroline=False, showline=False, color=TEXT_LOW),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False, color=TEXT_LOW),
        hovermode="x unified",
    )
    return fig

try:
    history = pd.read_csv(CSV_FILE)

    if len(history) > 1:
        t1, t2 = st.columns(2)

        with t1:
            st.caption("MOISTURE TREND")
            fig_m = go.Figure()
            fig_m.add_trace(go.Scatter(
                y=history["moisture_raw"], mode="lines",
                line=dict(color=COPPER, width=3, shape="spline"),
                fill="tozeroy", fillcolor="rgba(201,124,61,0.16)",
                name="Moisture"
            ))
            st.plotly_chart(style_fig(fig_m), width="stretch", config={"displayModeBar": False})

        with t2:
            st.caption("TEMPERATURE & HUMIDITY")
            fig_th = go.Figure()
            fig_th.add_trace(go.Scatter(
                y=history["temperature"], mode="lines",
                line=dict(color=GOLD, width=3, shape="spline"), name="Temperature (°C)"
            ))
            fig_th.add_trace(go.Scatter(
                y=history["humidity"], mode="lines",
                line=dict(color=TEAL, width=3, shape="spline"), name="Humidity (%)"
            ))
            st.plotly_chart(style_fig(fig_th), width="stretch", config={"displayModeBar": False})
    else:
        st.caption("Trend charts will appear once at least two readings are logged.")
except Exception:
    pass

# ============================================================
# COLOR SENSOR VISUALIZATION
# ============================================================

render_html('<div class="section-label"><span class="bar"></span>Color Sensor Reading</div>')

if data:
    sw1, sw2 = st.columns([1, 2.4])

    with sw1:
        raw_vals = [data["red"], data["green"], data["blue"]]
        peak = max(raw_vals) if max(raw_vals) > 0 else 1
        r_n = int(min(255, (data["red"] / peak) * 255))
        g_n = int(min(255, (data["green"] / peak) * 255))
        b_n = int(min(255, (data["blue"] / peak) * 255))
        render_html(f"""
            <div style="display:flex; flex-direction:column; align-items:center; gap:10px; padding-top:10px;">
                <div class="swatch-ring" style="background:rgb({r_n},{g_n},{b_n});"></div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:var(--text-low);">
                    RGB≈ {r_n}, {g_n}, {b_n}
                </div>
            </div>
        """)

    with sw2:
        fig_c = go.Figure()
        fig_c.add_trace(go.Bar(
            x=["Red", "Green", "Blue"],
            y=[data["red"], data["green"], data["blue"]],
            marker=dict(color=[HOLD_C, PASS_C, "#4A7FD6"], line=dict(width=0)),
            width=0.5
        ))
        st.plotly_chart(style_fig(fig_c, height=260), width="stretch", config={"displayModeBar": False})

# ============================================================
# FOOTER
# ============================================================

render_html("""
    <div class="nameplate">
        ☕ <b>Coffee Powder Packing Readiness Analyzer</b><br>
        Multi-Sensor Quality Inspection Prototype<br>
        Arduino UNO · TCS3200 · Moisture Sensor · DHT22
    </div>
""")

# ============================================================
# AUTO REFRESH
# ============================================================

if live_mode:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()