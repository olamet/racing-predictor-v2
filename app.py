import streamlit as st
import pandas as pd
import plotly.express as px
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
def load_history():
    try:
        df = pd.read_csv('racing_history.csv')
        return df.to_dict('records')
    except FileNotFoundError:
        return []
if 'history' not in st.session_state:
    st.session_state.history = load_history()
def save_history():
    df = pd.DataFrame(st.session_state.history)
    df.to_csv('racing_history.csv', index=False)
st.title("Racing Predictor Pro")
st.markdown("Advanced analytics with permanent data storage!")
col1, col2 = st.columns(2)
with col1:
    position = st.selectbox("Visible Road Position", ["L", "C", "R"])
    road = st.selectbox("Visible Road Type", list(df_speed.columns))
with col2:
    car1 = st.selectbox("Car 1", df_speed.index.tolist())
    car2 = st.selectbox("Car 2", df_speed.index.tolist())
    car3 = st.selectbox("Car 3", df_speed.index.tolist())
cars = [car1, car2, car3]
weight_map = {"L": 0.8, "C": 1.0, "R": 1.3}
weight = weight_map[position]
speeds = [df_speed.loc[car, road] for car in cars]
weighted_speeds = [s * weight for s in speeds]
prediction = cars[weighted_speeds.index(max(weighted_speeds))]
st.subheader("Prediction Result")
st.success(f"Predicted Winner: {prediction}")
