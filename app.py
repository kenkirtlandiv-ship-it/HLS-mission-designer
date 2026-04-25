import streamlit as st
import math
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Mission Console", layout="wide")

# --- THE "HARDENED" CSS: BOXES, BUTTONS, AND DARKNESS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

    /* 1. REMOVE GHOST VOID AND HEADER */
    [data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
    .main .block-container { padding-top: 0rem !important; margin-top: -30px !important; }

    /* 2. GLOBAL COLORS */
    .stApp { background-color: #000000 !important; color: #98FF98 !important; font-family: 'JetBrains Mono', monospace; }
    h1, h2, h3, p, span, label, div { color: #98FF98 !important; text-transform: uppercase; }

    /* 3. TACTICAL PANEL STYLING (Targeting Streamlit Columns) */
    [data-testid="column"] {
        border: 1px solid #98FF98;
        padding: 15px !important;
        background-color: #050505;
        min-height: 520px;
    }

    /* 4. BUTTONS: MINT ON SELECTION, GREY OTHERWISE */
    .stButton > button {
        width: 100% !important;
        border: 1px solid #98FF98 !important;
        background-color: #1a1a1a !important;
        color: #98FF98 !important;
        border-radius: 0px !important;
        height: 50px !important;
        font-size: 10px !important;
        margin-bottom: 5px !important;
    }

    /* 5. FORCE DARK DROPDOWNS & EXPANDERS */
    div[data-baseweb="select"] > div, div[data-baseweb="popover"], div[role="listbox"], ul {
        background-color: #1a1a1a !important;
        color: #98FF98 !important;
        border: 1px solid #98FF98 !important;
    }
    div[data-testid="stExpander"], div[data-testid="stExpanderDetails"] {
        background-color: #000 !important;
        border: 1px solid #98FF98 !important;
        color: #98FF98 !important;
        border-radius: 0px !important;
    }

    /* 6. RESULTS & TABLE */
    table { background-color: #000 !important; border: 1px solid #98FF98 !important; width: 100%; }
    th, td { border: 1px solid #333 !important; color: #98FF98 !important; padding: 8px; }
    [data-testid="stMetricValue"] { color: #98FF98 !important; font-size: 32px !important; }
    .warning-red { color: #FF3131 !important; font-weight: bold; }
    
    .stSlider [data-baseweb="slider"] { background-color: transparent !important; }
    hr { border: 0; border-top: 1px solid #333; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT FOR ORION BUTTONS ---
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = "No HLS Push"

def update_mode(mode_name):
    st.session_state.selected_mode = mode_name

# --- INTERFACE ---
st.markdown("<h2 style='text-align: center; letter-spacing: 5px; margin-bottom: 20px;'>HLS MISSION LOGISTICS CONSOLE</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# PANEL 1: TANKER
with col1:
    st.markdown("<h3 style='font-size:14px;'>STARSHIP REFILL TANKER</h3>", unsafe_allow_html=True)
    inner_c1, inner_c2 = st.columns([1, 2])
    with inner_c1:
        st.image("tanker.svg", use_container_width=True)
    with inner_c2:
        ref_amt = st.slider("PROP PER REFILL (T)", 50, 200, 100, step=5)
        cadence = st.slider("CADENCE (DAYS)", 1, 31, 7)
        cost_f = st.slider("COST PER FLIGHT ($M)", 1, 500, 100, step=5)

# PANEL 2: HLS
with col2:
    st.markdown("<h3 style='font-size:14px;'>HLS STARSHIP</h3>", unsafe_allow_html=True)
    inner_c3, inner_c4 = st.columns([1, 2])
    with inner_c3:
        st.image("hls.svg", use_container_width=True)
    with inner_c4:
        dry_m = st.slider("HLS DRY MASS (T)", 80, 250, 120, step=5)
        isp = st.slider("ENGINE ISP (S)", 350, 380, 365)
        orbit = st.selectbox("STAGING ORBIT", ["NRHO", "LLO", "PCO"])

# PANEL 3: ORION
with col3:
    st.markdown("<h3 style='font-size:14px;'>ORION MODE</h3>", unsafe_allow_html=True)
    inner_c5, inner_c6 = st.columns([1, 2])
    with inner_c5:
        st.image("orion.svg", use_container_width=True)
    with inner_c6:
        modes = [
            "No HLS Push", 
            "HLS Push from LEO to Staging Orbit",
            "HLS Push from NRHO to LLO", 
            "HLS Push from NRHO to PCO", 
            "HLS Push from PCO to LLO"
        ]
        for m in modes:
            is_active = st.session_state.selected_mode == m
            # Visual highlight for the active button
            if is_active:
                st.markdown(f"<style>div.stButton > button:first-child:contains('{m}') {{ background-color: #98FF98 !important; color: black !important; }}</style>", unsafe_allow_html=True)
            
            st.button(m, key=f"btn_{m}", on_click=update_mode, args=(m,))

# --- MATH (BACKWARD INTEGRATION) ---
G = 9.80665; OM = 27.0; CAP = 1500.0
DV = {"LEO_TO_TLI": 3200, "TLI_TO_NRHO": 450, "TLI_TO_LLO": 900, "TLI_TO_PCO": 800, "NRHO_TO_SURFACE": 2750, "LLO_TO_SURFACE": 2000, "PCO_TO_SURFACE": 2400}

def get_tel():
    m = st.session_state.selected_mode; log = []
    # Surface Ascent
    dva = DV[f"{orbit}_TO_SURFACE"]; maf = dry_m; mai = maf * math.exp(dva / (isp * G))
    log.append({"LEG": "ASCENT: SURFACE TO ORBIT", "DV": dva, "WET MASS": f"{mai:.1f}T", "DRY MASS": f"{maf:.1f}T", "VEHICLE": "HLS"})
    # Surface Descent
    dvd = dva; mdf = mai; mdi = mdf * math.exp(dvd / (isp * G))
    log.append({"LEG": "DESCENT: ORBIT TO SURFACE", "DV": dvd, "WET MASS": f"{mdi:.1f}T", "DRY MASS": f"{mdf:.1f}T", "VEHICLE": "HLS"})
    curr = mdi
    # Pushes
    if "NRHO TO LLO" in m:
        dvp = 450; mpf = curr + OM; mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH (NRHO->LLO)", "DV": dvp, "WET MASS": f"{mpi:.1f}T", "DRY MASS": f"{mpf:.1f}T", "VEHICLE": "HLS + ORION"}); curr = mpi - OM
    elif "NRHO TO PCO" in m:
        dvp = 350; mpf = curr + OM; mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH (NRHO->PCO)", "DV": dvp, "WET MASS": f"{mpi:.1f}T", "DRY MASS": f"{mpf:.1f}T", "VEHICLE": "HLS + ORION"}); curr = mpi - OM
    elif "PCO TO LLO" in m:
        dvp = 400; mpf = curr + OM; mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH (PCO->LLO)", "DV": dvp, "WET MASS": f"{mpi:.1f}T", "DRY MASS": f"{mpf:.1f}T", "VEHICLE": "HLS + ORION"}); curr = mpi - OM
    # TLI Arrival
    dva2 = DV[f"TLI_TO_{orbit}"]; has_o = "LEO to Staging" in m
    ma2f = curr + (OM if has_o else 0); ma2i = ma2f * math.exp(dva2 / (isp * G))
    log.append({"LEG": f"ARRIVAL AT {orbit}", "DV": dva2, "WET MASS": f"{ma2i:.1f}T", "DRY MASS": f"{ma2f:.1f}T", "VEHICLE": f"HLS {'+ ORION' if has_o else ''}"})
    # LEO Departure
    dvl = 3200; mlf = ma2i; mli = mlf * math.exp(dvl / (isp * G))
    log.append({"LEG": "TLI DEPARTURE (LEO)", "DV": dvl, "WET MASS": f"{mli:.1f}T", "DRY MASS": f"{mlf:.1f}T", "VEHICLE": f"HLS {'+ ORION' if has_o else ''}"})
    prop = mli - dry_m - (OM if has_o else 0)
    if any(x in m for x in ["NRHO TO", "PCO TO"]): prop = mli - dry_m
    return prop, log

total_p, t_log = get_tel(); tanks = math.ceil(total_p / ref_amt); cost = tanks * cost_f

# --- RESULTS ---
st.markdown("<h3 style='margin-bottom:0px; margin-top:20px;'>RESULTS</h3><hr>", unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
with r1: st.metric("TANKERS", tanks)
with r2: 
    s_c = "warning-red" if total_p > CAP else ""
    st.markdown(f"TOTAL PROPELLANT")
    st.markdown(f"<p class='{s_c}' style='font-size:32px; margin:0;'>{total_p:,.1f} T / {CAP:,.0f} T</p>", unsafe_allow_html=True)
    if total_p > CAP: st.markdown(f"<p class='warning-red' style='font-size:10px;'>MISSION WOULD REQUIRE ADDITIONAL REFILLS IN HIGHER ORBIT, OR AT THE MOON</p>", unsafe_allow_html=True)
with r3: st.metric("REFILL CAMPAIGN LENGTH", f"{tanks * cadence} DAYS")
with r4: st.metric("REFILL CAMPAIGN COST", f"${cost/1000:.2f} B" if cost >= 1000 else f"${cost:,.0f} M")

# TANKER FLEET (Vertical Icons)
t_icons = st.columns(15) 
for i in range(min(tanks, 15)):
    with t_icons[i]: st.image("tanker.svg", use_container_width=True)
if tanks > 15: st.write(f"... AND {tanks-15} MORE TANKERS")

st.markdown("<br>", unsafe_allow_html=True)
with st.expander("▶ VIEW DETAILED TELEMETRY LOG (BACKWARD INTEGRATION)"):
    st.table(pd.DataFrame(t_log))
