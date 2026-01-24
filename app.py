import streamlit as st
import pandas as pd

# Speed Data
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

# Initialize history
if 'history' not in st.session_state:
    st.session_state.history = []

# Title
st.title("🏎️ Racing Predictor")
st.write("Enter race details:")

# Input
position = st.selectbox("Position", ["L", "C", "R"])
road = st.selectbox("Road Type", list(df_speed.columns))
car1 = st.selectbox("Car 1", df_speed.index.tolist())
car2 = st.selectbox("Car 2", df_speed.index.tolist())
car3 = st.selectbox("Car 3", df_speed.index.tolist())

cars = [car1, car2, car3]
speeds = [df_speed.loc[car, road] for car in cars]
prediction = cars[speeds.index(max(speeds))]

st.subheader(f"Predicted Winner: {prediction}")

# Save result
winner = st.selectbox("Actual Winner", cars)
if st.button("Save Race"):
    st.session_state.history.append({
        "Position": position,
        "Road": road,
        "Cars": f"{car1},{car2},{car3}",
        "Winner": winner
    })
    st.success("Saved!")

# Show history
if st.session_state.history:
    st.write("History:")
    st.dataframe(pd.DataFrame(st.session_state.history))
