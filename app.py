import streamlit as st
import math
import pandas as pd
import base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Mission Console", layout="wide")

# --- UTILITY: ICON ENCODER ---
def get_b64(file):
    try:
        with open(file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

t_64 = get_b64("tanker.svg")

# --- THE STABILIZED TACTICAL CSS (VERSION 37) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

    /* 1. TOP GAP REMOVAL */
    [data-testid="stHeader"], [data-testid="stDecoration"], footer { display: none !important; }
    .main .block-container { padding-top: 1rem !important; margin-top: -60px !important; }

    /* 2. GLOBAL THEME */
    .stApp { background-color: #000000 !important; color: #98FF98 !important; font-family: 'JetBrains Mono', monospace; }
    h1, h2, h3, p, span, label, div { color: #98FF98 !important; text-transform: uppercase; }

    /* 3. UNIFIED BOXES (HARD SYMMETRY) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #98FF98 !important;
        background-color: #050505 !important;
        padding: 20px !important;
        min-height: 520px !important; 
        max-height: 520px !important;
        overflow: hidden !important;
        display: flex;
        flex-direction: column;
    }

    /* 4. SHIP ICON EQUALIZER (All Ships Same Scale) */
    [data-testid="stImage"] img {
        height: 180px !important; 
        width: auto !important;
        object-fit: contain;
        margin: 0 auto !important;
        display: block;
    }

    /* 5. TACTICAL SELECTION LIST (ORION) */
    .selected-opt { color: #98FF98 !important; font-weight: bold; font-size: 13px; margin-bottom: 5px; }
    .dim-opt { color: #1e3d1e !important; font-size: 13px; margin-bottom: 5px; }
    
    /* Transparent Selection Buttons */
    .stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: inherit !important;
        text-align: left !important;
        padding: 2px 0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        text-transform: uppercase !important;
        font-size: 13px !important;
        width: 100% !important;
    }
    .stButton > button:hover { color: #98FF98 !important; background-color: rgba(152, 255, 152, 0.05) !important; }

    /* 6. UI HARDENING */
    div[data-baseweb="select"] > div { background-color: #1a1a1a !important; color: #98FF98 !important; border: 1px solid #98FF98 !important; }
    div[role="listbox"], div[data-baseweb="popover"], ul { background-color: #1a1a1a !important; color: #98FF98 !important; border: 1px solid #98FF98 !important; }
    
    table { background-color: #000 !important; border: 1px solid #98FF98 !important; width: 100%; margin-top: 15px; }
    th { background-color: #1a1a1a !important; color: #98FF98 !important; border: 1px solid #98FF98 !important; text-align: left !important; }
    td { border: 1px solid #333 !important; color: #98FF98 !important; padding: 10px !important; }

    /* 7. FLEET GRID */
    .fleet-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 15px; padding: 15px; border: 1px solid #333; background: #050505; }

    /* 8. METRICS & SLIDERS */
    [data-testid="stMetricValue"] { color: #98FF98 !important; font-size: 32px !important; }
    .warning-red { color: #FF3131 !important; font-weight: bold; }
    .stSlider [data-baseweb="slider"] { background-color: transparent !important; }
    hr { border: 0; border-top: 1px solid #333; margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'orion_mode' not in st.session_state:
    st.session_state.orion_mode = "NO HLS PUSH"

def set_mode(m):
    st.session_state.orion_mode = m

# --- UI START ---
st.markdown("<h2 style='text-align: center; letter-spacing: 5px; margin-bottom: 20px;'>HLS MISSION LOGISTICS CONSOLE</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# PANEL 1: TANKER
with col1:
    with st.container(border=True):
        st.markdown("<p style='font-size:12px; font-weight:bold; letter-spacing:2px;'>STARSHIP REFILL TANKER</p>", unsafe_allow_html=True)
        st.image("tanker.svg")
        ref_amt = st.slider("PROP PER REFILL (T)", 50, 200, 100, step=5)
        cadence = st.slider("CADENCE (DAYS)", 1, 31, 7)
        cost_f = st.slider("COST PER FLIGHT ($M)", 1, 500, 100, step=5)

# PANEL 2: HLS
with col2:
    with st.container(border=True):
        st.markdown("<p style='font-size:12px; font-weight:bold; letter-spacing:2px;'>HLS STARSHIP</p>", unsafe_allow_html=True)
        st.image("hls.svg")
        dry_m = st.slider("HLS DRY MASS (T)", 80, 250, 120, step=5)
        isp = st.slider("ENGINE ISP (S)", 350, 380, 365)
        orbit = st.selectbox("STAGING ORBIT", ["NRHO", "LLO", "PCO"])

# PANEL 3: ORION
with col3:
    with st.container(border=True):
        st.markdown("<p style='font-size:12px; font-weight:bold; letter-spacing:2px;'>ORION MODE</p>", unsafe_allow_html=True)
        st.image("orion.svg")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Orbital Logic Gate
        available_modes = ["NO HLS PUSH", "HLS PUSH FROM LEO TO STAGING ORBIT"]
        if orbit == "LLO":
            available_modes += ["HLS PUSH FROM NRHO TO LLO", "HLS PUSH FROM PCO TO LLO"]
        elif orbit == "PCO":
            available_modes += ["HLS PUSH FROM NRHO TO PCO"]
            
        if st.session_state.orion_mode not in available_modes:
            st.session_state.orion_mode = "NO HLS PUSH"

        for m in available_modes:
            is_active = st.session_state.orion_mode == m
            label_text = f"▶ {m}" if is_active else f"  {m}"
            css_class = "selected-opt" if is_active else "dim-opt"
            
            st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
            st.button(label_text, key=f"mode_{m}", on_click=set_mode, args=(m,))
            st.markdown("</div>", unsafe_allow_html=True)

# --- MISSION MATH (VERSION 38 MATH) ---
G = 9.80665; OM = 27.0; CAP = 1500.0
DV = {"LEO_TO_TLI": 3200, "TLI_TO_NRHO": 450, "TLI_TO_LLO": 900, "TLI_TO_PCO": 800, "NRHO_TO_SURFACE": 2750, "LLO_TO_SURFACE": 2000, "PCO_TO_SURFACE": 2400}

def get_log():
    m = st.session_state.orion_mode; log = []
    # 1. Surface Ops
    dva = DV[f"{orbit}_TO_SURFACE"]; maf = dry_m; mai = maf * math.exp(dva / (isp * G))
    log.append({"LEG": "ASCENT: SURFACE TO ORBIT", "DV": dva, "WET MASS": f"{mai:.1f}T", "DRY MASS": f"{maf:.1f}T", "VEHICLE": "HLS"})
    dvd = dva; mdf = mai; mdi = mdf * math.exp(dvd / (isp * G))
    log.append({"LEG": "DESCENT: ORBIT TO SURFACE", "DV": dvd, "WET MASS": f"{mdi:.1f}T", "DRY MASS": f"{mdf:.1f}T", "VEHICLE": "HLS"})
    curr = mdi
    
    # 2. Identify Rendezvous Logic (The Fix)
    arrival_target = orbit
    if "NRHO TO LLO" in m:
        dvp = 450; arrival_target = "NRHO"
        mpf = curr + OM; mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH (NRHO->LLO)", "DV": dvp, "WET MASS": f"{mpi:.1f}T", "DRY MASS": f"{mpf:.1f}T", "VEHICLE": "HLS + 27T ORION"}); curr = mpi - OM
    elif "NRHO TO PCO" in m:
        dvp = 350; arrival_target = "NRHO"
        mpf = curr + OM; mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH (NRHO->PCO)", "DV": dvp, "WET MASS": f"{mpi:.1f}T", "DRY MASS": f"{mpf:.1f}T", "VEHICLE": "HLS + 27T ORION"}); curr = mpi - OM
    elif "PCO TO LLO" in m:
        dvp = 400; arrival_target = "PCO"
        mpf = curr + OM; mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH (PCO->LLO)", "DV": dvp, "WET MASS": f"{mpi:.1f}T", "DRY MASS": f"{mpf:.1f}T", "VEHICLE": "HLS + 27T ORION"}); curr = mpi - OM

    # 3. TLI Arrival (Routes HLS to the correct Rendezvous orbit)
    dva2 = DV[f"TLI_TO_{arrival_target}"]; has_o = "LEO TO STAGING" in m
    ma2f = curr + (OM if has_o else 0); ma2i = ma2f * math.exp(dva2 / (isp * G))
    log.append({"LEG": f"ARRIVAL AT {arrival_target}", "DV": dva2, "WET MASS": f"{ma2i:.1f}T", "DRY MASS": f"{ma2f:.1f}T", "VEHICLE": f"HLS {'+ 27T ORION' if has_o else ''}"})
    
    # 4. TLI Departure (LEO)
    dvl = 3200; mlf = ma2i; mli = mlf * math.exp(dvl / (isp * G))
    log.append({"LEG": "TLI DEPARTURE (LEO)", "DV": dvl, "WET MASS": f"{mli:.1f}T", "DRY MASS": f"{mlf:.1f}T", "VEHICLE": f"HLS {'+ 27T ORION' if has_o else ''}"})
    
    prop = mli - dry_m - (OM if has_o else 0)
    if any(x in m for x in ["NRHO TO", "PCO TO"]): prop = mli - dry_m 
    return prop, log

total_p, t_log = get_log(); tanks = math.ceil(total_p / ref_amt); cost = tanks * cost_f

# --- RESULTS ---
st.markdown("### RESULTS")
st.markdown("<hr>", unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
with r1: st.metric("TANKERS", tanks)
with r2: 
    s_c = "warning-red" if total_p > CAP else ""
    st.markdown(f"TOTAL PROPELLANT")
    st.markdown(f"<p class='{s_c}' style='font-size:32px; margin:0;'>{total_p:,.1f} T / {CAP:,.0f} T</p>", unsafe_allow_html=True)
with r3: st.metric("REFILL CAMPAIGN LENGTH", f"{tanks * cadence} DAYS")
with r4: st.metric("REFILL CAMPAIGN COST", f"${cost/1000:.2f} B" if cost >= 1000 else f"${cost:,.0f} M")

# --- TANKER FLEET ---
st.markdown("### TANKER FLEET")
if t_64:
    fleet_html = "".join([f"<img src='data:image/svg+xml;base64,{t_64}' style='height:60px; margin:5px;'>" for _ in range(tanks)])
    st.markdown(f"<div class='fleet-grid'>{fleet_html}</div>", unsafe_allow_html=True)

# --- DETAILED MISSION READOUT ---
st.markdown("---")
st.markdown("### DETAILED MISSION READOUT")
st.table(pd.DataFrame(t_log))
