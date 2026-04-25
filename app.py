import streamlit as st
import math
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Mission Console", layout="wide")

# --- VERSION 21: TACTICAL CONSOLE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

    /* 1. REMOVE HEADER/VOIDS */
    [data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
    .main .block-container { padding-top: 0rem !important; margin-top: -60px !important; }

    /* 2. GLOBAL THEME */
    .stApp { background-color: #000000 !important; color: #98FF98 !important; font-family: 'JetBrains Mono', monospace; }
    h1, h2, h3, p, span, label, div { color: #98FF98 !important; text-transform: uppercase; }

    /* 3. TACTICAL PANEL BOXES */
    [data-testid="column"] {
        border: 1px solid #98FF98 !important;
        padding: 25px 15px 15px 15px !important;
        background-color: #050505 !important;
        min-height: 550px !important;
        position: relative;
    }

    /* INSET TITLE FOR BOXES */
    [data-testid="column"]::before {
        content: attr(data-label);
        position: absolute;
        top: -10px;
        left: 15px;
        background: #000;
        padding: 0 5px;
        font-size: 12px;
        letter-spacing: 2px;
        color: #98FF98;
        z-index: 10;
    }

    /* 4. BUTTONS (ACTIVE = MINT, INACTIVE = GREY) */
    .stButton > button {
        width: 100% !important;
        border: 1px solid #98FF98 !important;
        background-color: #1a1a1a !important;
        color: #98FF98 !important;
        border-radius: 0px !important;
        height: 45px !important;
        font-size: 9px !important;
        margin-bottom: 5px !important;
        text-align: center !important;
    }

    /* 5. FIX WHITE DROPDOWN & EXPANDER */
    div[data-baseweb="select"] > div, div[data-baseweb="popover"], div[role="listbox"], ul {
        background-color: #1a1a1a !important;
        color: #98FF98 !important;
        border: 1px solid #98FF98 !important;
    }
    div[data-testid="stExpander"], div[data-testid="stExpanderDetails"] {
        background-color: #000 !important;
        border: 1px solid #98FF98 !important;
        color: #98FF98 !important;
    }
    table { background-color: #000 !important; border: 1px solid #98FF98 !important; width: 100%; }
    th, td { border: 1px solid #333 !important; color: #98FF98 !important; padding: 5px; }

    /* 6. MISC */
    .stSlider [data-baseweb="slider"] { background-color: transparent !important; }
    [data-testid="stMetricValue"] { color: #98FF98 !important; font-size: 32px !important; }
    .warning-red { color: #FF3131 !important; font-weight: bold; }
    hr { border: 0; border-top: 1px solid #333; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'orion_mode' not in st.session_state:
    st.session_state.orion_mode = "NO HLS PUSH"

def set_orion(mode):
    st.session_state.orion_mode = mode

# --- UI CONTENT ---
st.markdown("<h2 style='text-align: center; letter-spacing: 5px; margin-bottom: 20px;'>HLS MISSION LOGISTICS CONSOLE</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# PANEL 1: TANKER
with col1:
    st.markdown("<p style='font-size:12px; margin-bottom:20px;'>STARSHIP REFILL TANKER</p>", unsafe_allow_html=True)
    c1a, c1b = st.columns([1, 2])
    with c1a:
        st.image("tanker.svg", use_container_width=True)
    with c1b:
        ref_amt = st.slider("PROP PER REFILL (T)", 50, 200, 100, step=5)
        cadence = st.slider("CADENCE (DAYS)", 1, 31, 7)
        cost_f = st.slider("COST PER FLIGHT ($M)", 1, 500, 100, step=5)

# PANEL 2: HLS
with col2:
    st.markdown("<p style='font-size:12px; margin-bottom:20px;'>HLS STARSHIP</p>", unsafe_allow_html=True)
    c2a, c2b = st.columns([1, 2])
    with c2a:
        st.image("hls.svg", use_container_width=True)
    with c2b:
        dry_m = st.slider("HLS DRY MASS (T)", 80, 250, 120, step=5)
        isp = st.slider("ENGINE ISP (S)", 350, 380, 365)
        orbit = st.selectbox("STAGING ORBIT", ["NRHO", "LLO", "PCO"])

# PANEL 3: ORION
with col3:
    st.markdown("<p style='font-size:12px; margin-bottom:20px;'>ORION MODE</p>", unsafe_allow_html=True)
    c3a, c3b = st.columns([1, 2.5])
    with c3a:
        st.image("orion.svg", use_container_width=True)
    with c3b:
        modes = [
            "NO HLS PUSH",
            "HLS PUSH FROM LEO TO STAGING ORBIT",
            "HLS PUSH FROM NRHO TO LLO",
            "HLS PUSH FROM NRHO TO PCO",
            "HLS PUSH FROM PCO TO LLO"
        ]
        for m in modes:
            active = st.session_state.orion_mode == m
            # Invert colors for active button
            if active:
                st.markdown(f"<style>div.stButton > button:first-child:contains('{m}') {{ background-color: #98FF98 !important; color: black !important; font-weight: bold; }}</style>", unsafe_allow_html=True)
            st.button(m, key=f"btn_{m}", on_click=set_orion, args=(m,))

# --- MATH (BACKWARD INTEGRATION) ---
G = 9.80665; OM = 27.0; CAP = 1500.0
DV = {"LEO_TO_TLI": 3200, "TLI_TO_NRHO": 450, "TLI_TO_LLO": 900, "TLI_TO_PCO": 800, "NRHO_TO_SURFACE": 2750, "LLO_TO_SURFACE": 2000, "PCO_TO_SURFACE": 2400}

def get_telemetry():
    mode = st.session_state.orion_mode
    log = []
    
    # Leg 1: Ascent (End @ Staging w/ Dry Mass)
    dva = DV[f"{orbit}_TO_SURFACE"]
    maf = dry_m
    mai = maf * math.exp(dva / (isp * G))
    log.append({"LEG": "ASCENT: SURFACE TO ORBIT", "DV": dva, "WET MASS": f"{mai:.1f}T", "DRY MASS": f"{maf:.1f}T", "VEHICLE": "HLS"})

    # Leg 2: Descent (End @ Surface w/ mai)
    dvd = dva
    mdf = mai
    mdi = mdf * math.exp(dvd / (isp * G))
    log.append({"LEG": "DESCENT: ORBIT TO SURFACE", "DV": dvd, "WET MASS": f"{mdi:.1f}T", "DRY MASS": f"{mdf:.1f}T", "VEHICLE": "HLS"})

    curr = mdi
    
    # Leg 3: Pushes
    if "NRHO TO LLO" in mode:
        dvp = 450; mpf = curr + OM; mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH (NRHO->LLO)", "DV": dvp, "WET MASS": f"{mpi:.1f}T", "DRY MASS": f"{mpf:.1f}T", "VEHICLE": "HLS + 27T ORION"}); curr = mpi - OM
    elif "NRHO TO PCO" in mode:
        dvp = 350; mpf = curr + OM; mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH (NRHO->PCO)", "DV": dvp, "WET MASS": f"{mpi:.1f}T", "DRY MASS": f"{mpf:.1f}T", "VEHICLE": "HLS + 27T ORION"}); curr = mpi - OM
    elif "PCO TO LLO" in mode:
        dvp = 400; mpf = curr + OM; mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH (PCO->LLO)", "DV": dvp, "WET MASS": f"{mpi:.1f}T", "DRY MASS": f"{mpf:.1f}T", "VEHICLE": "HLS + 27T ORION"}); curr = mpi - OM

    # Leg 4: TLI Arrival
    dva2 = DV[f"TLI_TO_{orbit}"]; has_o = "LEO TO STAGING" in mode
    ma2f = curr + (OM if has_o else 0)
    ma2i = ma2f * math.exp(dva2 / (isp * G))
    log.append({"LEG": f"ARRIVAL AT {orbit}", "DV": dva2, "WET MASS": f"{ma2i:.1f}T", "DRY MASS": f"{ma2f:.1f}T", "VEHICLE": f"HLS {'+ 27T ORION' if has_o else ''}"})

    # Leg 5: TLI Departure
    dvl = 3200; mlf = ma2i; mli = mlf * math.exp(dvl / (isp * G))
    log.append({"LEG": "TLI DEPARTURE (LEO)", "DV": dvl, "WET MASS": f"{mli:.1f}T", "DRY MASS": f"{mlf:.1f}T", "VEHICLE": f"HLS {'+ 27T ORION' if has_o else ''}"})

    prop = mli - dry_m - (OM if has_o else 0)
    if any(x in mode for x in ["NRHO TO", "PCO TO"]): prop = mli - dry_m
    return prop, log

total_p, t_log = get_telemetry(); tanks = math.ceil(total_p / ref_amt); cost = tanks * cost_f

# --- RESULTS ---
st.markdown("<h3 style='margin-top:20px;'>RESULTS</h3><hr>", unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
with r1: st.metric("TANKERS", tanks)
with r2: 
    s_c = "warning-red" if total_p > CAP else ""
    st.markdown(f"TOTAL PROPELLANT")
    st.markdown(f"<p class='{s_c}' style='font-size:32px; margin:0;'>{total_p:,.1f} T / {CAP:,.0f} T</p>", unsafe_allow_html=True)
    if total_p > CAP: st.markdown(f"<p class='warning-red' style='font-size:10px;'>MISSION WOULD REQUIRE ADDITIONAL REFILLS IN HIGHER ORBIT, OR AT THE MOON</p>", unsafe_allow_html=True)
with r3: st.metric("REFILL CAMPAIGN LENGTH", f"{tanks * cadence} DAYS")
with r4: st.metric("REFILL CAMPAIGN COST", f"${cost/1000:.2f} B" if cost >= 1000 else f"${cost:,.0f} M")

# TANKER FLEET
t_icons = st.columns(15) 
for i in range(min(tanks, 15)):
    with t_icons[i]: st.image("tanker.svg", use_container_width=True)
if tanks > 15: st.write(f"... AND {tanks-15} MORE TANKERS")

st.markdown("<br>", unsafe_allow_html=True)
with st.expander("▶ VIEW DETAILED TELEMETRY LOG (BACKWARD INTEGRATION)"):
    st.table(pd.DataFrame(t_log))
