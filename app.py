import streamlit as st
import math
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Logistics Terminal", layout="wide")

# --- THE "NUCLEAR" DARK CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

    /* 1. REMOVE TOP DECORATION LINES & VOID */
    [data-testid="stDecoration"] { display: none !important; visibility: hidden !important; height: 0 !important; }
    [data-testid="stHeader"] { display: none !important; visibility: hidden !important; height: 0 !important; }
    header { visibility: hidden !important; height: 0 !important; }
    
    /* REMOVE ALL PADDING FROM TOP */
    .main .block-container { 
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important; 
        margin-top: -30px !important; 
    }

    /* 2. GLOBAL THEME & BACKGROUNDS */
    .stApp {
        background-color: #000000 !important;
        color: #98FF98 !important;
        font-family: 'JetBrains Mono', monospace;
    }

    /* 3. FORCE DROPDOWNS (SELECTBOX) TO DARK GREY */
    div[data-baseweb="select"] > div {
        background-color: #1a1a1a !important;
        border: 1px solid #98FF98 !important;
        color: #98FF98 !important;
    }
    /* The menu that pops out */
    div[data-baseweb="popover"] { background-color: #1a1a1a !important; }
    ul[data-baseweb="listbox"] { background-color: #1a1a1a !important; }
    li[data-baseweb="option"] { background-color: #1a1a1a !important; color: #98FF98 !important; }
    li[data-baseweb="option"]:hover { background-color: #333 !important; }

    /* 4. FORCE EXPANDER (DETAILS) TO STAY BLACK */
    div[data-testid="stExpander"] {
        background-color: #000000 !important;
        border: 1px solid #98FF98 !important;
        border-radius: 0px !important;
    }
    div[data-testid="stExpander"] > div:first-child { background-color: #000 !important; }
    div[data-testid="stExpanderDetails"] { 
        background-color: #000000 !important; 
        color: #98FF98 !important;
    }

    /* 5. TEXT & TABLES */
    h1, h2, h3, p, span, label, div {
        color: #98FF98 !important;
        text-transform: uppercase;
    }
    table { background-color: #000 !important; color: #98FF98 !important; border: 1px solid #98FF98 !important; }
    th, td { border: 1px solid #333 !important; }

    /* 6. INPUT BLOCKS */
    .input-block {
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        border-top: 1px solid #98FF98;
        padding-top: 10px;
    }

    /* 7. BUTTONS */
    .stButton > button {
        width: 100%;
        border: 1px solid #98FF98 !important;
        background-color: #111 !important;
        color: #98FF98 !important;
        border-radius: 0px;
        height: 40px;
        font-size: 10px !important;
    }

    /* 8. METRICS */
    [data-testid="stMetricValue"] { color: #98FF98 !important; font-size: 38px !important; }
    [data-testid="stMetricLabel"] { color: #98FF98 !important; }
    
    hr { border: 0; border-top: 1px solid #333; margin: 10px 0; }
    .tanker-container { display: flex; flex-wrap: wrap; gap: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- SVG PLACEHOLDERS ---
TANKER_SVG = """<svg width="80" height="100" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg"><path d="M30 5 L15 25 L15 85 L10 95 L50 95 L45 85 L45 25 Z" fill="#444" stroke="#98FF98"/></svg>"""
HLS_SVG = """<svg width="80" height="100" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg"><path d="M30 5 L15 30 L15 85 L45 85 L45 30 Z" fill="#DDD" stroke="#98FF98"/></svg>"""
ORION_SVG = """<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><path d="M40 45 L50 25 L60 45 Z" fill="#444" stroke="#98FF98"/><rect x="5" y="50" width="90" height="4" fill="#222" stroke="#98FF98"/></svg>"""

# --- STATE MANAGEMENT ---
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = "MODE 1: NO PUSH"

# --- CONTENT ---
st.markdown("<h2 style='text-align: center; letter-spacing: 5px; margin-bottom: 15px;'>HLS MISSION LOGISTICS</h2>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    st.markdown(TANKER_SVG, unsafe_allow_html=True)
    st.write("TANKER CONFIG")
    ref_amt = st.slider("PROP PER REFILL (t)", 50, 200, 100, step=5)
    cadence = st.slider("CADENCE (DAYS)", 1, 31, 7)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    st.markdown(HLS_SVG, unsafe_allow_html=True)
    st.write("HLS CONFIG")
    dry_m = st.slider("HLS DRY MASS (t)", 80, 250, 120, step=5)
    isp = st.slider("ENGINE ISP (s)", 350, 380, 375)
    orbit = st.selectbox("STAGING ORBIT", ["NRHO", "LLO", "PCO"])
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    st.markdown(ORION_SVG, unsafe_allow_html=True)
    st.write("ORION MODE")
    
    modes = ["MODE 1: NO PUSH", "MODE 2: LEO TO STAGING"]
    if orbit == "LLO": modes += ["MODE 3: NRHO TO LLO", "MODE 4: PCO TO LLO"]
    elif orbit == "PCO": modes += ["MODE 3: NRHO TO PCO"]

    for m in modes:
        active = st.session_state.selected_mode == m
        label = f"▶ {m}" if active else m
        if active:
            st.markdown(f"<style>div.stButton > button:first-child:contains('{m}') {{ background-color: #98FF98 !important; color: black !important; font-weight: bold; }}</style>", unsafe_allow_html=True)
        if st.button(label):
            st.session_state.selected_mode = m
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- MATH ---
G = 9.80665
OM = 27.0
DV = {
    "LEO_TO_TLI": 3200, "TLI_TO_NRHO": 450, "TLI_TO_LLO": 900, "TLI_TO_PCO": 800,
    "NRHO_TO_SURFACE": 2750, "LLO_TO_SURFACE": 2000, "PCO_TO_SURFACE": 2400
}

def get_telemetry():
    m = st.session_state.selected_mode
    log = []
    
    # Backward Integration
    dva = DV[f"{orbit}_TO_SURFACE"]
    maf = dry_m
    mai = maf * math.exp(dva / (isp * G))
    log.append({"LEG": "ASCENT: SURFACE TO ORBIT", "DV": dva, "WET MASS": f"{mai:.1f}t", "DRY MASS": f"{maf:.1f}t", "VEHICLE": "HLS"})

    dvd = dva
    mdf = mai
    mdi = mdf * math.exp(dvd / (isp * G))
    log.append({"LEG": "DESCENT: ORBIT TO SURFACE", "DV": dvd, "WET MASS": f"{mdi:.1f}t", "DRY MASS": f"{mdf:.1f}t", "VEHICLE": "HLS"})

    curr = mdi
    if "MODE 3" in m or "MODE 4" in m:
        dvp = 450 if "NRHO TO LLO" in m else 400 if "PCO TO LLO" in m else 350
        mpf = curr + OM
        mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH MANEUVER", "DV": dvp, "WET MASS": f"{mpi:.1f}t", "DRY MASS": f"{mpf:.1f}t", "VEHICLE": "HLS + 27t ORION"})
        curr = mpi - OM

    dva2 = DV[f"TLI_TO_{orbit}"]
    has_o = "MODE 2" in m
    ma2f = curr + (OM if has_o else 0)
    ma2i = ma2f * math.exp(dva2 / (isp * G))
    log.append({"LEG": f"ARRIVAL AT {orbit}", "DV": dva2, "WET MASS": f"{ma2i:.1f}t", "DRY MASS": f"{ma2f:.1f}t", "VEHICLE": f"HLS {'+ 27t ORION' if has_o else ''}"})

    dv_leo = 3200
    m_leo_f = ma2i
    m_leo_i = m_leo_f * math.exp(dv_leo / (isp * G))
    log.append({"LEG": "TLI DEPARTURE (LEO)", "DV": dv_leo, "WET MASS": f"{m_leo_i:.1f}t", "DRY MASS": f"{m_leo_f:.1f}t", "VEHICLE": f"HLS {'+ 27t ORION' if has_o else ''}"})

    prop = m_leo_i - dry_m - (OM if has_o else 0)
    if "MODE 3" in m or "MODE 4" in m: prop = m_leo_i - dry_m
    return prop, log

total_p, t_log = get_telemetry()
tanks = math.ceil(total_p / ref_amt)

# --- RESULTS ---
st.markdown("<hr>", unsafe_allow_html=True)
r1, r2, r3 = st.columns(3)
with r1: st.metric("TANKERS", tanks)
with r2: st.metric("TOTAL PROPELLANT", f"{total_p:,.1f} T")
with r3: st.metric("REFILL CAMPAIGN LENGTH", f"{tanks * cadence} DAYS")

t_icons = "".join([f"<div style='display:inline-block; margin-right:4px;'>{TANKER_SVG}</div>" for _ in range(tanks)])
st.markdown(f"<div class='tanker-container'>{t_icons}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
with st.expander("▶ VIEW DETAILED TELEMETRY LOG"):
    st.table(pd.DataFrame(t_log))
