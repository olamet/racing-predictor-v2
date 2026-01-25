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

# --- إضافة الشريط الجانبي ---
page = st.sidebar.radio("اختر الصفحة", ["الرئيسية", "📊 نسبة الربح"])

# --- الصفحة الرئيسية ---
if page == "الرئيسية":
    st.title("Racing Predictor Pro")
    st.markdown("التوقعات الدقيقة مع حساب الربحية")
    
    col1, col2 = st.columns(2)
    with col1:
        position = st.selectbox("Visible Road Position", ["L", "C", "R"])
        road = st.selectbox("Visible Road Type", list(speed_data.keys())[1:])
    with col2:
        car1 = st.selectbox("Car 1", speed_data["Vehicle"])
        car2 = st.selectbox("Car 2", speed_data["Vehicle"])
        car3 = st.selectbox("Car 3", speed_data["Vehicle"])
    
    cars = [car1, car2, car3]
    
    st.markdown("---")
    st.subheader("Dual Predictions")
    
    hidden_roads_map = {        "expressway": ["highway", "bumpy"],
        "highway": ["expressway", "dirt"],
        "dirt": ["potholes", "desert"],
        "potholes": ["dirt", "bumpy"],
        "bumpy": ["highway", "potholes"],
        "desert": ["dirt", "potholes"]
    }
    hidden_roads = hidden_roads_map.get(road, ["dirt", "potholes"])
    
    weight_map = {"L": 0.8, "C": 1.0, "R": 1.3}
    weight = weight_map[position]
    
    combined_speeds = []
    for car in cars:
        car_idx = speed_data["Vehicle"].index(car)
        visible_speed = speed_data[road][car_idx] * weight
        hidden_speed1 = speed_data[hidden_roads[0]][car_idx]
        hidden_speed2 = speed_data[hidden_roads[1]][car_idx]
        combined_speed = (visible_speed * 0.6) + (hidden_speed1 * 0.2) + (hidden_speed2 * 0.2)
        combined_speeds.append(combined_speed)
    
    prediction_by_speed = cars[combined_speeds.index(max(combined_speeds))]
    
    prediction_by_history = cars[0]
    
    if st.session_state.history:
        hist_df = pd.DataFrame(st.session_state.history)
        
        exact_matches = hist_df[
            (hist_df['Position'] == position) &
            (hist_df['Road'] == road) &
            (hist_df['Car1'] == car1) &
            (hist_df['Car2'] == car2) &
            (hist_df['Car3'] == car3)
        ]
        
        if not exact_matches.empty:
            win_counts = exact_matches['Winner'].value_counts()
            valid_winners = win_counts[win_counts.index.isin(cars)]
            
            if not valid_winners.empty:
                prediction_by_history = valid_winners.idxmax()
            else:
                prediction_by_history = exact_matches['Winner'].mode().iloc[0]
        else:
            prediction_by_history = prediction_by_speed
    
    col1, col2 = st.columns(2)
      with col1:
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

# --- صفحة الإحصائيات ---
elif page == "📊 نسبة الربح":
    st.title("📊 نسبة ربح التوقعات")
    
    if not st.session_state.history or len(st.session_state.history) < 10:
        st.warning("يجب أن يكون لديك 10 جولات على الأقل لحساب النسبة. أنت لديك الآن: " + str(len(st.session_state.history)))
    else:
        hist_df = pd.DataFrame(st.session_state.history)
        
        # تحضير البيانات
        speed_data_dict = {k: v for k, v in zip(speed_data["Vehicle"], zip(*[speed_data[col] for col in speed_data if col != "Vehicle"]))}
        
        correct_speed = 0
        correct_history = 0
        total_races = len(hist_df)
        
        for idx, row in hist_df.iterrows():
            cars = [row['Car1'], row['Car2'], row['Car3']]
            
            # --- حساب توقع السرعة ---
            weight = {"L": 0.8, "C": 1.0, "R": 1.3}[row['Position']]
            hidden_roads = {
                "expressway": ["highway", "bumpy"],
                "highway": ["expressway", "dirt"],
                "dirt": ["potholes", "desert"],
                "potholes": ["dirt", "bumpy"],
                "bumpy": ["highway", "potholes"],                "desert": ["dirt", "potholes"]
            }.get(row['Road'], ["dirt", "potholes"])
            
            combined_speeds = []
            for car in cars:
                visible_speed = speed_data_dict[car][list(speed_data.keys()).index(row['Road'])-1] * weight
                hidden_speed1 = speed_data_dict[car][list(speed_data.keys()).index(hidden_roads[0])-1]
                hidden_speed2 = speed_data_dict[car][list(speed_data.keys()).index(hidden_roads[1])-1]
                combined_speed = (visible_speed * 0.6) + (hidden_speed1 * 0.2) + (hidden_speed2 * 0.2)
                combined_speeds.append(combined_speed)
            
            prediction_speed = cars[combined_speeds.index(max(combined_speeds))]
            
            # --- حساب توقع التاريخ ---
            exact_matches = hist_df[
                (hist_df['Position'] == row['Position']) &
                (hist_df['Road'] == row['Road']) &
                (hist_df['Car1'] == row['Car1']) &
                (hist_df['Car2'] == row['Car2']) &
                (hist_df['Car3'] == row['Car3'])
            ]
            
            prediction_history = row['Car1']
            if not exact_matches.empty:
                win_counts = exact_matches['Winner'].value_counts()
                valid_winners = win_counts[win_counts.index.isin(cars)]
                if not valid_winners.empty:
                    prediction_history = valid_winners.idxmax()
            
            # --- التحقق من الصحة ---
            actual = row['Winner']
            if prediction_speed == actual:
                correct_speed += 1
            if prediction_history == actual:
                correct_history += 1
        
        # --- عرض النتائج ---
        col1, col2 = st.columns(2)
        with col1:
            accuracy_speed = (correct_speed / total_races) * 100
            st.metric("النجاح بالسرعة", f"{accuracy_speed:.1f}%")
            st.progress(accuracy_speed / 100)
        
        with col2:
            accuracy_history = (correct_history / total_races) * 100
            st.metric("النجاح بالتاريخ", f"{accuracy_history:.1f}%")
            st.progress(accuracy_history / 100)
        
        st.markdown("---")
        st.subheader("التفاصيل")        st.write(f"✅ توقعات السرعة الصحيحة: {correct_speed}/{total_races}")
        st.write(f"✅ توقعات التاريخ الصحيحة: {correct_history}/{total_races}")
        
        # مخطط مقارنة بسيط
        comparison_df = pd.DataFrame({
            "النوع": ["التوقع بالسرعة", "التوقع التاريخي"],
            "النسبة": [accuracy_speed, accuracy_history]
        })
        st.bar_chart(comparison_df.set_index("النوع"))
