import os
import sys
import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.logic import (
    classify_moisture,
    classify_color,
    combine_status,
    calculate_readiness_score,
    parse_arduino_line,
    color_distance,
)
from backend.serial_reader import read_from_arduino


BASE_DIR = os.path.dirname(__file__)
CSV_FILE = os.path.join(BASE_DIR, "readings.csv")

CSV_COLUMNS = [
    "timestamp",
    "batch_id",
    "time_min",
    "moisture_raw",
    "red",
    "green",
    "blue",
    "moisture_status",
    "color_status",
    "final_status",
    "readiness_score",
]


st.set_page_config(
    page_title="Coffee Factory QC Dashboard",
    page_icon="☕",
    layout="wide",
)


st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(255, 191, 31, 0.12), transparent 30%),
        radial-gradient(circle at top right, rgba(111, 61, 31, 0.14), transparent 28%),
        linear-gradient(180deg, #f8f3ec 0%, #f1e8dc 100%);
    color: #2f241f;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2.5rem;
    max-width: 1450px;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #2b160d 0%, #5b2f18 42%, #9a5b2a 100%);
    padding: 36px 38px;
    border-radius: 30px;
    color: white;
    margin-bottom: 22px;
    box-shadow: 0 18px 38px rgba(59, 33, 22, 0.34);
    border: 1px solid rgba(255,255,255,0.10);
}

.hero:before {
    content: "";
    position: absolute;
    width: 260px;
    height: 260px;
    right: -70px;
    top: -100px;
    background: radial-gradient(circle, rgba(255, 213, 145, 0.28), transparent 70%);
}

.hero-topline {
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #ffd99e;
    font-weight: 800;
    margin-bottom: 8px;
}

.hero-title {
    font-size: 43px;
    font-weight: 950;
    line-height: 1.1;
    margin-bottom: 12px;
}

.hero-subtitle {
    font-size: 16px;
    color: #f7dfbf;
    line-height: 1.65;
    max-width: 980px;
}

.status-pass {
    padding: 28px;
    border-radius: 26px;
    background: linear-gradient(135deg, #075f3a, #19b875);
    color: white;
    font-size: 35px;
    font-weight: 950;
    text-align: center;
    box-shadow: 0 16px 30px rgba(25, 184, 117, 0.28);
    border: 1px solid rgba(255,255,255,0.12);
}

.status-warn {
    padding: 28px;
    border-radius: 26px;
    background: linear-gradient(135deg, #9a6900, #ffc43d);
    color: white;
    font-size: 35px;
    font-weight: 950;
    text-align: center;
    box-shadow: 0 16px 30px rgba(255, 196, 61, 0.28);
    border: 1px solid rgba(255,255,255,0.12);
}

.status-hold {
    padding: 28px;
    border-radius: 26px;
    background: linear-gradient(135deg, #8d1724, #ef3f50);
    color: white;
    font-size: 35px;
    font-weight: 950;
    text-align: center;
    box-shadow: 0 16px 30px rgba(239, 63, 80, 0.30);
    border: 1px solid rgba(255,255,255,0.12);
}

.metric-card {
    background: rgba(255,255,255,0.96);
    border: 1px solid rgba(122,74,37,0.12);
    border-radius: 25px;
    padding: 22px 22px 18px 22px;
    box-shadow: 0 12px 26px rgba(80, 53, 32, 0.10);
    min-height: 142px;
}

.metric-icon {
    font-size: 28px;
    margin-bottom: 8px;
}

.metric-label {
    font-size: 14px;
    color: #7a6a5c;
    font-weight: 750;
}

.metric-value {
    font-size: 29px;
    font-weight: 950;
    color: #2e2119;
    margin-top: 6px;
}

.metric-mini {
    font-size: 12px;
    color: #9a8778;
    margin-top: 5px;
}

.kpi-card {
    background: linear-gradient(135deg, #ffffff, #fff6eb);
    border: 1px solid rgba(122,74,37,0.10);
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 10px 22px rgba(80,53,32,0.08);
}

.kpi-label {
    color: #806f63;
    font-size: 13px;
    font-weight: 750;
}

.kpi-value {
    color: #3b2116;
    font-size: 30px;
    font-weight: 950;
    margin-top: 5px;
}

.panel-card {
    background: rgba(255,255,255,0.97);
    border: 1px solid rgba(122,74,37,0.10);
    border-radius: 26px;
    padding: 22px;
    box-shadow: 0 12px 28px rgba(80,53,32,0.09);
    margin-bottom: 18px;
}

.section-title {
    font-size: 29px;
    font-weight: 950;
    color: #3b2116;
    margin-bottom: 6px;
}

.section-sub {
    font-size: 14px;
    color: #7a6a5c;
    margin-bottom: 14px;
    line-height: 1.5;
}

.breakdown-card {
    background: linear-gradient(180deg, #fffaf5 0%, #fff3e5 100%);
    border: 1px solid #efd9bf;
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 8px 18px rgba(122,74,37,0.08);
}

.badge-pass, .badge-warn, .badge-hold {
    display: inline-block;
    padding: 8px 15px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 900;
    margin: 4px 6px 8px 0;
}

.badge-pass {
    background: rgba(25, 184, 117, 0.14);
    color: #08784a;
}

.badge-warn {
    background: rgba(255, 196, 61, 0.20);
    color: #8a6200;
}

.badge-hold {
    background: rgba(239, 63, 80, 0.15);
    color: #a61c29;
}

.live-chip {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(25, 184, 117, 0.14);
    color: #08784a;
    font-weight: 900;
    font-size: 13px;
    margin-bottom: 10px;
}

.footer-note {
    background: linear-gradient(135deg, #2b160d, #6f3d1f);
    color: #f6e9db;
    padding: 20px 24px;
    border-radius: 22px;
    margin-top: 18px;
    box-shadow: 0 10px 22px rgba(59,33,22,0.20);
    font-size: 14px;
    line-height: 1.7;
}

/* Modern Live Decision Panel */
.live-decision-card {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at top right, rgba(255, 196, 61, 0.16), transparent 28%),
        linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,248,238,0.96));
    border: 1px solid rgba(122, 74, 37, 0.12);
    border-radius: 30px;
    padding: 28px;
    box-shadow: 0 18px 36px rgba(80, 53, 32, 0.12);
    margin-bottom: 20px;
}

.live-decision-card:before {
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    right: -70px;
    top: -90px;
    background: radial-gradient(circle, rgba(154, 91, 42, 0.18), transparent 70%);
}

.live-decision-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    position: relative;
    z-index: 1;
}

.live-decision-kicker {
    font-size: 12px;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    font-weight: 950;
    color: #9a7a62;
    margin-bottom: 6px;
}

.live-decision-title {
    font-size: 36px;
    font-weight: 950;
    line-height: 1.12;
    margin-bottom: 10px;
}

.live-decision-desc {
    color: #6f5b4d;
    font-size: 15px;
    line-height: 1.65;
    max-width: 900px;
}

.live-status-orb {
    width: 92px;
    height: 92px;
    border-radius: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 42px;
    box-shadow: 0 16px 28px rgba(43,22,13,0.14);
    flex-shrink: 0;
}

.live-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-top: 22px;
    position: relative;
    z-index: 1;
}

.live-mini-card {
    background: rgba(255,255,255,0.90);
    border: 1px solid rgba(122,74,37,0.10);
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 10px 22px rgba(80,53,32,0.08);
}

.live-mini-label {
    color: #806f63;
    font-size: 13px;
    font-weight: 850;
    margin-bottom: 7px;
}

.live-mini-value {
    color: #2e2119;
    font-size: 28px;
    font-weight: 950;
}

.live-action-box {
    margin-top: 20px;
    padding: 18px 20px;
    border-radius: 22px;
    background: linear-gradient(135deg, #fff7ec, #ffffff);
    border: 1px solid rgba(122,74,37,0.12);
    color: #3b2116;
    font-size: 15px;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

.live-detail-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-top: 14px;
    position: relative;
    z-index: 1;
}

.live-detail-box {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(122,74,37,0.10);
    border-radius: 20px;
    padding: 15px;
    color: #6f5b4d;
    font-size: 13px;
    line-height: 1.6;
}

.live-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}

.live-chip-small {
    padding: 8px 11px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 950;
}

.chip-pass {
    background: rgba(25, 184, 117, 0.14);
    color: #08784a;
}

.chip-warn {
    background: rgba(255, 196, 61, 0.22);
    color: #8a6200;
}

.chip-hold {
    background: rgba(239, 63, 80, 0.15);
    color: #a61c29;
}

.chip-color {
    background: rgba(111, 61, 31, 0.10);
    color: #5b2f18;
}

/* Premium Sidebar */
section[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(255, 196, 61, 0.18), transparent 28%),
        radial-gradient(circle at bottom right, rgba(111, 61, 31, 0.18), transparent 30%),
        linear-gradient(180deg, #2b160d 0%, #5b2f18 45%, #efe0cf 100%) !important;
    border-right: 1px solid rgba(255, 217, 158, 0.25);
    box-shadow: 12px 0 35px rgba(43, 22, 13, 0.18);
}

.sidebar-hero-card {
    background: linear-gradient(135deg, #2b160d 0%, #6f3d1f 60%, #9a5b2a 100%);
    border-radius: 26px;
    padding: 22px 18px;
    margin-bottom: 18px;
    box-shadow: 0 18px 34px rgba(43, 22, 13, 0.34);
    border: 1px solid rgba(255,255,255,0.12);
}

.sidebar-hero-kicker {
    color: #ffd99e !important;
    font-size: 11px;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    font-weight: 900;
    margin-bottom: 8px;
}

.sidebar-hero-title {
    color: #ffffff !important;
    font-size: 24px;
    font-weight: 950;
    line-height: 1.15;
    margin-bottom: 8px;
}

.sidebar-hero-sub {
    color: #f7dfbf !important;
    font-size: 12.5px;
    line-height: 1.55;
}

.sidebar-glass-card {
    background: rgba(255, 249, 241, 0.92);
    border: 1px solid rgba(255, 217, 158, 0.35);
    border-radius: 24px;
    padding: 18px;
    margin-bottom: 18px;
    box-shadow: 0 14px 28px rgba(43, 22, 13, 0.18);
}

.sidebar-section-title {
    color: #3b2116 !important;
    font-size: 18px;
    font-weight: 950;
    margin-bottom: 6px;
}

.sidebar-section-sub {
    color: #7a6a5c !important;
    font-size: 12.5px;
    line-height: 1.55;
    margin-bottom: 12px;
}

.sidebar-status-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 12px;
}

.sidebar-status-pill {
    border-radius: 16px;
    padding: 12px 10px;
    text-align: center;
    font-weight: 950;
    font-size: 12px;
    box-shadow: 0 8px 16px rgba(80,53,32,0.08);
}

.pill-pass {
    background: rgba(25, 184, 117, 0.14);
    color: #08784a !important;
    border: 1px solid rgba(25, 184, 117, 0.25);
}

.pill-warn {
    background: rgba(255, 196, 61, 0.22);
    color: #8a6200 !important;
    border: 1px solid rgba(255, 196, 61, 0.35);
}

.pill-hold {
    background: rgba(239, 63, 80, 0.15);
    color: #a61c29 !important;
    border: 1px solid rgba(239, 63, 80, 0.25);
}

.sidebar-footer-badge {
    background: rgba(43, 22, 13, 0.92);
    color: #f7dfbf !important;
    border-radius: 18px;
    padding: 14px;
    font-size: 12px;
    line-height: 1.55;
    border: 1px solid rgba(255, 217, 158, 0.2);
}

.sidebar-footer-badge b {
    color: #ffd99e !important;
}

section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stNumberInput input {
    border-radius: 16px !important;
    border: 1px solid rgba(122,74,37,0.22) !important;
    background: rgba(255,255,255,0.96) !important;
    color: #3b2116 !important;
    font-weight: 800 !important;
    box-shadow: 0 8px 16px rgba(80,53,32,0.08);
}

section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #2b160d 0%, #6f3d1f 100%) !important;
    color: #fff7ec !important;
    border: 1px solid rgba(255, 217, 158, 0.35) !important;
    border-radius: 17px !important;
    font-weight: 950 !important;
    box-shadow: 0 12px 22px rgba(43,22,13,0.24) !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #6f3d1f 0%, #9a5b2a 100%) !important;
    transform: translateY(-2px);
}

section[data-testid="stSidebar"] label {
    color: #3b2116 !important;
    font-weight: 850 !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.20) !important;
    margin: 18px 0 !important;
}

@media (max-width: 1000px) {
    .live-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .live-detail-row {
        grid-template-columns: 1fr;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


def empty_dataframe():
    return pd.DataFrame(columns=CSV_COLUMNS)


def init_csv():
    if (not os.path.exists(CSV_FILE)) or os.path.getsize(CSV_FILE) == 0:
        df = empty_dataframe()
        df.to_csv(CSV_FILE, index=False)


def clean_dataframe(df):
    for col in ["time_min", "moisture_raw", "red", "green", "blue", "readiness_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in ["timestamp", "batch_id", "moisture_status", "color_status", "final_status"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    return df


def load_data():
    init_csv()

    try:
        df = pd.read_csv(CSV_FILE)
    except pd.errors.EmptyDataError:
        df = empty_dataframe()
        df.to_csv(CSV_FILE, index=False)

    for col in CSV_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[CSV_COLUMNS]
    df = clean_dataframe(df)
    return df


def save_data(df):
    df = df[CSV_COLUMNS]
    df.to_csv(CSV_FILE, index=False)


def append_reading(batch_id, time_min, moisture, r, g, b):
    df = load_data()

    moisture_status = classify_moisture(moisture)
    color_status = classify_color(r, g, b)
    final_status = combine_status(moisture_status, color_status)
    readiness_score = calculate_readiness_score(moisture_status, color_status)

    new_row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "batch_id": batch_id,
        "time_min": time_min,
        "moisture_raw": moisture,
        "red": r,
        "green": g,
        "blue": b,
        "moisture_status": moisture_status,
        "color_status": color_status,
        "final_status": final_status,
        "readiness_score": readiness_score,
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)


def get_next_time(df, batch_id):
    if len(df) == 0:
        return 0

    selected = df[df["batch_id"] == batch_id]

    if len(selected) == 0:
        return 0

    return int(selected["time_min"].max()) + 5


def status_banner(status):
    class_name = {
        "PASS": "status-pass",
        "WARN": "status-warn",
        "HOLD": "status-hold",
    }.get(status, "status-warn")

    label = {
        "PASS": "✅ PASS — Ready for Packing",
        "WARN": "⚠️ WARN — Monitor Before Packing",
        "HOLD": "🚫 HOLD — Do Not Pack",
    }.get(status, status)

    st.markdown(f'<div class="{class_name}">{label}</div>', unsafe_allow_html=True)


def metric_card(icon, label, value, mini_text=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-mini">{mini_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label, value):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge(status, label):
    status_lower = str(status).lower()

    if status_lower not in ["pass", "warn", "hold"]:
        status_lower = "warn"

    return f'<div class="badge-{status_lower}">{label}: {status}</div>'


def live_decision_panel(latest):
    moisture_raw = int(latest["moisture_raw"])
    r = int(latest["red"])
    g = int(latest["green"])
    b = int(latest["blue"])
    moisture_status = str(latest["moisture_status"])
    color_status = str(latest["color_status"])
    final_status = str(latest["final_status"])
    readiness_score = int(latest["readiness_score"])
    distance = color_distance(r, g, b)

    if final_status == "PASS":
        decision_icon = "✅"
        decision_title = "PASS — Ready for Packing"
        decision_color = "#19b875"
        orb_bg = "linear-gradient(135deg, #075f3a, #19b875)"
        action_text = "Batch can move to packing."
        explanation = "Moisture and roast-color readings are within the calibrated accepted range."
    elif final_status == "WARN":
        decision_icon = "⚠️"
        decision_title = "WARN — Monitor Before Packing"
        decision_color = "#ffc43d"
        orb_bg = "linear-gradient(135deg, #9a6900, #ffc43d)"
        action_text = "Recheck sample or monitor for another short interval."
        explanation = "One quality signal is near the warning boundary. Packing should be delayed until confirmed stable."
    else:
        decision_icon = "🚫"
        decision_title = "HOLD — Do Not Pack"
        decision_color = "#ef3f50"
        orb_bg = "linear-gradient(135deg, #8d1724, #ef3f50)"
        action_text = "Do not send this batch to packing."
        explanation = "Moisture or roast-color reading indicates a rejected/risky condition for packing."

    html = f"""
<div class="live-decision-card" style="border-left: 10px solid {decision_color};">
<div class="live-decision-top">
<div>
<div class="live-decision-kicker">Live Quality Decision</div>
<div class="live-decision-title" style="color: {decision_color};">
{decision_title}
</div>
<div class="live-decision-desc">
{explanation}
</div>
</div>
<div class="live-status-orb" style="background: {orb_bg}; color: white;">
{decision_icon}
</div>
</div>

<div class="live-grid">
<div class="live-mini-card">
<div class="live-mini-label">💧 Moisture Raw</div>
<div class="live-mini-value">{moisture_raw}</div>
</div>

<div class="live-mini-card">
<div class="live-mini-label">Moisture Status</div>
<div class="live-mini-value" style="color: {decision_color};">{moisture_status}</div>
</div>

<div class="live-mini-card">
<div class="live-mini-label">Color Status</div>
<div class="live-mini-value" style="color: {decision_color};">{color_status}</div>
</div>

<div class="live-mini-card">
<div class="live-mini-label">Readiness Score</div>
<div class="live-mini-value">{readiness_score}%</div>
</div>
</div>

<div class="live-action-box">
<b>🏭 Recommended Factory Action:</b> {action_text}
</div>

<div class="live-detail-row">
<div class="live-detail-box">
<b>Moisture Decision Boundaries</b>
<div class="live-chip-row">
<span class="live-chip-small chip-pass">PASS ≥ 430</span>
<span class="live-chip-small chip-warn">WARN 350–429</span>
<span class="live-chip-small chip-hold">HOLD &lt; 350</span>
</div>
</div>

<div class="live-detail-box">
<b>Color Consistency Boundaries</b>
<div class="live-chip-row">
<span class="live-chip-small chip-pass">Distance ≤ 145</span>
<span class="live-chip-small chip-warn">146–190</span>
<span class="live-chip-small chip-hold">&gt; 190</span>
</div>
</div>

<div class="live-detail-box">
<b>Latest TCS3200 Reading</b>
<div class="live-chip-row">
<span class="live-chip-small chip-color">R {r}</span>
<span class="live-chip-small chip-color">G {g}</span>
<span class="live-chip-small chip-color">B {b}</span>
<span class="live-chip-small chip-color">D {distance:.1f}</span>
</div>
</div>
</div>
</div>
"""

    st.markdown(html, unsafe_allow_html=True)


def make_gauge(score):
    score = int(score)

    if score >= 75:
        bar_color = "#19b875"
    elif score >= 50:
        bar_color = "#ffc43d"
    else:
        bar_color = "#ef3f50"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Packing Readiness Score", "font": {"size": 20}},
            number={"suffix": "%", "font": {"size": 38, "color": "#3b2116"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#6f3d1f"},
                "bar": {"color": bar_color},
                "bgcolor": "white",
                "borderwidth": 1,
                "bordercolor": "rgba(122,74,37,0.18)",
                "steps": [
                    {"range": [0, 50], "color": "#ffd6dc"},
                    {"range": [50, 75], "color": "#ffe8a8"},
                    {"range": [75, 100], "color": "#c9f4df"},
                ],
                "threshold": {
                    "line": {"color": "#3b2116", "width": 4},
                    "thickness": 0.75,
                    "value": score,
                },
            },
        )
    )

    fig.update_layout(
        height=305,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#3b2116"},
    )
    return fig


def read_and_store_live_reading(port, batch_id, next_time_min):
    line = read_from_arduino(port=port)
    parsed = parse_arduino_line(line)

    if parsed is None:
        return False, f"Invalid Arduino data received: {line}"

    moisture, r, g, b, arduino_status = parsed
    append_reading(batch_id, next_time_min, moisture, r, g, b)

    return True, f"Live reading saved. Arduino status: {arduino_status}"


init_csv()


st.markdown(
    """
<div class="hero">
    <div class="hero-topline">Factory Floor Prototype • Real-Time QC Screening</div>
    <div class="hero-title">☕ Coffee Factory Packing Readiness Control Center</div>
    <div class="hero-subtitle">
        Premium real-time decision support for post-grind coffee powder packing readiness.
        The system monitors moisture stability, roast color consistency, batch traceability,
        and generates PASS / WARN / HOLD decisions through a modern factory dashboard.
    </div>
</div>
""",
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-hero-card">
            <div class="sidebar-hero-kicker">Arduino • Sensor • Factory QC</div>
            <div class="sidebar-hero-title">☕ Live Device Control</div>
            <div class="sidebar-hero-sub">
                Real-time coffee powder packing readiness monitoring with calibrated decision support.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-glass-card">
            <div class="sidebar-section-title">⚙️ Connection Setup</div>
            <div class="sidebar-section-sub">USB based Arduino live data connection.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    port = st.text_input("Arduino COM Port", value="COM3")
    batch_id = st.text_input("Batch ID", value="BATCH_001")

    st.divider()

    st.markdown(
        """
        <div class="sidebar-glass-card">
            <div class="sidebar-section-title">📡 Live Acquisition</div>
            <div class="sidebar-section-sub">Manual or automatic sensor data reading.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    read_button = st.button("📡 Read Live Device Data", use_container_width=True)

    auto_live = st.checkbox("🔴 Auto Live Mode", value=True)

    live_interval = st.number_input(
        "Auto read interval seconds",
        min_value=5,
        max_value=60,
        value=8,
        step=1,
    )

    st.markdown(
        """
        <div class="sidebar-status-row">
            <div class="sidebar-status-pill pill-pass">PASS ≥ 430</div>
            <div class="sidebar-status-pill pill-warn">WARN 350–429</div>
        </div>
        <div class="sidebar-status-row" style="grid-template-columns: 1fr;">
            <div class="sidebar-status-pill pill-hold">HOLD &lt; 350</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        """
        <div class="sidebar-glass-card">
            <div class="sidebar-section-title">🧪 Factory Test Samples</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    demo_pass = st.button("✅ Add PASS Sample", use_container_width=True)
    demo_warn = st.button("⚠️ Add WARN Sample", use_container_width=True)
    demo_hold = st.button("🚫 Add HOLD Sample", use_container_width=True)

    st.divider()

    st.markdown(
        """
        <div class="sidebar-glass-card">
            <div class="sidebar-section-title">🗂️ Data Control</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    clear_data = st.button("🗑 Clear CSV Data", use_container_width=True)

    st.divider()

    st.markdown(
        """
        <div class="sidebar-footer-badge">
            <b>Storage Layer</b><br>
            Phase 1: CSV traceability<br>
            Phase 2: SQLite upgrade
        </div>
        """,
        unsafe_allow_html=True,
    )


df = load_data()
next_time_min = get_next_time(df, batch_id)

if clear_data:
    save_data(empty_dataframe())
    st.success("CSV data cleared successfully.")
    st.rerun()

if read_button:
    try:
        success, message = read_and_store_live_reading(port, batch_id, next_time_min)

        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

    except Exception as e:
        st.error(f"Could not read from Arduino: {e}")
        st.info("Close Arduino Serial Monitor and check COM port.")

if demo_pass:
    # Correct coffee powder sample from final chamber calibration
    append_reading(batch_id, next_time_min, 552, 320, 382, 328)
    st.success("PASS sample added.")
    st.rerun()

if demo_warn:
    # Borderline sample: moisture warning range + slight color variation
    append_reading(batch_id, next_time_min, 400, 450, 460, 390)
    st.warning("WARN sample added.")
    st.rerun()

if demo_hold:
    # Risky/rejected sample: moisture below HOLD boundary
    append_reading(batch_id, next_time_min, 330, 399, 454, 376)
    st.error("HOLD sample added.")
    st.rerun()


auto_message = None

if auto_live:
    try:
        df_for_live = load_data()
        next_live_time = get_next_time(df_for_live, batch_id)

        success, message = read_and_store_live_reading(port, batch_id, next_live_time)
        auto_message = (success, message)

    except Exception as e:
        auto_message = (False, f"Auto live read failed: {e}")


df = load_data()

if len(df) == 0:
    st.info("No readings yet. Connect Arduino or use demo samples from the sidebar.")

    if auto_live:
        time.sleep(int(live_interval))
        st.rerun()

    st.stop()

latest = df.iloc[-1]
selected_batch = df[df["batch_id"] == batch_id].copy()

if selected_batch.empty:
    selected_batch = df.copy()

selected_batch = selected_batch.sort_values("time_min")


if auto_live:
    st.markdown(
        '<div class="live-chip">🔴 Auto Live Mode Active — Reading Arduino every few seconds</div>',
        unsafe_allow_html=True,
    )

    if auto_message:
        success, message = auto_message

        if success:
            st.success(message)
        else:
            st.warning(message)


total_readings = len(df)
pass_count = int((df["final_status"] == "PASS").sum())
warn_count = int((df["final_status"] == "WARN").sum())
hold_count = int((df["final_status"] == "HOLD").sum())

k1, k2, k3, k4 = st.columns(4)

with k1:
    kpi_card("Total Readings", total_readings)

with k2:
    kpi_card("PASS Count", pass_count)

with k3:
    kpi_card("WARN Count", warn_count)

with k4:
    kpi_card("HOLD Count", hold_count)

st.write("")

status_banner(latest["final_status"])
st.write("")

live_decision_panel(latest)
st.write("")

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("💧", "Moisture Raw", latest["moisture_raw"], "Calibrated capacitive sensor value")

with m2:
    metric_card("🎨", "Color Reading", f'{latest["red"]}, {latest["green"]}, {latest["blue"]}', "TCS3200 calibrated frequency values")

with m3:
    metric_card("🎯", "Readiness Score", f'{latest["readiness_score"]}%', "Combined moisture + color score")

with m4:
    metric_card("🏷️", "Batch ID", latest["batch_id"], "Latest tracked batch")

st.write("")


left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Time-Aware Moisture Stability</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Higher values indicate dry/stable powder. Lower values indicate wet/risky powder. Calibrated boundaries: PASS ≥ 430, WARN 350–429, HOLD < 350.</div>',
        unsafe_allow_html=True,
    )

    fig = px.line(
        selected_batch,
        x="time_min",
        y="moisture_raw",
        markers=True,
        title="Moisture Trend During Holding Period",
    )

    fig.update_traces(line=dict(width=4), marker=dict(size=9))
    fig.update_layout(
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="white",
        title_font_size=18,
        font=dict(color="#3b2116"),
        margin=dict(l=20, r=20, t=55, b=20),
    )

    fig.add_hline(
        y=430,
        line_dash="dash",
        line_color="#19b875",
        annotation_text="PASS Boundary: 430",
        annotation_position="top left",
    )

    fig.add_hline(
        y=350,
        line_dash="dash",
        line_color="#ef3f50",
        annotation_text="HOLD Boundary: 350",
        annotation_position="bottom left",
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎯 Packing Readiness</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Overall score based on moisture stability and roast color consistency.</div>',
        unsafe_allow_html=True,
    )

    st.plotly_chart(make_gauge(latest["readiness_score"]), use_container_width=True)

    st.markdown('<div class="breakdown-card">', unsafe_allow_html=True)
    st.markdown("### Latest Breakdown")
    st.markdown(
        badge(latest["moisture_status"], "Moisture")
        + badge(latest["color_status"], "Color")
        + badge(latest["final_status"], "Final"),
        unsafe_allow_html=True,
    )
    st.write(f"**Timestamp:** {latest['timestamp']}")
    st.write(f"**Readiness Score:** {latest['readiness_score']}%")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🎨 Roast Color Consistency Trend</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">TCS3200 values are compared with the final chamber accepted coffee powder reference: R324, G392, B329. Larger distance indicates roast/color variation.</div>',
    unsafe_allow_html=True,
)

fig2 = px.line(
    selected_batch,
    x="time_min",
    y=["red", "green", "blue"],
    markers=True,
    title="TCS3200 Color Sensor Frequency Trend",
    color_discrete_map={
        "red": "#ef3f50",
        "green": "#19b875",
        "blue": "#2f80ed",
    },
)

fig2.update_traces(line=dict(width=3), marker=dict(size=8))
fig2.update_layout(
    height=380,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="white",
    title_font_size=18,
    font=dict(color="#3b2116"),
    margin=dict(l=20, r=20, t=55, b=20),
)

st.plotly_chart(fig2, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


col_a, col_b = st.columns([1, 1])

with col_a:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Decision Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">PASS / WARN / HOLD decision summary for stored traceability records.</div>',
        unsafe_allow_html=True,
    )

    status_counts = df["final_status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]

    fig3 = px.bar(
        status_counts,
        x="status",
        y="count",
        title="Decision Count Summary",
        color="status",
        color_discrete_map={
            "PASS": "#19b875",
            "WARN": "#ffc43d",
            "HOLD": "#ef3f50",
        },
    )

    fig3.update_layout(
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="white",
        title_font_size=18,
        font=dict(color="#3b2116"),
        showlegend=False,
        margin=dict(l=20, r=20, t=55, b=20),
    )

    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_b:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏭 Factory Action Guide</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Recommended operator action based on the latest screening decision.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="breakdown-card">
            <p>✅ <b>PASS:</b> Batch can move to packing.</p>
            <p>⚠️ <b>WARN:</b> Recheck sample or monitor for another short interval.</p>
            <p>🚫 <b>HOLD:</b> Do not send batch to packing until quality is rechecked.</p>
            <hr>
            <p><b>Panel wording:</b> This is a calibrated threshold-based decision-support prototype, not a lab replacement.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 Batch History & Traceability Log</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Latest stored readings for CSV-based Phase 1 traceability.</div>',
    unsafe_allow_html=True,
)

st.dataframe(df.tail(50), use_container_width=True, hide_index=True)
st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    """
<div class="footer-note">
    <b>Prototype Note:</b> This system is designed as a <b>factory-floor packing readiness screening prototype</b>.
    In Phase 1, readings are stored using a <b>CSV-based traceability layer</b>.
    After validating the complete sensor-to-dashboard pipeline, the storage layer can be upgraded to
    <b>SQLite in Phase 2</b> for structured local batch traceability.
</div>
""",
    unsafe_allow_html=True,
)


if auto_live:
    time.sleep(int(live_interval))
    st.rerun()