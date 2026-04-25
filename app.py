import streamlit as st
import math
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="HLS Logistics Terminal", layout="wide")

# --- THE TACTICAL CSS OVERRIDE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

    /* KILL THE TOP LINES AND VOID */
    [data-testid="stHeader"], [data-testid="stDecoration"], footer { 
        display: none !important; 
        visibility: hidden !important; 
        height: 0 !important; 
    }
    .main .block-container { 
        padding-top: 0rem !important; 
        margin-top: -50px !important; 
    }

    /* GLOBAL THEME */
    .stApp {
        background-color: #000000 !important;
        color: #98FF98 !important;
        font-family: 'JetBrains Mono', monospace;
    }

    /* DARK DROPDOWNS - NO MORE WHITE */
    div[data-baseweb="select"] > div, div[data-baseweb="popover"], div[role="listbox"], ul {
        background-color: #1a1a1a !important;
        color: #98FF98 !important;
        border: 1px solid #98FF98 !important;
    }
    li[role="option"], div[role="option"] {
        background-color: #1a1a1a !important;
        color: #98FF98 !important;
    }
    li[role="option"]:hover { background-color: #333 !important; }

    /* DARK EXPANDER */
    div[data-testid="stExpander"], div[data-testid="stExpanderDetails"] {
        background-color: #000000 !important;
        border: 1px solid #98FF98 !important;
        color: #98FF98 !important;
        border-radius: 0px !important;
    }

    /* TEXT & ALIGNMENT */
    h1, h2, h3, p, span, label, div { color: #98FF98 !important; text-transform: uppercase; }
    
    .input-block {
        min-height: 480px;
        border-top: 1px solid #98FF98;
        padding-top: 10px;
    }

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
    
    .tanker-container { display: flex; flex-wrap: wrap; gap: 4px; }
    hr { border: 0; border-top: 1px solid #333; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- STATE ---
if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = "MODE 1: NO PUSH"

# --- INPUT SECTION ---
st.markdown("<h2 style='text-align: center; letter-spacing: 5px; margin-top: 0px;'>HLS MISSION LOGISTICS</h2>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    st.image("tanker.svg", width=120)
    st.write("TANKER CONFIG")
    ref_amt = st.slider("PROP PER REFILL (t)", 50, 200, 100, step=5)
    cadence = st.slider("CADENCE (DAYS)", 1, 31, 7)
    cost_f = st.slider("COST PER FLIGHT ($M)", 1, 500, 100, step=5)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    st.image("hls.svg", width=80)
    st.write("HLS CONFIG")
    dry_m = st.slider("HLS DRY MASS (t)", 80, 250, 120, step=5)
    isp = st.slider("ENGINE ISP (s)", 350, 380, 365)
    orbit = st.selectbox("STAGING ORBIT", ["NRHO", "LLO", "PCO"])
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='input-block'>", unsafe_allow_html=True)
    st.image("orion.svg", width=180)
    st.write("ORION MODE")
    modes = ["MODE 1: NO PUSH", "MODE 2: LEO TO STAGING"]
    if orbit == "LLO": modes += ["MODE 3: NRHO TO LLO", "MODE 4: PCO TO LLO"]
    elif orbit == "PCO": modes += ["MODE 3: NRHO TO PCO"]
    
    for m in modes:
        active = st.session_state.selected_mode == m
        if active: st.markdown(f"<style>div.stButton > button:first-child:contains('{m}') {{ background-color: #98FF98 !important; color: black !important; font-weight: bold; }}</style>", unsafe_allow_html=True)
        if st.button(f"▶ {m}" if active else m): st.session_state.selected_mode = m; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- MATH ---
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
st.markdown("<h3 style='margin-bottom:-10px;'>RESULTS</h3><hr>", unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
with r1: st.metric("TANKERS", tanks)
with r2: 
    s_c = "warning-red" if total_p > CAP else ""
    st.markdown(f"TOTAL PROPELLANT")
    st.markdown(f"<p class='{s_c}' style='font-size:32px; margin:0;'>{total_p:,.1f} T / {CAP:,.0f} T</p>", unsafe_allow_html=True)
    if total_p > CAP: st.markdown(f"<p class='warning-red' style='font-size:10px;'>MISSION WOULD REQUIRE ADDITIONAL REFILLS IN HIGHER ORBIT, OR AT THE MOON</p>", unsafe_allow_html=True)
with r3: st.metric("REFILL CAMPAIGN LENGTH", f"{tanks * cadence} DAYS")
with r4: st.metric("REFILL CAMPAIGN COST", f"${cost/1000:.2f} B" if cost >= 1000 else f"${cost:,.0f} M")

# TANKER ROW - Using st.image for the fleet
t_cols = st.columns(15) # Show up to 15 side-by-side
for i in range(min(tanks, 15)):
    with t_cols[i]: st.image("tanker.svg")
if tanks > 15: st.write(f"... and {tanks-15} more tankers")

st.markdown("<br>", unsafe_allow_html=True)
with st.expander("▶ VIEW DETAILED TELEMETRY LOG"): st.table(pd.DataFrame(t_log))
