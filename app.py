import streamlit as st
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Logistics Tool", layout="wide")

# --- CLEAN MINT CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

    .stApp {
        background-color: #0f1110;
        color: #98FF98;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Mint borders and text */
    h1, h2, h3, p, span, label {
        color: #98FF98 !important;
        text-transform: uppercase;
    }

    .stSlider [data-baseweb="slider"] {
        background-color: transparent;
    }

    .mint-border {
        border: 1px solid #98FF98;
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 10px;
        background: rgba(152, 255, 152, 0.02);
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #98FF98 !important;
    }

    /* Grid for tankers */
    .tanker-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        justify-content: flex-start;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SVG ASSETS ---
TANKER_SVG = """<svg width="80" height="120" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg">
    <path d="M30 5 L15 25 L15 85 L10 95 L50 95 L45 85 L45 25 Z" fill="#C0C0C0" stroke="#98FF98" stroke-width="1"/>
    <path d="M15 25 L10 22 L10 30 Z M45 25 L50 22 L50 30 Z" fill="#C0C0C0" stroke="#98FF98"/>
    <path d="M15 80 L5 85 L5 95 L15 90 Z M45 80 L55 85 L55 95 L45 90 Z" fill="#C0C0C0" stroke="#98FF98"/>
</svg>"""

HLS_SVG = """<svg width="80" height="120" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg">
    <path d="M30 5 L15 30 L15 85 L45 85 L45 30 Z" fill="#FFFFFF" stroke="#98FF98" stroke-width="1"/>
    <rect x="25" y="15" width="10" height="5" fill="#333"/>
    <line x1="15" y1="85" x2="10" y2="98" stroke="#98FF98" stroke-width="2"/>
    <line x1="45" y1="85" x2="50" y2="98" stroke="#98FF98" stroke-width="2"/>
</svg>"""

ORION_SVG = """<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <path d="M40 45 L50 25 L60 45 Z" fill="#C0C0C0" stroke="#98FF98" stroke-width="1"/>
    <rect x="42" y="45" width="16" height="15" fill="#C0C0C0" stroke="#98FF98"/>
    <rect x="10" y="50" width="32" height="4" fill="#555" stroke="#98FF98"/>
    <rect x="58" y="50" width="32" height="4" fill="#555" stroke="#98FF98"/>
    <path d="M45 60 L35 75 M55 60 L65 75" stroke="#98FF98" stroke-width="2"/>
</svg>"""

# --- INPUTS ---
st.markdown("<h2 style='text-align: center;'>HLS REFILL CALCULATOR</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='mint-border'>", unsafe_allow_html=True)
    st.markdown(TANKER_SVG, unsafe_allow_html=True)
    refill_amount = st.slider("PROP PER REFILL (t)", 50, 200, 100)
    cadence = st.slider("CADENCE (DAYS)", 1, 31, 7)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='mint-border'>", unsafe_allow_html=True)
    st.markdown(HLS_SVG, unsafe_allow_html=True)
    dry_mass = st.slider("DRY MASS (t)", 80, 250, 120)
    isp = st.slider("ISP (s)", 350, 380, 375)
    orbit = st.selectbox("STAGING ORBIT", ["NRHO", "LLO", "PCO"])
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='mint-border'>", unsafe_allow_html=True)
    st.markdown(ORION_SVG, unsafe_allow_html=True)
    push_options = ["No Push", "Push LEO to Staging", "Push Staging to LLO"]
    if orbit == "LLO": push_options = ["Push LEO to Staging", "Push Staging to LLO"]
    push_mode = st.radio("ORION MODE", push_options)
    st.markdown("</div>", unsafe_allow_html=True)

# --- MATH CORE ---
G = 9.80665
ORION_M = 27.0
DV = {
    "LEO_TO_TLI": 3200, "TLI_TO_NRHO": 450, "TLI_TO_LLO": 900, "TLI_TO_PCO": 800,
    "NRHO_TO_SURFACE": 2750, "LLO_TO_SURFACE": 2000, "PCO_TO_SURFACE": 2400
}

def calculate():
    # 1. Ascent: Ends at Dry Mass
    dv_ascent = DV[f"{orbit}_TO_SURFACE"]
    m_final_ascent = dry_mass
    m_init_ascent = m_final_ascent * math.exp(dv_ascent / (isp * G))
    
    # 2. Descent: Ends at m_init_ascent
    dv_descent = dv_ascent
    m_final_descent = m_init_ascent
    m_init_descent = m_final_descent * math.exp(dv_descent / (isp * G))
    
    # 3. Orion Push (Staging to LLO)
    m_before_push_leg = m_init_descent
    if push_mode == "Push Staging to LLO":
        dv_transfer = 450
        m_final_push = m_before_push_leg + ORION_M
        m_init_push = m_final_push * math.exp(dv_transfer / (isp * G))
        # Mass after push leg is finished and Orion is dropped
        m_before_push_leg = m_init_push - ORION_M

    # 4. TLI / Departure
    dv_tli = 3200 + DV[f"TLI_TO_{orbit}"]
    orion_on_tli = ORION_M if push_mode == "Push LEO to Staging" else 0
    m_final_tli = m_before_push_leg + orion_on_tli
    m_init_tli = m_final_tli * math.exp(dv_tli / (isp * G))
    
    # Propellant is Total Initial Mass minus the payload we don't refill (Dry Mass + Orion)
    total_prop = m_init_tli - dry_mass - orion_on_tli
    if push_mode == "Push Staging to LLO":
        # We also need to subtract the orion mass from the final calculation here
        total_prop = m_init_tli - dry_mass
        if push_mode != "Push LEO to Staging": total_prop -= 0 # logic check
        
    num_tankers = math.ceil(total_prop / refill_amount)
    return total_prop, num_tankers, (m_init_tli, m_init_descent, m_init_ascent)

total_prop, num_tankers, stages = calculate()

# --- RESULTS ---
st.markdown("<div class='mint-border'>", unsafe_allow_html=True)
r_col1, r_col2, r_col3 = st.columns(3)
with r_col1:
    st.metric("TANKERS", num_tankers)
with r_col2:
    st.metric("TOTAL PROP", f"{total_prop:,.1f} t")
with r_col3:
    st.metric("TOTAL DAYS", num_tankers * cadence)

# Tanker visualization
tanker_html = "".join([f"<div style='display:inline-block;'>{TANKER_SVG}</div>" for _ in range(num_tankers)])
st.markdown(f"<div class='tanker-container'>{tanker_html}</div>", unsafe_allow_html=True)

# Math Readout
st.markdown("### MISSION LOG (BACKWARD INTEGRATION)")
st.text(f"""
[1] TLI DEPARTURE: Start Mass {stages[0]:.1f}t (Includes Prop + HLS + Orion if selected)
[2] LUNAR ARRIVAL: HLS Mass {stages[1]:.1f}t (Post-TLI, Pre-Descent)
[3] LUNAR SURFACE: HLS Mass {stages[2]:.1f}t (Ready for Ascent)
[4] MISSION END:   HLS Dry Mass {dry_mass:.1f}t (Docked in {orbit})
""")
st.markdown("</div>", unsafe_allow_html=True)
