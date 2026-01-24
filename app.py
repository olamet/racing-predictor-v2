import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
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

# --- Load Historical Data (if uploaded) ---
def load_historical_data():
    try:
        # محاولة تحميل ملف البيانات التاريخية
        hist_df = pd.read_csv('racing_history.csv')
        st.session_state.history = hist_df.to_dict('records')
        st.sidebar.success(f"Loaded {len(st.session_state.history)} historical races!")
    except FileNotFoundError:
        pass

load_historical_data()

# --- Title ---
st.title("🏎️ Racing Car Predictor Pro")
st.markdown("Smart predictions powered by your historical data!")

# --- Sidebar: Import/Export ---
st.sidebar.header("📁 Data Management")

# Export Button
if st.session_state.history:
    df_export = pd.DataFrame(st.session_state.history)
    csv = df_export.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="racing_data.csv">📥 Download All Data (CSV)</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)

# Import Sectionst.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📤 Upload Historical Data (CSV)", type="csv")
if uploaded_file is not None:
    df_uploaded = pd.read_csv(uploaded_file)
    st.session_state.history = df_uploaded.to_dict('records')
    st.sidebar.success(f"Imported {len(st.session_state.history)} races!")

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

# --- Speed-Based Prediction ---
speeds = [df_speed.loc[car, road] for car in cars]
fastest_by_speed = cars[speeds.index(max(speeds))]

# --- Historical Analysis ---
history_df = pd.DataFrame(st.session_state.history)
win_counts = {car: 0 for car in cars}
total_matches = 0

if not history_df.empty:
    mask = (
        (history_df['Position'] == position) &
        (history_df['Road'] == road) &
        (history_df['Car1'].isin(cars)) &
        (history_df['Car2'].isin(cars)) &
        (history_df['Car3'].isin(cars))
    )
    relevant_matches = history_df[mask]
    total_matches = len(relevant_matches)
    
    if total_matches > 0:
        for car in cars:
            win_counts[car] = len(relevant_matches[relevant_matches['Winner'] == car])

# --- Smart Prediction ---
if total_matches >= 2:  # Require at least 2 matches for historical prediction
    best_historical = max(win_counts, key=win_counts.get)
    prediction = best_historical
    method = "📊 Historical Data"
    confidence = max(win_counts.values()) / total_matches * 100
else:    prediction = fastest_by_speed
    method = "⚡ Speed-Based"
    confidence = None

# --- Display Prediction ---
st.subheader("🔮 Prediction Result")
if confidence:
    st.success(f"**{prediction}** ({method}) | Confidence: {confidence:.0f}%")
else:
    st.info(f"**{prediction}** ({method}) | Not enough historical data")

# --- Win Probabilities ---
if total_matches > 0:
    st.subheader("📈 Win Probabilities")
    prob_data = []
    for car in cars:
        prob = win_counts[car] / total_matches * 100
        prob_data.append({"Car": car, "Probability (%)": prob})
    prob_df = pd.DataFrame(prob_data)
    st.bar_chart(prob_df.set_index("Car"))

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
    st.success("Race saved successfully!")

# --- Analytics Dashboard ---
if st.session_state.history:
    st.markdown("---")
    st.subheader("📊 Advanced Analytics")
    
    hist_df = pd.DataFrame(st.session_state.history)
    
    # Win Count by Car
    wins_by_car = hist_df['Winner'].value_counts().reset_index()
    wins_by_car.columns = ['Car', 'Wins']
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("🏆 Total Wins by Car")        fig1 = px.pie(wins_by_car, values='Wins', names='Car', hole=0.3)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.write("📍 Wins by Position")
        wins_by_pos = hist_df.groupby(['Position', 'Winner']).size().reset_index(name='Count')
        fig2 = px.bar(wins_by_pos, x='Position', y='Count', color='Winner', barmode='group')
        st.plotly_chart(fig2, use_container_width=True)
    
    # Road Type Analysis
    st.write("🛣️ Performance by Road Type")
    road_wins = hist_df.groupby(['Road', 'Winner']).size().reset_index(name='Wins')
    fig3 = px.bar(road_wins, x='Road', y='Wins', color='Winner', barmode='stack')
    st.plotly_chart(fig3, use_container_width=True)
