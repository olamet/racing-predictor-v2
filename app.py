import streamlit as st
import pandas as pd

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
st.markdown("Exact matching historical predictions")

col1, col2 = st.columns(2)
with col1:
    position = st.selectbox("Visible Road Position", ["L", "C", "R"])
    road = st.selectbox("Visible Road Type", list(df_speed.columns))
with col2:
    car1 = st.selectbox("Car 1", df_speed.index.tolist())
    car2 = st.selectbox("Car 2", df_speed.index.tolist())
    car3 = st.selectbox("Car 3", df_speed.index.tolist())

cars = [car1, car2, car3]

st.markdown("---")
st.subheader("Dual Predictions")

hidden_roads_map = {
    "expressway": ["highway", "bumpy"],
    "highway": ["expressway", "dirt"],
    "dirt": ["potholes", "desert"],
    "potholes": ["dirt", "bumpy"],    "bumpy": ["highway", "potholes"],
    "desert": ["dirt", "potholes"]
}
hidden_roads = hidden_roads_map.get(road, ["dirt", "potholes"])

weight_map = {"L": 0.8, "C": 1.0, "R": 1.3}
weight = weight_map[position]

combined_speeds = []
for car in cars:
    visible_speed = df_speed.loc[car, road] * weight
    hidden_speed1 = df_speed.loc[car, hidden_roads[0]]
    hidden_speed2 = df_speed.loc[car, hidden_roads[1]]
    combined_speed = (visible_speed * 0.6) + (hidden_speed1 * 0.2) + (hidden_speed2 * 0.2)
    combined_speeds.append(combined_speed)

prediction_by_speed = cars[combined_speeds.index(max(combined_speeds))]

# EXACT HISTORICAL MATCHING
prediction_by_history = cars[0]  # Default

if st.session_state.history:
    hist_df = pd.DataFrame(st.session_state.history)
    
    # Filter EXACT matching races (same position, road, AND car order)
    exact_matches = hist_df[
        (hist_df['Position'] == position) &
        (hist_df['Road'] == road) &
        (hist_df['Car1'] == car1) &
        (hist_df['Car2'] == car2) &
        (hist_df['Car3'] == car3)
    ]
    
    if not exact_matches.empty:
        # Count wins for each car in THIS EXACT setup
        win_counts = exact_matches['Winner'].value_counts()
        
        # Only consider winners that are in current race
        valid_winners = win_counts[win_counts.index.isin(cars)]
        
        if not valid_winners.empty:
            prediction_by_history = valid_winners.idxmax()
        else:
            # If no valid winners, use the most frequent winner overall
            prediction_by_history = exact_matches['Winner'].mode().iloc[0]
    else:
        # If no exact matches, fall back to combined speed prediction
        prediction_by_history = prediction_by_speed

col1, col2 = st.columns(2)with col1:
    st.success(f"By Combined Speed:\n{prediction_by_speed}")
with col2:
    st.info(f"By Exact History:\n{prediction_by_history}")

st.markdown("---")
actual_winner = st.selectbox("Actual Winner", cars)
if st.button("Save This Race"):
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
    st.success(f"Race saved! Total: {len(st.session_state.history)}")

if st.session_state.history:
    st.markdown("---")
    st.subheader("Race History")
    st.dataframe(pd.DataFrame(st.session_state.history))
