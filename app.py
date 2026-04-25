import streamlit as st
import math
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Logistics Terminal", layout="wide")

# --- CUSTOM CSS (MINT & BLACK TERMINAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

    .stApp {
        background-color: #000000;
        color: #98FF98;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Standard Text */
    h1, h2, h3, p, span, label, div, .stSelectbox, .stSlider {
        color: #98FF98 !important;
        text-transform: uppercase;
    }

    /* Alignment Container */
    .input-block {
        min-height: 450px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        border-top: 1px solid #98FF98;
        padding-top: 20px;
    }

    /* Slider Styling */
    .stSlider [data-baseweb="slider"] { background-color: transparent; }
    [data-testid="stMetricValue"] { color: #98FF98 !important; font-size: 38px !important; }

    /* Button Grid Styling */
    .stButton > button {
        width: 100%;
        border: 1px solid #98FF98 !important;
        background-color: #222 !important; /* Grey Unselected */
        color: #98FF98 !important;
        border-radius: 0px;
        height: 50px;
        font-size: 10px !important;
        margin-bottom: 5px;
    }

    /* Horizontal line */
    hr { border: 0; border-top: 1px solid #333; margin: 10px 0; }

    /* Tanker visualization */
    .tanker-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        justify-content: flex-start;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SVG PLACEHOLDERS ---
TANKER_SVG = """<svg width="80" height="100" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg"><path d="M30 5 L15 25 L15 85 L10 95 L50 95 L45 85 L45 25 Z" fill="#777" stroke="#98FF98"/></svg>"""
HLS_SVG = """<svg width="80" height="100" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg"><path d="M30 5 L15 30 L15 85 L45 85 L45 30 Z" fill="#FFF" stroke="#98FF98"/></svg>"""
ORION_SVG = """<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><path d="M40 45 L50 25 L60 45 Z" fill="#777" stroke="#98FF98"/><rect x="5" y="50" width="90" height="4" fill="#333" stroke="#98FF98"/></svg>"""

# --- INITIALIZE STATE ---
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = "MODE 1: NO PUSH"

# --- UI INPUTS ---
st.markdown("<h2 style='text-align: center; letter-spacing: 5px;'>HLS MISSION LOGISTICS</h2>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    st.markdown(TANKER_SVG, unsafe_allow_html=True)
    st.write("TANKER SPECS")
    refill_amount = st.slider("PROP PER REFILL (t)", 50, 200, 100, step=5)
    cadence = st.slider("CADENCE (DAYS)", 1, 31, 7)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    st.markdown(HLS_SVG, unsafe_allow_html=True)
    st.write("HLS SPECS")
    dry_mass = st.slider("HLS DRY MASS (t)", 80, 250, 120, step=5)
    isp = st.slider("ENGINE ISP (s)", 350, 380, 375)
    orbit = st.selectbox("STAGING ORBIT", ["NRHO", "LLO", "PCO"])
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    st.markdown(ORION_SVG, unsafe_allow_html=True)
    st.write("ORION MISSION MODE")
    
    # Mode Logic Mapping
    possible_modes = ["MODE 1: NO PUSH", "MODE 2: LEO TO STAGING"]
    if orbit == "LLO":
        possible_modes += ["MODE 3: NRHO TO LLO", "MODE 4: PCO TO LLO"]
    elif orbit == "PCO":
        possible_modes += ["MODE 3: NRHO TO PCO"]

    # Button Grid UI
    for mode_name in possible_modes:
        # Check if this is the active mode
        is_active = st.session_state.selected_mode == mode_name
        btn_label = f"▶ {mode_name}" if is_active else mode_name
        
        # Inject custom color for active button
        if is_active:
            st.markdown(f"<style>div.stButton > button:first-child:contains('{mode_name}') {{ background-color: #98FF98 !important; color: black !important; }}</style>", unsafe_allow_html=True)

        if st.button(btn_label):
            st.session_state.selected_mode = mode_name
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- BACKWARD MATH ENGINE ---
G = 9.80665
ORION_M = 27.0
DV = {
    "LEO_TO_TLI": 3200, "TLI_TO_NRHO": 450, "TLI_TO_LLO": 900, "TLI_TO_PCO": 800,
    "NRHO_TO_SURFACE": 2750, "LLO_TO_SURFACE": 2000, "PCO_TO_SURFACE": 2400
}

def run_telemetry():
    mode = st.session_state.selected_mode
    mission_log = []

    # 1. Ascent (Ends at Dry Mass)
    dv_ascent = DV[f"{orbit}_TO_SURFACE"]
    m_final_ascent = dry_mass
    m_init_ascent = m_final_ascent * math.exp(dv_ascent / (isp * G))
    mission_log.append({"LEG": "ASCENT: SURFACE TO ORBIT", "DV (m/s)": dv_ascent, "WET MASS": f"{m_init_ascent:.1f}t", "DRY MASS": f"{m_final_ascent:.1f}t", "VEHICLE": "HLS"})

    # 2. Descent (Ends at m_init_ascent)
    dv_descent = dv_ascent
    m_final_descent = m_init_ascent
    m_init_descent = m_final_descent * math.exp(dv_descent / (isp * G))
    mission_log.append({"LEG": "DESCENT: ORBIT TO SURFACE", "DV (m/s)": dv_descent, "WET MASS": f"{m_init_descent:.1f}t", "DRY MASS": f"{m_final_descent:.1f}t", "VEHICLE": "HLS"})

    current_m = m_init_descent

    # 3. Intermediate Orion Push
    if "MODE 3" in mode or "MODE 4" in mode:
        dv_push = 450 if "NRHO TO LLO" in mode else 400 if "PCO TO LLO" in mode else 350
        m_final_push = current_m + ORION_M
        m_init_push = m_final_push * math.exp(dv_push / (isp * G))
        mission_log.append({"LEG": "ORION PUSH (MANEUVER)", "DV (m/s)": dv_push, "WET MASS": f"{m_init_push:.1f}t", "DRY MASS": f"{m_final_push:.1f}t", "VEHICLE": "HLS + 27t ORION"})
        current_m = m_init_push - ORION_M

    # 4. TLI Arrival
    dv_tli_arr = DV[f"TLI_TO_{orbit}"]
    has_orion_tli = "MODE 2" in mode
    m_final_tli_arr = current_m + (ORION_M if has_orion_tli else 0)
    m_init_tli_arr = m_final_tli_arr * math.exp(dv_tli_arr / (isp * G))
    mission_log.append({"LEG": f"ARRIVAL AT {orbit}", "DV (m/s)": dv_tli_arr, "WET MASS": f"{m_init_tli_arr:.1f}t", "DRY MASS": f"{m_final_tli_arr:.1f}t", "VEHICLE": f"HLS {'+ 27t ORION' if has_orion_tli else ''}"})

    # 5. TLI Departure
    dv_tli_dep = 3200
    m_final_tli_dep = m_init_tli_arr
    m_init_tli_dep = m_final_tli_dep * math.exp(dv_tli_dep / (isp * G))
    mission_log.append({"LEG": "TLI DEPARTURE (LEO)", "DV (m/s)": dv_tli_dep, "WET MASS": f"{m_init_tli_dep:.1f}t", "DRY MASS": f"{m_final_tli_dep:.1f}t", "VEHICLE": f"HLS {'+ 27t ORION' if has_orion_tli else ''}"})

    # Propellant is Wet Mass at start minus final dry HLS and any Orion mass left at TLI arrival
    total_prop = m_init_tli_dep - dry_mass - (ORION_M if has_orion_tli else 0)
    if "MODE 3" in mode or "MODE 4" in mode:
        total_prop = m_init_tli_dep - dry_mass

    return total_prop, mission_log

total_prop, mission_log = run_telemetry()
num_tankers = math.ceil(total_prop / refill_amount)

# --- RESULTS SECTION ---
st.markdown("---")
r1, r2, r3 = st.columns(3)
with r1: st.metric("TANKERS", num_tankers)
with r2: st.metric("TOTAL PROPELLANT", f"{total_prop:,.1f} T")
with r3: st.metric("MISSION DURATION", f"{num_tankers * cadence} DAYS")

# Tanker Visualization
tanker_icons = "".join([f"<div style='display:inline-block; margin-right:5px;'>{TANKER_SVG}</div>" for _ in range(num_tankers)])
st.markdown(f"<div class='tanker-container'>{tanker_icons}</div>", unsafe_allow_html=True)

# --- DETAILED READOUT (EXPANDER) ---
st.markdown("---")
with st.expander("▶ VIEW DETAILED TELEMETRY LOG (BACKWARD INTEGRATION)"):
    df = pd.DataFrame(mission_log)
    # Reverse to show backward flow logic or leave as is? Let's leave as is to show "End-to-Start" path.
    st.table(df)
    st.info("NOTE: TELEMETRY IS CALCULATED BACKWARD FROM LUNAR ASCENT TO LEO DEPARTURE.")
