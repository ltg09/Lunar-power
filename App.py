import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Lunar Microgrid Sim", layout="wide")

st.title("🌙 Lunar Power Management Simulator")
st.sidebar.header("System Constraints")

# --- Sliders for Inputs ---
rtg_power = st.sidebar.slider("RTG Constant Output (W)", 0, 500, 110)
solar_peak = st.sidebar.slider("Solar Peak Output (W)", 0, 5000, 2500)
battery_cap = st.sidebar.slider("Battery Capacity (Wh)", 1000, 50000, 15000)
base_load = st.sidebar.slider("Base Load Consumption (W)", 50, 2000, 400)

st.sidebar.markdown("---")
lunar_cycle = st.sidebar.radio("Lunar Phase", ["Lunar Day (14 Earth Days)", "Lunar Night (14 Earth Days)"])

# --- Logic / Simulation ---
# Simulating a 24-hour Earth-equivalent slice of the lunar mission
hours = np.arange(0, 25, 1)
solar_gen = []
for h in hours:
    if lunar_cycle == "Lunar Night (14 Earth Days)":
        solar_gen.append(0)
    else:
        # Simple sine curve for solar over a "day" slice
        gen = solar_peak * np.sin(np.pi * h / 24)
        solar_gen.append(max(0, gen))

# Battery State of Charge calculation
soc = [battery_cap * 0.5] # Start at 50%
net_power = []

for i in range(len(hours)):
    current_gen = solar_gen[i] + rtg_power
    net = current_gen - base_load
    net_power.append(net)
    
    if i > 0:
        new_soc = soc[i-1] + net
        soc.append(min(battery_cap, max(0, new_soc)))

# --- Visualization ---
fig = go.Figure()
fig.add_trace(go.Scatter(x=hours, y=soc, name="Battery SoC (Wh)", fill='tozeroy', line=dict(color='limegreen')))
fig.add_trace(go.Bar(x=hours, y=net_power, name="Net Power (W)", marker_color='orange', opacity=0.6))

fig.update_layout(
    title="Energy Storage & Net Flux",
    xaxis_title="Hours",
    yaxis_title="Watts / Watt-Hours",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# --- Summary Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("RTG Contribution", f"{rtg_power} W")
col2.metric("Peak Generation", f"{max(solar_gen) + rtg_power:.0f} W")
col3.metric("Final SoC", f"{(soc[-1]/battery_cap)*100:.1f}%")

if soc[-1] == 0:
    st.error("⚠️ SYSTEM FAILURE: Battery depleted. Habitat life support at risk.")
elif soc[-1] < (battery_cap * 0.2):
    st.warning("Low Power: Energy conservation protocols recommended.")
else:
    st.success("System Stable: Power generation exceeds or meets mission load.")
