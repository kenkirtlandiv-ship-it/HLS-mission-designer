import streamlit as st
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Logistics Tool", layout="wide")

# --- MINT TERMINAL CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

    .stApp {
        background-color: #0d0f0e;
        color: #98FF98;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Set all UI text to Mint */
    h1, h2, h3, p, span, label, .stSelectbox, .stSlider, .stRadio {
        color: #98FF98 !important;
        text-transform: uppercase;
    }

    /* Minimalist horizontal rule */
    hr {
        border: 0;
        border-top: 1px solid #98FF98;
        margin: 20px 0;
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #98FF98 !important;
    }

    .tanker-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: flex-start;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SVG PLACEHOLDERS (Replace these with your code) ---
TANKER_SVG = """<svg width="100" height="150" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg"><path d="M30 5 L15 25 L15 85 L10 95 L50 95 L45 85 L45 25 Z" fill="#C0C0C0" stroke="#98FF98"/><path d="M15 25 L10 22 L10 30 M45 25 L50 22 L50 30 M15 80 L5 85 L15 90 M45 80 L55 85 L45 90" stroke="#98FF98"/></svg>"""
HLS_SVG = """<svg width="100" height="150" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg"><path d="M30 5 L15 30 L15 85 L45 85 L45 30 Z" fill="#FFFFFF" stroke="#98FF98"/><rect x="25" y="15" width="10" height="5" fill="#333"/><line x1="15" y1="85" x2="8" y2="98" stroke="#98FF98" stroke-width="2"/><line x1="45" y1="85" x2="52" y2="98" stroke="#98FF98" stroke-width="2"/></svg>"""
ORION_SVG = """<svg width="120" height="120" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><path d="M40 45 L50 25 L60 45 Z" fill="#C0C0C0" stroke="#98FF98"/><rect x="42" y="45" width="16" height="15" fill="#C0C0C0" stroke="#98FF98"/><rect x="5" y="50" width="35" height="4" fill="#555" stroke="#98FF98"/><rect x="60" y="50" width="35" height="4" fill="#555" stroke="#98FF98"/></svg>"""

# --- INPUT SECTION ---
st.markdown("<h2 style='text-align: center; letter-spacing: 5px;'>HLS MISSION LOGISTICS</h2>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(TANKER_SVG, unsafe_allow_html=True)
    refill_amount = st.slider("PROP PER REFILL (t)", 50, 200, 100)
    cadence = st.slider("LAUNCH CADENCE (DAYS)", 1, 31, 7)

with col2:
    st.markdown(HLS_SVG, unsafe_allow_html=True)
    dry_mass = st.slider("HLS DRY MASS (t)", 80, 250, 120)
    isp = st.slider("ENGINE ISP (s)", 350, 380, 375)
    orbit = st.selectbox("STAGING ORBIT", ["NRHO", "LLO", "PCO"])

with col3:
    st.markdown(ORION_SVG, unsafe_allow_html=True)
    # Filter modes based on Orbit selection
    modes = ["Mode 1: No Push", "Mode 2: HLS Push LEO to Staging"]
    if orbit == "LLO":
        modes.append("Mode 3: HLS Push from NRHO to Staging")
        modes.append("Mode 4: HLS Push from PCO to Staging")
    
    push_mode = st.radio("ORION MISSION MODE", modes)

# --- CALCULATION ENGINE (BACKWARD) ---
G = 9.80665
ORION_M = 27.0
DV = {
    "LEO_TO_TLI": 3200, "TLI_TO_NRHO": 450, "TLI_TO_LLO": 900, "TLI_TO_PCO": 800,
    "NRHO_TO_SURFACE": 2750, "LLO_TO_SURFACE": 2000, "PCO_TO_SURFACE": 2400
}

def calculate():
    # 1. Ascent Phase: Ends at Staging Orbit with Dry Mass
    dv_ascent = DV[f"{orbit}_TO_SURFACE"]
    m_final_ascent = dry_mass
    m_init_ascent = m_final_ascent * math.exp(dv_ascent / (isp * G))
    
    # 2. Descent Phase: Ends at Surface with m_init_ascent
    dv_descent = dv_ascent
    m_final_descent = m_init_ascent
    m_init_descent = m_final_descent * math.exp(dv_descent / (isp * G))
    
    m_current = m_init_descent
    
    # 3. Intermediate Orion Push (Modes 3 & 4)
    # Only applicable if Staging Orbit is LLO
    if push_mode == "Mode 3: HLS Push from NRHO to Staging":
        dv_push = 450 # Transfer NRHO to LLO
        m_final_push = m_current + ORION_M
        m_init_push = m_final_push * math.exp(dv_push / (isp * G))
        m_current = m_init_push - ORION_M # Drop Orion at LLO, HLS mass remains
    elif push_mode == "Mode 4: HLS Push from PCO to Staging":
        dv_push = 400 # Transfer PCO to LLO estimate
        m_final_push = m_current + ORION_M
        m_init_push = m_final_push * math.exp(dv_push / (isp * G))
        m_current = m_init_push - ORION_M

    # 4. LEO to Staging Orbit
    dv_tli_arrival = 3200 + DV[f"TLI_TO_{orbit}"]
    
    # Add Orion mass for the entire Earth-to-Moon leg if Mode 2
    payload_on_tli = ORION_M if "Mode 2" in push_mode else 0
    
    m_final_tli = m_current + payload_on_tli
    m_init_tli = m_final_tli * math.exp(dv_tli_arrival / (isp * G))
    
    # Final Propellant = Initial Mass at LEO minus the hardware we didn't "bring" as fuel
    # (The dry mass of HLS and Orion if we pushed it)
    total_prop = m_init_tli - dry_mass - payload_on_tli
    
    # Adjust for Mode 3/4 where Orion was picked up mid-way
    if "Mode 3" in push_mode or "Mode 4" in push_mode:
        # Initial mass at LEO included the fuel to pick up Orion, 
        # but we subtract the dry mass at the end.
        total_prop = m_init_tli - dry_mass

    num_tankers = math.ceil(total_prop / refill_amount)
    return total_prop, num_tankers, m_init_tli

total_prop, num_tankers, leo_mass = calculate()

# --- RESULTS SECTION ---
st.markdown("---")
res_col1, res_col2, res_col3 = st.columns(3)

with res_col1:
    st.metric("TANKERS REQUIRED", num_tankers)
with res_col2:
    st.metric("TOTAL PROPELLANT", f"{total_prop:,.1f} T")
with res_col3:
    st.metric("MISSION DURATION", f"{num_tankers * cadence} DAYS")

# Horizontal Tanker Row
tanker_icons = "".join([f"<div style='display:inline-block;'>{TANKER_SVG}</div>" for _ in range(num_tankers)])
st.markdown(f"<div class='tanker-container'>{tanker_icons}</div>", unsafe_allow_html=True)

# Math Readout
st.markdown("---")
with st.expander("VIEW TELEMETRY (MATH READOUT)"):
    st.text(f"""
    MISSION STAGING: {orbit}
    TARGET ORION MODE: {push_mode}
    
    [STATION 1] LEO DEPARTURE
    Total Mass: {leo_mass:.1f} t
    
    [STATION 2] LUNAR ARRIVAL
    HLS Mass: {(leo_mass * math.exp(-(3200 + DV[f'TLI_TO_{orbit}']) / (isp * G))):.1f} t
    
    [STATION 3] LUNAR SURFACE
    HLS Mass: {(dry_mass * math.exp(DV[f'{orbit}_TO_SURFACE'] / (isp * G))):.1f} t
    
    [STATION 4] MISSION COMPLETE
    Final HLS Mass: {dry_mass:.1f} t
    """)
