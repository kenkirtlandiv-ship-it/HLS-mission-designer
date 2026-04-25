import streamlit as st
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Starship HLS Refill Calculator", layout="centered")

st.title("🚀 Starship HLS Lunar Mission Calculator")
st.markdown("Calculate how many propellant refills are needed based on mission architecture.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Starship Variables")
dry_mass_t = st.sidebar.slider("HLS Dry Mass (Metric Tons)", 80, 200, 120)
isp = st.sidebar.slider("Vacuum ISP (seconds)", 350, 380, 375)
refill_capacity_t = st.sidebar.slider("Refill Amount per Tanker (Tons)", 50, 200, 100)

st.sidebar.header("Mission Architecture")
staging_orbit = st.sidebar.selectbox("Staging Orbit", ["NRHO", "LLO", "PCO"])

# Orion Push Logic
push_options = ["HLS does not push Orion", "HLS pushes Orion (Transfer only)", "HLS pushes Orion (From LEO)"]
# Constraint: Scenario 1 (No push) not allowed for LLO
if staging_orbit == "LLO":
    push_options = ["HLS pushes Orion (Transfer only)", "HLS pushes Orion (From LEO)"]

orion_push = st.sidebar.radio("Orion Push Scenario", push_options)

# --- CONSTANTS & DATA ---
G_CONSTANT = 9.80665
ORION_MASS_T = 27.0
STARSHIP_MAX_PROP_T = 1500.0

# Delta-V Values (m/s)
DV = {
    "LEO_TO_TLI": 3200,
    "TLI_TO_NRHO": 450,
    "TLI_TO_LLO": 900,
    "TLI_TO_PCO": 800,
    "NRHO_TO_SURFACE": 2750,
    "LLO_TO_SURFACE": 2000,
    "PCO_TO_SURFACE": 2400,
}

# --- CALCULATIONS ---
def calculate_mission():
    # 1. Ascent (Surface to Staging Orbit)
    dv_ascent = DV[f"{staging_orbit}_TO_SURFACE"] # Assuming ascent = descent
    m_final_ascent = dry_mass_t
    m_initial_ascent = m_final_ascent * math.exp(dv_ascent / (isp * G_CONSTANT))
    prop_ascent = m_initial_ascent - m_final_ascent

    # 2. Descent (Staging Orbit to Surface)
    dv_descent = DV[f"{staging_orbit}_TO_SURFACE"]
    m_final_descent = m_initial_ascent
    m_initial_descent = m_final_descent * math.exp(dv_descent / (isp * G_CONSTANT))
    prop_descent = m_initial_descent - m_final_descent

    # 3. Orbit Transfers / Orion Push
    m_before_landing = m_initial_descent
    
    # Add Orion mass if being pushed during the transfer
    if orion_push == "HLS pushes Orion (Transfer only)":
        # Specific sub-leg: Transfer from NRHO/PCO to LLO
        # This implies staging is LLO, but it was pushed from a high orbit
        dv_transfer = 0
        if staging_orbit == "LLO":
            # Rough estimate for NRHO -> LLO delta-v push
            dv_transfer = 450 
        
        m_final_transfer = m_before_landing + ORION_MASS_T
        m_initial_transfer = m_final_transfer * math.exp(dv_transfer / (isp * G_CONSTANT))
        prop_transfer = m_initial_transfer - m_final_transfer
        m_current = m_initial_transfer - ORION_MASS_T # Orion is dropped off at LLO
    else:
        m_current = m_before_landing

    # 4. LEO to Staging Orbit
    dv_to_staging = DV["LEO_TO_TLI"] + DV[f"TLI_TO_{staging_orbit}"]
    
    # Determine if Orion is attached for the LEO departure
    total_payload_at_leo = 0
    if orion_push == "HLS pushes Orion (From LEO)":
        total_payload_at_leo = ORION_MASS_T

    m_final_leo_burn = m_current + total_payload_at_leo
    m_initial_leo_burn = m_final_leo_burn * math.exp(dv_to_staging / (isp * G_CONSTANT))
    prop_leo_to_staging = m_initial_leo_burn - m_final_leo_burn
    
    # --- TOTALS ---
    total_prop_required = prop_ascent + prop_descent + prop_leo_to_staging
    if orion_push == "HLS pushes Orion (Transfer only)":
        total_prop_required += (m_initial_transfer - m_final_transfer)

    refills_needed = total_prop_required / refill_capacity_t
    
    return total_prop_required, refills_needed

total_prop, refills = calculate_mission()

# --- DISPLAY RESULTS ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Propellant Needed", f"{total_prop:.1f} Tons")
with col2:
    st.metric("Refills Required", f"{math.ceil(refills)}")

# Warnings
if total_prop > STARSHIP_MAX_PROP_T:
    st.error(f"⚠️ Warning: Total propellant ({total_prop:.1f}t) exceeds Starship capacity ({STARSHIP_MAX_PROP_T}t). You may need to refill in Lunar orbit.")

st.info(f"""
**Mission Summary:**
- **Orbit:** {staging_orbit}
- **Dry Mass:** {dry_mass_t}t
- **Orion Scenario:** {orion_push}
- **Delta-V Budget:** Working backward from Surface to LEO.
""")
