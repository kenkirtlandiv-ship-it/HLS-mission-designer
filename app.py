import streamlit as st
import math
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Logistics Terminal", layout="wide")

# --- CUSTOM CSS: THE "HARDENED" DARK TERMINAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

    /* 1. ABSOLUTE REMOVAL OF TOP DECORATION & VOID */
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    header { visibility: hidden !important; height: 0 !important; }
    
    /* Pull content to the very top */
    .main .block-container { 
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important; 
        margin-top: -60px !important; 
    }

    /* 2. GLOBAL DARK THEME */
    .stApp {
        background-color: #000000 !important;
        color: #98FF98 !important;
        font-family: 'JetBrains Mono', monospace;
    }

    /* 3. DROPDOWN (SELECTBOX) DARK MODE */
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

    /* 4. EXPANDER & TABLE DARK MODE */
    div[data-testid="stExpander"] {
        background-color: #000000 !important;
        border: 1px solid #98FF98 !important;
        border-radius: 0px !important;
    }
    div[data-testid="stExpanderDetails"] {
        background-color: #000000 !important;
        color: #98FF98 !important;
    }
    table { background-color: #000 !important; border: 1px solid #98FF98 !important; }
    th, td { border: 1px solid #333 !important; color: #98FF98 !important; }

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

    /* ROTATION FOR HORIZONTAL SHIPS */
    .horizontal-ship {
        transform: rotate(90deg);
        margin: 40px 0; /* Space for the rotation swing */
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

# --- STATE ---
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = "MODE 1: NO PUSH"

# --- CONTENT ---
st.markdown("<h2 style='text-align: center; letter-spacing: 5px; margin-bottom: 5px; margin-top: 0px;'>HLS MISSION LOGISTICS</h2>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    # Rotating the tanker to be horizontal
    st.markdown('<div class="horizontal-ship">', unsafe_allow_html=True)
    st.image("tanker.svg", width=100)
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("STARSHIP REFILL TANKER")
    ref_amt = st.slider("PROP PER REFILL (t)", 50, 200, 100, step=5)
    cadence = st.slider("CADENCE (DAYS)", 1, 31, 7)
    cost_f = st.slider("COST PER FLIGHT ($M)", 1, 500, 100, step=5)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    # Rotating the HLS to be horizontal
    st.markdown('<div class="horizontal-ship">', unsafe_allow_html=True)
    st.image("hls.svg", width=100)
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("HLS STARSHIP")
    dry_m = st.slider("HLS DRY MASS (t)", 80, 250, 120, step=5)
    isp = st.slider("ENGINE ISP (s)", 350, 380, 365)
    orbit = st.selectbox("STAGING ORBIT", ["NRHO", "LLO", "PCO"])
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    # Orion is naturally horizontal
    st.image("orion.svg", width=220)
    st.write("ORION MODE")
    modes = ["MODE 1: NO PUSH", "MODE 2: LEO TO STAGING"]
    if orbit == "LLO": modes += ["MODE 3: NRHO TO LLO", "MODE 4: PCO TO LLO"]
    elif orbit == "PCO": modes += ["MODE 3: NRHO TO PCO"]
    
    for m in modes:
        active = st.session_state.selected_mode == m
        if active: st.markdown(f"<style>div.stButton > button:first-child:contains('{m}') {{ background-color: #98FF98 !important; color: black !important; font-weight: bold; }}</style>", unsafe_allow_html=True)
        if st.button(f"▶ {m}" if active else m): st.session_state.selected_mode = m; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- MATH (BACKWARD INTEGRATION) ---
G = 9.80665; OM = 27.0; CAP = 1500.0
DV = {"LEO_TO_TLI": 3200, "TLI_TO_NRHO": 450, "TLI_TO_LLO": 900, "TLI_TO_PCO": 800, "NRHO_TO_SURFACE": 2750, "LLO_TO_SURFACE": 2000, "PCO_TO_SURFACE": 2400}

def get_tel():
    m = st.session_state.selected_mode; log = []
    dva = DV[f"{orbit}_TO_SURFACE"]; maf = dry_m; mai = maf * math.exp(dva / (isp * G))
    log.append({"LEG": "ASCENT: SURFACE TO ORBIT", "DV": dva, "WET MASS": f"{mai:.1f}t", "DRY MASS": f"{maf:.1f}t", "VEHICLE": "HLS"})
    dvd = dva; mdf = mai; mdi = mdf * math.exp(dvd / (isp * G))
    log.append({"LEG": "DESCENT: ORBIT TO SURFACE", "DV": dvd, "WET MASS": f"{mdi:.1f}t", "DRY MASS": f"{mdf:.1f}t", "VEHICLE": "HLS"})
    curr = mdi
    if "MODE 3" in m or "MODE 4" in m:
        dvp = 450 if "NRHO TO LLO" in m else 400 if "PCO TO LLO" in m else 350
        mpf = curr + OM; mpi = mpf * math.exp(dvp / (isp * G))
        log.append({"LEG": "ORION PUSH MANEUVER", "DV": dvp, "WET MASS": f"{mpi:.1f}t", "DRY MASS": f"{mpf:.1f}t", "VEHICLE": "HLS + 27T ORION"})
        curr = mpi - OM
    dva2 = DV[f"TLI_TO_{orbit}"]; has_o = "MODE 2" in m; ma2f = curr + (OM if has_o else 0); ma2i = ma2f * math.exp(dva2 / (isp * G))
    log.append({"LEG": f"ARRIVAL AT {orbit}", "DV": dva2, "WET MASS": f"{ma2i:.1f}t", "DRY MASS": f"{ma2f:.1f}t", "VEHICLE": f"HLS {'+ 27T ORION' if has_o else ''}"})
    dvl = 3200; mlf = ma2i; mli = mlf * math.exp(dvl / (isp * G))
    log.append({"LEG": "TLI DEPARTURE (LEO)", "DV": dvl, "WET MASS": f"{mli:.1f}t", "DRY MASS": f"{mlf:.1f}t", "VEHICLE": f"HLS {'+ 27T ORION' if has_o else ''}"})
    prop = mli - dry_m - (OM if has_o else 0)
    if "MODE 3" in m or "MODE 4" in m: prop = mli - dry_m
    return prop, log

total_p, t_log = get_tel(); tanks = math.ceil(total_p / ref_amt); cost = tanks * cost_f

# --- RESULTS ---
st.markdown("<h3 style='margin-bottom:0px; margin-top:10px;'>RESULTS</h3><hr style='margin-top:5px;'>", unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
with r1: st.metric("TANKERS", tanks)
with r2: 
    s_c = "warning-red" if total_p > CAP else ""
    st.markdown(f"TOTAL PROPELLANT")
    st.markdown(f"<p class='{s_c}' style='font-size:32px; margin:0;'>{total_p:,.1f} T / {CAP:,.0f} T</p>", unsafe_allow_html=True)
    if total_p > CAP: st.markdown(f"<p class='warning-red' style='font-size:10px;'>MISSION WOULD REQUIRE ADDITIONAL REFILLS IN HIGHER ORBIT, OR AT THE MOON</p>", unsafe_allow_html=True)
with r3: st.metric("REFILL CAMPAIGN LENGTH", f"{tanks * cadence} DAYS")
with r4: st.metric("REFILL CAMPAIGN COST", f"${cost/1000:.2f} B" if cost >= 1000 else f"${cost:,.0f} M")

# TANKER ROW - Displaying actual icons
t_cols = st.columns(15) 
for i in range(min(tanks, 15)):
    with t_cols[i]: st.image("tanker.svg")
if tanks > 15: st.write(f"... AND {tanks-15} MORE TANKERS")

st.markdown("<br>", unsafe_allow_html=True)
with st.expander("▶ VIEW DETAILED TELEMETRY LOG"): st.table(pd.DataFrame(t_log))
