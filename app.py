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
    st.subheader("Advanced Analytics")
    
    hist_df = pd.DataFrame(st.session_state.history)
    
    wins_by_car = hist_df['Winner'].value_counts().reset_index()
    wins_by_car.columns = ['Car', 'Wins']
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("Total Wins by Car")
        if not wins_by_car.empty:
            fig1 = px.pie(wins_by_car, values='Wins', names='Car', hole=0.3)
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.write("Wins by Position")
        wins_by_pos = hist_df.groupby(['Position', 'Winner']).size().reset_index(name='Count')
        if not wins_by_pos.empty:
            fig2 = px.bar(wins_by_pos, x='Position', y='Count', color='Winner', barmode='group')
            st.plotly_chart(fig2, use_container_width=True)
    
    st.write("Win Probability by (Position + Road)")
    if not hist_df.empty:
        grouped = hist_df.groupby(['Position', 'Road', 'Winner']).size().reset_index(name='Count')
        if not grouped.empty:
            total_per_group = grouped.groupby(['Position', 'Road'])['Count'].sum().reset_index()
            total_per_group.rename(columns={'Count': 'Total'}, inplace=True)
            
            prob_df = grouped.merge(total_per_group, on=['Position', 'Road'])
            prob_df['Probability (%)'] = (prob_df['Count'] / prob_df['Total']) * 100
        st.dataframe(prob_df.sort_values(by=['Position', 'Road'], ascending=[True, True]), use_container_width=True)
            
        if not prob_df.empty:
           fig3 = px.bar(prob_df, x='Position', y='Probability (%)', color='Winner', facet_col='Road', facet_col_wrap=3)
           st.plotly_chart(fig3, use_container_width=True)
    
    st.write("Wins by Car per (Position + Road)")
    wins_per_combination = hist_df.groupby(['Position', 'Road', 'Winner']).size().reset_index(name='Wins')
    if not wins_per_combination.empty:
        st.dataframe(wins_per_combination.sort_values(by=['Position', 'Road'], ascending=[True, True]), use_container_width=True)

if st.session_state.history:
    st.markdown("---")
    st.subheader("Race History")
    st.dataframe(pd.DataFrame(st.session_state.history))
