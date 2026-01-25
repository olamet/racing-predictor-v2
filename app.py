import streamlit as st
import pandas as pd

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

# --- Load History from CSV ---
def load_history():
    try:
        df = pd.read_csv('racing_history.csv')
        return df.to_dict('records')
    except FileNotFoundError:
        return []

if 'history' not in st.session_state:
    st.session_state.history = load_history()

# --- Save History to CSV ---
def save_history():
    df = pd.DataFrame(st.session_state.history)
    df.to_csv('racing_history.csv', index=False)

st.title("🏎️ Racing Predictor Pro")
st.markdown("Phase 1: Dual Prediction System")

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

# --- Phase 1: Combined Speed Prediction ---
st.markdown("---")
st.subheader("🔮 Dual Predictions")
# Step 1: Estimate hidden roads based on visible road
hidden_roads_map = {
    "expressway": ["highway", "bumpy"],
    "highway": ["expressway", "dirt"],
    "dirt": ["potholes", "desert"],
    "potholes": ["dirt", "bumpy"],
    "bumpy": ["highway", "potholes"],
    "desert": ["dirt", "potholes"]
}
hidden_roads = hidden_roads_map.get(road, ["dirt", "potholes"])

# Step 2: Calculate combined speeds
weight_map = {"L": 0.8, "C": 1.0, "R": 1.3}
weight = weight_map[position]

combined_speeds = []
for car in cars:
    # Speed on visible road (weighted by position)
    visible_speed = df_speed.loc[car, road] * weight
    
    # Speeds on hidden roads (no position weighting)
    hidden_speed1 = df_speed.loc[car, hidden_roads[0]]
    hidden_speed2 = df_speed.loc[car, hidden_roads[1]]
    
    # Combined speed with weights
    combined_speed = (visible_speed * 0.6) + (hidden_speed1 * 0.2) + (hidden_speed2 * 0.2)
    combined_speeds.append(combined_speed)

prediction_by_speed = cars[combined_speeds.index(max(combined_speeds))]

# Step 3: Simple historical prediction
prediction_by_history = "Car"  # Default
if st.session_state.history:
    # Find most common winner in similar conditions
    hist_df = pd.DataFrame(st.session_state.history)
    similar_races = hist_df[
        (hist_df['Road'] == road) & 
        (hist_df['Position'] == position) &
        (hist_df['Car1'].isin(cars)) &
        (hist_df['Car2'].isin(cars)) &
        (hist_df['Car3'].isin(cars))
    ]
    
    if not similar_races.empty:
        most_common_winner = similar_races['Winner'].mode().iloc[0]
        prediction_by_history = most_common_winner

# --- Display Both Predictions ---
col1, col2 = st.columns(2)
with col1:    st.success(f"📊 **By Combined Speed:**\n{prediction_by_speed}")
with col2:
    st.info(f"📈 **By History:**\n{prediction_by_history}")

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
    save_history()
    st.balloons()
    st.success(f"Race saved! Total races: {len(st.session_state.history)}")

# --- Show History ---
if st.session_state.history:
    st.markdown("---")
    st.subheader("📜 Race History")
    st.dataframe(pd.DataFrame(st.session_state.history))
