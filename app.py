import streamlit as st
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Mission Planner 80s", layout="wide")

# --- NEO 80s CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=JetBrains+Mono&display=swap');

    /* Background and global text */
    .stApp {
        background-color: #0a0a0c;
        color: #00f3ff;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Titles */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #ff00ff !important;
        text-shadow: 0 0 10px #ff00ff, 0 0 20px #ff00ff;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Metric boxes */
    [data-testid="stMetricValue"] {
        color: #00f3ff !important;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 5px #00f3ff;
    }

    /* Sliders and Widgets */
    .stSlider [data-baseweb="slider"] {
        background-color: transparent;
    }
    
    /* Custom container for the "NEO" look */
    .neo-container {
        border: 2px solid #00f3ff;
        border-radius: 10px;
        padding: 20px;
        background: rgba(0, 243, 255, 0.05);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
        margin-bottom: 20px;
        text-align: center;
    }

    /* The Tanker visual row */
    .tanker-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VECTOR ART STRINGS (SVG) ---
TANKER_SVG = """<svg width="60" height="100" viewBox="0 0 60 100" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M30 5L10 30V85H50V30L30 5Z" stroke="#ff00ff" stroke-width="2" fill="#ff00ff22"/><path d="M10 70H50M10 40H50" stroke="#ff00ff" stroke-width="1"/></svg>"""
HLS_SVG = """<svg width="60" height="100" viewBox="0 0 60 100" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M30 2L15 25V80H45V25L30 2Z" stroke="#00f3ff" stroke-width="2" fill="#00f3ff22"/><rect x="20" y="80" width="5" height="15" fill="#00f3ff"/><rect x="35" y="80" width="5" height="15" fill="#00f3ff"/><path d="M15 40H45" stroke="#00f3ff" stroke-width="1"/></svg>"""
ORION_SVG = """<svg width="80" height="60" viewBox="0 0 80 60" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M30 40L40 15L50 40H30Z" stroke="#ffffff" stroke-width="2" fill="#ffffff22"/><rect x="10" y="25" width="20" height="5" fill="#ffffff"/><rect x="50" y="25" width="20" height="5" fill="#ffffff"/><path d="M40 40V50" stroke="#ffffff" stroke-width="1"/></svg>"""

# --- CONSTANTS ---
G_CONSTANT = 9.80665
ORION_MASS_T = 27.0
STARSHIP_MAX_PROP_T = 1500.0

DV = {
    "LEO_TO_TLI": 3200, "TLI_TO_NRHO": 450, "TLI_TO_LLO": 900, "TLI_TO_PCO": 800,
    "NRHO_TO_SURFACE": 2750, "LLO_TO_SURFACE": 2000, "PCO_TO_SURFACE": 2400
}

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>HLS Mission Logistics Console</h1>", unsafe_allow_html=True)
st.write("---")

# --- INTERACTIVE UI COLUMNS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='neo-container'>", unsafe_allow_html=True)
    st.markdown(TANKER_SVG, unsafe_allow_html=True)
    st.subheader("Tanker Fleet")
    refill_amount = st.slider("Propellant per Flight (t)", 50, 200, 100)
    cadence = st.slider("Launch Cadence (Days)", 1, 31, 7)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='neo-container'>", unsafe_allow_html=True)
    st.markdown(HLS_SVG, unsafe_allow_html=True)
    st.subheader("HLS Starship")
    dry_mass = st.slider("HLS Dry Mass (t)", 80, 250, 120)
    isp = st.slider("Engine ISP (s)", 350, 380, 375)
    orbit = st.selectbox("Staging Orbit", ["NRHO", "LLO", "PCO"])
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='neo-container'>", unsafe_allow_html=True)
    st.markdown(ORION_SVG, unsafe_allow_html=True)
    st.subheader("Orion / ESM")
    # Logic for restricted LLO option
    options = ["No Push", "LEO to Staging", "Staging to LLO"]
    if orbit == "LLO":
        options = ["LEO to Staging", "Staging to LLO"]
    
    push_mode = st.radio("Mission Mode", options)
    st.markdown("</div>", unsafe_allow_html=True)

# --- MATH LOGIC ---
def run_calculations():
    # Ascent
    dv_land = DV[f"{orbit}_TO_SURFACE"]
    m_final_ascent = dry_mass
    m_initial_ascent = m_final_ascent * math.exp(dv_land / (isp * G_CONSTANT))
    prop_ascent = m_initial_ascent - m_final_ascent

    # Descent
    m_final_descent = m_initial_ascent
    m_initial_descent = m_final_descent * math.exp(dv_land / (isp * G_CONSTANT))
    prop_descent = m_initial_descent - m_final_descent

    # Mid-Mission Push (Staging to LLO)
    prop_push = 0
    m_after_push = m_initial_descent
    if push_mode == "Staging to LLO":
        dv_push = 450 # Approx transfer from High to Low orbit
        m_final_push = m_after_push + ORION_MASS_T
        m_initial_push = m_final_push * math.exp(dv_push / (isp * G_CONSTANT))
        prop_push = m_initial_push - m_final_push
        m_after_push = m_initial_push - ORION_MASS_T

    # LEO to Staging
    dv_departure = DV["LEO_TO_TLI"] + DV[f"TLI_TO_{orbit}"]
    payload_at_departure = ORION_MASS_T if push_mode == "LEO to Staging" else 0
    m_final_leo = m_after_push + payload_at_departure
    m_initial_leo = m_final_leo * math.exp(dv_departure / (isp * G_CONSTANT))
    prop_departure = m_initial_leo - m_final_leo
    
    total_prop = prop_ascent + prop_descent + prop_push + prop_departure
    num_tankers = math.ceil(total_prop / refill_amount)
    total_days = num_tankers * cadence

    return total_prop, num_tankers, total_days, (prop_ascent, prop_descent, prop_push, prop_departure)

total_prop, num_tankers, total_days, breakdowns = run_calculations()

# --- RESULTS DISPLAY ---
st.write("---")
res_col1, res_col2, res_col3 = st.columns(3)

with res_col1:
    st.markdown(f"### Tankers Required")
    st.markdown(f"<h1 style='font-size: 80px; margin:0;'>{num_tankers}</h1>", unsafe_allow_html=True)

with res_col2:
    st.metric("Total Propellant", f"{total_prop:,.1f} Tons")
    st.metric("Campaign Duration", f"{total_days} Days")

with res_col3:
    if total_prop > STARSHIP_MAX_PROP_T:
        st.error(f"CAPACITY EXCEEDED! Starship max is {STARSHIP_MAX_PROP_T}t. Prop required: {total_prop:,.1f}t")
    else:
        st.success("MISSION FEASIBLE: Within capacity.")

# Visual Tanker Count
st.markdown("<div class='tanker-grid'>", unsafe_allow_html=True)
for _ in range(num_tankers):
    st.markdown(TANKER_SVG, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- MATH READOUT ---
with st.expander("📊 TELEMETRY DATA (THE MATH)"):
    st.code(f"""
    1. LUNAR ASCENT:
       Delta-V: {DV[f'{orbit}_TO_SURFACE']} m/s
       Mass: Start {dry_mass}t -> End {breakdowns[0]:.2f}t
    
    2. LUNAR DESCENT:
       Delta-V: {DV[f'{orbit}_TO_SURFACE']} m/s
       Mass: Start {breakdowns[0]:.2f}t -> End {breakdowns[1]+breakdowns[0]:.2f}t
       
    3. ORION PUSH (Transfer):
       Mode: {push_mode}
       Extra Prop: {breakdowns[2]:.2f}t
       
    4. EARTH DEPARTURE (TLI):
       Delta-V: {DV['LEO_TO_TLI'] + DV[f'TLI_TO_{orbit}']} m/s
       Prop Required: {breakdowns[3]:.2f}t
       
    TOTAL PROPELLANT: {total_prop:.2f} metric tons
    REFILLS: {total_prop:.2f} / {refill_amount} = {num_tankers}
    """)
