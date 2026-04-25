import streamlit as st
import math
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Mission Logistics Console", layout="wide")

# --- PURE BLACK & MINT CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

    .stApp {
        background-color: #000000;
        color: #98FF98;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Mint text for all elements */
    h1, h2, h3, p, span, label, div, .stSelectbox, .stSlider, .stRadio {
        color: #98FF98 !important;
        text-transform: uppercase;
    }

    /* Sliders and Metrics */
    .stSlider [data-baseweb="slider"] { background-color: transparent; }
    [data-testid="stMetricValue"] { color: #98FF98 !important; font-size: 32px !important; }

    /* Custom Button Grid - Selected state */
    .stButton > button {
        width: 100%;
        border: 1px solid #98FF98 !important;
        background-color: transparent !important;
        color: #98FF98 !important;
        border-radius: 0px;
        height: 60px;
        font-size: 11px !important;
    }

    .stButton > button:active, .stButton > button:focus {
        background-color: #98FF98 !important;
        color: #000 !important;
    }

    hr { border: 0; border-top: 1px solid #98FF98; margin: 15px 0; }

    /* Tanker visualization */
    .tanker-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        justify-content: flex-start;
        margin-top: 10px;
    }
    
    /* Telemetry Table */
    .telemetry-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }
    .telemetry-table td, .telemetry-table th {
        border: 1px solid #98FF98;
        padding: 8px;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SVG PLACEHOLDERS ---
TANKER_SVG = """<svg width="60" height="90" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg"><path d="M30 5 L15 25 L15 85 L10 95 L50 95 L45 85 L45 25 Z" fill="#C0C0C0" stroke="#98FF98"/><path d="M15 25 L10 22 L10 30 M45 25 L50 22 L50 30 M15 80 L5 85 L15 90 M45 80 L55 85 L45 90" stroke="#98FF98"/></svg>"""
HLS_SVG = """<svg width="80" height="110" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg"><path d="M30 5 L15 30 L15 85 L45 85 L45 30 Z" fill="#FFFFFF" stroke="#98FF98"/><rect x="25" y="15" width="10" height="5" fill="#333"/><line x1="15" y1="85" x2="8" y2="98" stroke="#98FF98" stroke-width="2"/><line x1="45" y1="85" x2="52" y2="98" stroke="#98FF98" stroke-width="2"/></svg>"""
ORION_SVG = """<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><path d="M40 45 L50 25 L60 45 Z" fill="#C0C0C0" stroke="#98FF98"/><rect x="42" y="45" width="16" height="15" fill="#C0C0C0" stroke="#98FF98"/><rect x="5" y="50" width="35" height="4" fill="#555" stroke="#98FF98"/><rect x="60" y="50" width="35" height="4" fill="#555" stroke="#98FF98"/></svg>"""

# --- LOGIC CONSTANTS ---
G = 9.80665
ORION_M = 27.0
DV = {
    "LEO_TO_TLI": 3200, "TLI_TO_NRHO": 450, "TLI_TO_LLO": 900, "TLI_TO_PCO": 800,
    "NRHO_TO_SURFACE": 2750, "LLO_TO_SURFACE": 2000, "PCO_TO_SURFACE": 2400
}

# --- INITIALIZE STATE ---
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = "MODE 1: NO PUSH"

# --- UI INPUTS ---
st.markdown("<h2 style='text-align: center; letter-spacing: 3px;'>HLS MISSION TELEMETRY</h2>", unsafe_allow_html=True)
st.markdown("---")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(TANKER_SVG, unsafe_allow_html=True)
    refill_amount = st.slider("PROP PER REFILL (t)", 50, 200, 100, step=5)
    cadence = st.slider("LAUNCH CADENCE (DAYS)", 1, 31, 7)

with c2:
    st.markdown(HLS_SVG, unsafe_allow_html=True)
    dry_mass = st.slider("HLS DRY MASS (t)", 80, 250, 120, step=5)
    isp = st.slider("ENGINE ISP (s)", 350, 380, 375)
    orbit = st.selectbox("STAGING ORBIT", ["NRHO", "LLO", "PCO"])

with c3:
    st.markdown(ORION_SVG, unsafe_allow_html=True)
    st.write("ORION SELECTION GRID")
    
    # Mode Logic Mapping
    possible_modes = ["MODE 1: NO PUSH", "MODE 2: LEO TO STAGING"]
    if orbit == "LLO":
        possible_modes += ["MODE 3: NRHO TO LLO", "MODE 4: PCO TO LLO"]
    elif orbit == "PCO":
        possible_modes += ["MODE 3: NRHO TO PCO"]

    # Button Grid UI
    grid_cols = st.columns(2)
    for i, mode_name in enumerate(possible_modes):
        with grid_cols[i % 2]:
            if st.button(mode_name):
                st.session_state.selected_mode = mode_name
    
    st.markdown(f"ACTIVE: <span style='color:black; background-color:#98FF98; padding: 2px 8px;'>{st.session_state.selected_mode}</span>", unsafe_allow_html=True)

# --- BACKWARD MATH ENGINE ---
def run_telemetry():
    mode = st.session_state.selected_mode
    mission_log = []

    # 1. Ascent (Ends at Dry Mass)
    dv_ascent = DV[f"{orbit}_TO_SURFACE"]
    m_final_ascent = dry_mass
    m_init_ascent = m_final_ascent * math.exp(dv_ascent / (isp * G))
    mission_log.append({"Leg": "Ascent: Surface to Orbit", "Delta-V": dv_ascent, "Wet Mass": round(m_init_ascent, 1), "Dry Mass": m_final_ascent, "Payload": "HLS Only"})

    # 2. Descent (Ends at m_init_ascent)
    dv_descent = dv_ascent
    m_final_descent = m_init_ascent
    m_init_descent = m_final_descent * math.exp(dv_descent / (isp * G))
    mission_log.append({"Leg": "Descent: Orbit to Surface", "Delta-V": dv_descent, "Wet Mass": round(m_init_descent, 1), "Dry Mass": round(m_final_descent,1), "Payload": "HLS Only"})

    current_m = m_init_descent

    # 3. Intermediate Orion Push
    if "MODE 3" in mode or "MODE 4" in mode:
        dv_push = 450 if "NRHO TO LLO" in mode else 400 if "PCO TO LLO" in mode else 350
        # HLS picks up Orion
        m_final_push = current_m + ORION_M
        m_init_push = m_final_push * math.exp(dv_push / (isp * G))
        mission_log.append({"Leg": "Orion Push (Pick-up)", "Delta-V": dv_push, "Wet Mass": round(m_init_push, 1), "Dry Mass": round(m_final_push, 1), "Payload": "HLS + Orion"})
        # Before pick-up, HLS was solo
        current_m = m_init_push - ORION_M

    # 4. TLI Arrival (Staging Orbit Insertion)
    dv_tli_arr = DV[f"TLI_TO_{orbit}"]
    payload_on_tli = ORION_M if "MODE 2" in mode else 0
    m_final_tli_arr = current_m + payload_on_tli
    m_init_tli_arr = m_final_tli_arr * math.exp(dv_tli_arr / (isp * G))
    mission_log.append({"Leg": f"Arrival at {orbit}", "Delta-V": dv_tli_arr, "Wet Mass": round(m_init_tli_arr, 1), "Dry Mass": round(m_final_tli_arr, 1), "Payload": f"HLS + {payload_on_tli}t Orion"})

    # 5. TLI Departure (LEO to TLI)
    dv_tli_dep = 3200
    m_final_tli_dep = m_init_tli_arr
    m_init_tli_dep = m_final_tli_dep * math.exp(dv_tli_dep / (isp * G))
    mission_log.append({"Leg": "TLI Departure from LEO", "Delta-V": dv_tli_dep, "Wet Mass": round(m_init_tli_dep, 1), "Dry Mass": round(m_final_tli_dep, 1), "Payload": "Trans-Lunar Stack"})

    total_prop = m_init_tli_dep - dry_mass - (ORION_M if "MODE 2" in mode or "MODE 3" in mode or "MODE 4" in mode else 0)
    # Correcting prop calculation: It's simply Wet Mass at LEO - Dry Hardware
    total_prop = m_init_tli_dep - dry_mass - payload_on_tli
    if "MODE 3" in mode or "MODE 4" in mode:
        total_prop = m_init_tli_dep - dry_mass # Since Orion is "dropped" but fuel was used

    return total_prop, mission_log

total_prop, mission_log = run_telemetry()
num_tankers = math.ceil(total_prop / refill_amount)

# --- RESULTS ---
st.markdown("---")
r1, r2, r3 = st.columns(3)
with r1: st.metric("TANKERS", num_tankers)
with r2: st.metric("TOTAL PROP", f"{total_prop:,.1f} T")
with r3: st.metric("MISSION TIME", f"{num_tankers * cadence} DAYS")

# Tanker visualization
tanker_icons = "".join([f"<div style='display:inline-block; padding-right:5px;'>{TANKER_SVG}</div>" for _ in range(num_tankers)])
st.markdown(f"<div class='tanker-container'>{tanker_icons}</div>", unsafe_allow_html=True)

# --- DETAILED READOUT ---
st.markdown("### SUPER DETAILED TELEMETRY (BACKWARD ORDER)")
df = pd.DataFrame(mission_log)
st.table(df)

st.markdown(f"**FINAL CALCULATION:** To deliver the mission, Starship must leave LEO with a total wet mass of **{mission_log[-1]['Wet Mass']} tons**.")
