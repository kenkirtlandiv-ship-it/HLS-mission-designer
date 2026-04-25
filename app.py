import streamlit as st
import math
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Logistics Terminal", layout="wide")

# --- CUSTOM CSS: THE "HARDENED" DARK TERMINAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

    /* 1. FORCE REMOVE TOP GAP AND LINES */
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    header { visibility: hidden !important; height: 0 !important; }
    .main .block-container { 
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important; 
        margin-top: -45px !important; 
    }

    /* 2. GLOBAL DARK THEME */
    .stApp {
        background-color: #000000 !important;
        color: #98FF98 !important;
        font-family: 'JetBrains Mono', monospace;
    }

    /* 3. DROPDOWN & SELECTBOX HARDENING (DARK GREY) */
    div[data-baseweb="select"] > div {
        background-color: #1a1a1a !important;
        border: 1px solid #98FF98 !important;
        color: #98FF98 !important;
    }
    div[data-baseweb="popover"], div[role="listbox"], ul {
        background-color: #1a1a1a !important;
        color: #98FF98 !important;
        border: 1px solid #98FF98 !important;
    }
    li[role="option"], div[role="option"] {
        background-color: #1a1a1a !important;
        color: #98FF98 !important;
    }
    li[role="option"]:hover, div[role="option"]:hover {
        background-color: #333 !important;
    }

    /* 4. EXPANDER & TABLE HARDENING */
    div[data-testid="stExpander"] {
        background-color: #000000 !important;
        border: 1px solid #98FF98 !important;
        border-radius: 0px !important;
    }
    div[data-testid="stExpanderDetails"] {
        background-color: #000000 !important;
        color: #98FF98 !important;
    }
    table { background-color: #000 !important; border: 1px solid #98FF98 !important; width: 100%; }
    th, td { border: 1px solid #333 !important; color: #98FF98 !important; padding: 8px; }

    /* 5. TEXT & LAYOUT */
    h1, h2, h3, p, span, label, div {
        color: #98FF98 !important;
        text-transform: uppercase;
    }
    .input-block {
        min-height: 480px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        border-top: 1px solid #98FF98;
        padding-top: 10px;
    }

    /* 6. WIDGETS */
    .stSlider [data-baseweb="slider"] { background-color: transparent !important; }
    [data-testid="stMetricValue"] { color: #98FF98 !important; font-size: 32px !important; }
    .warning-red { color: #FF3131 !important; font-weight: bold; }

    .stButton > button {
        width: 100%;
        border: 1px solid #98FF98 !important;
        background-color: #111 !important;
        color: #98FF98 !important;
        border-radius: 0px;
        height: 40px;
        font-size: 10px !important;
    }
    
    .tanker-container { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 5px; }
    hr { border: 0; border-top: 1px solid #333; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- SVG ASSETS (FROM USER UPLOADS) ---
TANKER_SVG = """<svg width="100" height="180" viewBox="0 0 101 247" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M100.5 246.5H0.5V173.5L10.5 141.5V110.5L34 50.5L50.5 0.5L67 50.5L90.5 110.5V141.5L100.5 173.5V246.5Z" fill="#8E8E8E"/><path d="M50.5 0.5L34 50.5M50.5 0.5L67 50.5M34 50.5L10.5 110.5V141.5L0.5 173.5V246.5H100.5V173.5L90.5 141.5V110.5L67 50.5M34 50.5H67M10.5 110.5H90.5M10.5 141.5H90.5M0.5 173.5H100.5M20.5 246.5V173.5M80.5 246.5V173.5" stroke="#94FFB4" stroke-width="1"/></svg>"""

HLS_SVG = """<svg width="80" height="180" viewBox="0 0 101 247" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M100.5 246.5H0.5V173.5L10.5 141.5V110.5L34 50.5L50.5 0.5L67 50.5L90.5 110.5V141.5L100.5 173.5V246.5Z" fill="#F2F2F2"/><path d="M50.5 0.5L34 50.5L10.5 110.5V141.5L0.5 173.5V246.5H100.5V173.5L90.5 141.5V110.5L67 50.5L50.5 0.5ZM50.5 0.5L34 50.5M50.5 0.5L67 50.5M10.5 110.5H90.5M10.5 141.5H90.5M0.5 173.5H100.5M20.5 246.5V173.5M80.5 246.5V173.5" stroke="#94FFB4" stroke-width="1"/><rect x="25.5" y="72.5" width="50" height="12" rx="6" fill="#3D3D3D"/><rect x="5.5" y="117.5" width="27" height="16" fill="#3D3D3D"/><rect x="68.5" y="117.5" width="27" height="16" fill="#3D3D3D"/><path d="M78.5 204.5L95.5 246.5H74.5L61.5 204.5H78.5Z" fill="#3D3D3D"/><path d="M22.5 204.5L5.5 246.5H26.5L39.5 204.5H22.5Z" fill="#3D3D3D"/></svg>"""

ORION_SVG = """<svg width="200" height="100" viewBox="0 0 293 103" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M106.5 45.5L133.5 0.5H160.5L187.5 45.5H106.5Z" fill="#8E8E8E"/><path d="M106.5 45.5L133.5 0.5H160.5L187.5 45.5M106.5 45.5H187.5" stroke="#94FFB4" stroke-width="1"/><path d="M115.5 45.5V90.5H178.5V45.5H115.5Z" fill="#F2F2F2"/><path d="M115.5 45.5V90.5H178.5V45.5H115.5Z" stroke="#94FFB4" stroke-width="1"/><rect x="4.5" y="74.5" width="103" height="16" fill="#3D3D3D"/><rect x="186.5" y="74.5" width="103" height="16" fill="#3D3D3D"/><rect x="4.5" y="74.5" width="103" height="16" stroke="#94FFB4" stroke-width="1"/><rect x="186.5" y="74.5" width="103" height="16" stroke="#94FFB4" stroke-width="1"/><path d="M136.5 90.5L131.5 102.5H162.5L157.5 90.5H136.5Z" fill="#3D3D3D"/><path d="M136.5 90.5L131.5 102.5H162.5L157.5 90.5H136.5Z" stroke="#94FFB4" stroke-width="1"/><rect x="107.5" y="80.5" width="8" height="4" fill="#94FFB4"/><rect x="178.5" y="80.5" width="8" height="4" fill="#94FFB4"/><rect x="133.5" y="20.5" width="27" height="6" fill="#3D3D3D" stroke="#94FFB4" stroke-width="1"/></svg>"""

# --- LOGIC ---
if 'selected_mode' not in st.session_state: st.session_state.selected_mode = "MODE 1: NO PUSH"

st.markdown("<h2 style='text-align: center; letter-spacing: 5px; margin-top: 0px;'>HLS MISSION LOGISTICS</h2>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    st.markdown(TANKER_SVG, unsafe_allow_html=True)
    st.write("TANKER CONFIG")
    ref_amt = st.slider("PROP PER REFILL (t)", 50, 200, 100, step=5)
    cadence = st.slider("CADENCE (DAYS)", 1, 31, 7)
    cost_f = st.slider("COST PER FLIGHT ($M)", 1, 500, 100, step=5)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    st.markdown(HLS_SVG, unsafe_allow_html=True)
    st.write("HLS CONFIG")
    dry_m = st.slider("HLS DRY MASS (t)", 80, 250, 120, step=5)
    isp = st.slider("ENGINE ISP (s)", 350, 380, 365)
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
        if active: st.markdown(f"<style>div.stButton > button:first-child:contains('{m}') {{ background-color: #98FF98 !important; color: black !important; font-weight: bold; }}</style>", unsafe_allow_html=True)
        if st.button(f"▶ {m}" if active else m): st.session_state.selected_mode = m; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- MATH ENGINE ---
G = 9.80665; OM = 27.0; CAP = 1500.0
DV = {"LEO_TO_TLI": 3200, "TLI_TO_NRHO": 450, "TLI_TO_LLO": 900, "TLI_TO_PCO": 800, "NRHO_TO_SURFACE": 2750, "LLO_TO_SURFACE": 2000, "PCO_TO_SURFACE": 2400}

def get_tel():
    m = st.session_state.selected_mode; log = []
    # 1. Ascent
    dva = DV[f"{orbit}_TO_SURFACE"]; maf = dry_m; mai = maf * math.exp(dva / (isp * G))
    log.append({"LEG": "ASCENT: SURFACE TO ORBIT", "DV": dva, "WET MASS": f"{mai:.1f}t", "DRY MASS": f"{maf:.1f}t", "VEHICLE": "HLS"})
    # 2. Descent
    dvd = dva; mdf = mai; mdi = mdf * math.exp(dvd / (isp * G))
    log.append({"LEG": "DESCENT: ORBIT TO SURFACE", "DV": dvd, "WET MASS": f"{mdi:.1f}t", "DRY MASS": f"{mdf:.1f}t", "VEHICLE": "HLS"})
    curr = mdi
    # 3. Pushes
    if "MODE 3" in m or "MODE 4" in m:
        dvp = 450 if "NRHO TO LLO" in m else 400 if "PCO TO LLO" in m else 350
        mpf = curr + OM; mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH MANEUVER", "DV": dvp, "WET MASS": f"{mpi:.1f}t", "DRY MASS": f"{mpf:.1f}t", "VEHICLE": "HLS + 27T ORION"})
        curr = mpi - OM
    # 4. TLI Arrival
    dva2 = DV[f"TLI_TO_{orbit}"]; has_o = "MODE 2" in m; ma2f = curr + (OM if has_o else 0); ma2i = ma2f * math.exp(dva2 / (isp * G))
    log.append({"LEG": f"ARRIVAL AT {orbit}", "DV": dva2, "WET MASS": f"{ma2i:.1f}t", "DRY MASS": f"{ma2f:.1f}t", "VEHICLE": f"HLS {'+ 27T ORION' if has_o else ''}"})
    # 5. TLI Departure
    dvl = 3200; mlf = ma2i; mli = mlf * math.exp(dvl / (isp * G))
    log.append({"LEG": "TLI DEPARTURE (LEO)", "DV": dvl, "WET MASS": f"{mli:.1f}t", "DRY MASS": f"{mlf:.1f}t", "VEHICLE": f"HLS {'+ 27T ORION' if has_o else ''}"})
    prop = mli - dry_m - (OM if has_o else 0)
    if "MODE 3" in m or "MODE 4" in m: prop = mli - dry_m
    return prop, log

total_p, t_log = get_tel(); tanks = math.ceil(total_p / ref_amt); cost = tanks * cost_f

# --- RESULTS ---
st.markdown("<h3 style='margin-bottom:-10px;'>RESULTS</h3><hr>", unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
with r1: st.metric("TANKERS", tanks)
with r2: 
    s_c = "warning-red" if total_p > CAP else ""
    st.markdown(f"TOTAL PROPELLANT")
    st.markdown(f"<p class='{s_c}' style='font-size:32px; margin:0;'>{total_p:,.1f} T / {CAP:,.0f} T</p>", unsafe_allow_html=True)
    if total_p > CAP: st.markdown(f"<p class='warning-red' style='font-size:10px;'>MISSION WOULD REQUIRE ADDITIONAL REFILLS IN HIGHER ORBIT, OR AT THE MOON</p>", unsafe_allow_html=True)
with r3: st.metric("REFILL CAMPAIGN LENGTH", f"{tanks * cadence} DAYS")
with r4: st.metric("REFILL CAMPAIGN COST", f"${cost/1000:.2f} B" if cost >= 1000 else f"${cost:,.0f} M")

icons = "".join([f"<div style='display:inline-block; margin-right:4px;'>{TANKER_SVG}</div>" for _ in range(tanks)])
st.markdown(f"<div class='tanker-container'>{icons}</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("▶ VIEW DETAILED TELEMETRY LOG"): st.table(pd.DataFrame(t_log))
