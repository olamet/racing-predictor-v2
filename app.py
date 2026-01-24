import streamlit as st
import pandas as pd
import base64

# --- Speed Data ---
speed_data = {
    "Vehicle": ["Car", "Sport", "Super", "Bigbike", "Moto", "ORV", "SUV", "Truck", "ATV"],
    "expressway": [264, 432, 480, 264, 220.8, 286, 348, 240, 115.2],
    "highway": [290.4, 480, 528, 230.4, 225.6, 240, 360, 276, 115.2],
    "dirt": [153.6, 360, 264, 165.6, 144, 220.8, 336, 87.6, 187.2],
    "potholes": [67.2, 57.6, 52.8, 187.2, 96, 134.4, 110.4, 108, 144],
    "bumpy": [98.4, 168, 151.2, 259.2, 108, 218.4, 213.6, 216, 187.2],
    "desert": [132, 96, 62.4, 132, 72, 58.08, 139.2, 98.28, 168]
}
df_speed = pd.DataFrame(speed_data).set_index("Vehicle")

# --- Initialize Session State ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Sidebar: Import/Export ---
st.sidebar.header("📁 Data Management")

# Export Button
if st.session_state.history:
    df_export = pd.DataFrame(st.session_state.history)
    csv = df_export.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="racing_data.csv">📥 Download Data</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)

# Import Section
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📤 Upload Data (CSV)", type="csv")
if uploaded_file is not None:
    df_uploaded = pd.read_csv(uploaded_file)
    st.session_state.history = df_uploaded.to_dict('records')
    st.sidebar.success(f"Loaded {len(st.session_state.history)} races!")

# --- Title ---
st.title("🏎️ Racing Predictor Pro")
st.markdown("Smart predictions with data persistence!")

# --- Input Section ---
col1, col2 = st.columns(2)
with col1:
    position = st.selectbox("📍 Visible Road Position", ["L", "C", "R"])
    road = st.selectbox("🛣️ Visible Road Type", list(df_speed.columns))
with col2:
    car1 = st.selectbox("🚗 Car 1", df_speed.index.tolist())
    car2 = st.selectbox("🚗 Car 2", df_speed.index.tolist())
    car3 = st.selectbox("🚗 Car 3", df_speed.index.tolist())

cars = [car1, car2, car3]

# --- Distance Weighting ---
weight_map = {"L": 0.8, "C": 1.0, "R": 1.3}
weight = weight_map[position]
speeds = [df_speed.loc[car, road] for car in cars]
weighted_speeds = [s * weight for s in speeds]
prediction = cars[weighted_speeds.index(max(weighted_speeds))]

# --- Display Prediction ---
st.subheader("🔮 Prediction Result")
st.success(f"Predicted Winner: **{prediction}**")

# --- Save Actual Result ---
st.markdown("---")
actual_winner = st.selectbox("🏆 Actual Winner", cars)
if st.button("💾 Save This Race"):
    st.session_state.history.append({
        "Position": position,
        "Road": road,
        "Car1": car1,
        "Car2": car2,
        "Car3": car3,
        "Winner": actual_winner
    })
    st.balloons()
    st.success("Race saved!")

# --- Show History ---
if st.session_state.history:
    st.markdown("---")
    st.subheader("📜 Your Race History")
    st.dataframe(pd.DataFrame(st.session_state.history))
