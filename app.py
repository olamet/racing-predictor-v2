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

# --- خرائط الطرق المخفية ---
hidden_roads_map = {
    "expressway": ["highway", "bumpy"],
    "highway": ["expressway", "dirt"],
    "dirt": ["potholes", "desert"],
    "potholes": ["dirt", "bumpy"],
    "bumpy": ["highway", "potholes"],
    "desert": ["dirt", "potholes"]
}

# --- أوزان ديناميكية حسب نوع الطريق ---
road_weights_config = {
    "expressway": {"visible": 0.5, "hidden1": 0.25, "hidden2": 0.25},
    "highway": {"visible": 0.5, "hidden1": 0.25, "hidden2": 0.25},
    "dirt": {"visible": 0.3, "hidden1": 0.35, "hidden2": 0.35},
    "potholes": {"visible": 0.3, "hidden1": 0.35, "hidden2": 0.35},
    "bumpy": {"visible": 0.4, "hidden1": 0.3, "hidden2": 0.3},
    "desert": {"visible": 0.2, "hidden1": 0.4, "hidden2": 0.4}
}

# --- خصائص السيارات ---
car_properties = {
    "Car": {"weight": 1.0, "power": 1.0, "handling": 1.0},
    "Sport": {"weight": 0.8, "power": 1.3, "handling": 1.2},
    "Super": {"weight": 0.7, "power": 1.5, "handling": 1.4},
    "Bigbike": {"weight": 0.6, "power": 1.2, "handling": 0.9},
    "Moto": {"weight": 0.5, "power": 1.0, "handling": 0.8},
    "ORV": {"weight": 1.3, "power": 1.1, "handling": 1.5},
    "SUV": {"weight": 1.2, "power": 1.2, "handling": 1.3},
    "Truck": {"weight": 1.5, "power": 1.0, "handling": 0.7},
    "ATV": {"weight": 0.9, "power": 0.9, "handling": 1.6}
}

# --- النسب المئوية الصحيحة للطرق (46% + 27% + 27%) ---
ROAD_PERCENTAGES = {
    "visible": 0.27,      # الطريق المرئي
    "long_hidden": 0.46,  # الطريق الطويل المخفي (الموضع L)    "short_hidden": 0.27  # الطريق المخفي القصير
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

page = st.sidebar.radio("اختر الصفحة", ["الرئيسية", "نسبة الربح"])

if page == "الرئيسية":
    st.title("Racing Predictor Pro")
    st.markdown("تنبؤ ذكي مع نسب طرق دقيقة (46% + 27% + 27%)")
    
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
    st.subheader("التنبؤ الذكي")
    
    weight_map = {"L": 0.8, "C": 1.0, "R": 1.3}
    weight = weight_map[position]
    
    # --- التنبؤ بالطرق المخفية ومواقعها ---
    hidden_roads = hidden_roads_map.get(road, ["dirt", "potholes"])
    hidden_positions = ["C", "C"]  # افتراضي: وسط
    
    if st.session_state.history and len(st.session_state.history) > 20:
        hist_temp = pd.DataFrame(st.session_state.history)
        if 'Hidden_Road_1' in hist_temp.columns and 'Hidden_Road_1_Position' in hist_temp.columns:
            road_matches = hist_temp[
                (hist_temp['Road'] == road) & 
                (hist_temp['Position'] == position)            ]
            if not road_matches.empty:
                road_matches['full_pair'] = (
                    road_matches['Hidden_Road_1'] + ',' + 
                    road_matches['Hidden_Road_1_Position'] + ',' +
                    road_matches['Hidden_Road_2'] + ',' + 
                    road_matches['Hidden_Road_2_Position']
                )
                mode_series = road_matches['full_pair'].mode()
                if not mode_series.empty:
                    parts = mode_series.iloc[0].split(',')
                    if len(parts) == 4:
                        hidden_roads = [parts[0], parts[2]]
                        hidden_positions = [parts[1], parts[3]]
    
    prediction_method = ""
    
    if st.session_state.history and len(st.session_state.history) > 20:
        hist_df = pd.DataFrame(st.session_state.history)
        
        similar_matches = hist_df[
            (hist_df['Position'] == position) &
            (hist_df['Road'] == road) &
            (hist_df['Car1'].isin(cars)) &
            (hist_df['Car2'].isin(cars)) &
            (hist_df['Car3'].isin(cars))
        ]
        
        if len(similar_matches) >= 1:
            win_counts = {}
            for car in cars:
                wins = len(similar_matches[similar_matches['Winner'] == car])
                win_counts[car] = wins
            
            prediction = max(win_counts, key=win_counts.get)
            prediction_method = "التاريخي (دقة عالية)"
        else:
            # --- حساب الوقت الإجمالي باستخدام النسب الصحيحة (46% + 27% + 27%) ---
            combined_times = []
            
            # تحديد الطريق الطويل (الموضع L)
            is_long_hidden1 = (hidden_positions[0] == "L")
            is_long_hidden2 = (hidden_positions[1] == "L")
            
            # ضمان وجود طريق طويل واحد فقط
            if is_long_hidden1 and is_long_hidden2:
                is_long_hidden1 = True
                is_long_hidden2 = False
            elif not is_long_hidden1 and not is_long_hidden2:
                is_long_hidden1 = True
                is_long_hidden2 = False
            
            for car in cars:
                car_idx = speed_data["Vehicle"].index(car)
                visible_speed = speed_data[road][car_idx] * weight
                
                # سرعة الطرق المخفية مع تعديل الموضع
                h1_weight = weight_map.get(hidden_positions[0], 1.0)
                h2_weight = weight_map.get(hidden_positions[1], 1.0)
                hidden_speed1 = speed_data[hidden_roads[0]][car_idx] * h1_weight
                hidden_speed2 = speed_data[hidden_roads[1]][car_idx] * h2_weight
                
                # حساب الوقت باستخدام النسب المئوية الصحيحة
                time_visible = ROAD_PERCENTAGES["visible"] / visible_speed
                
                if is_long_hidden1:
                    time_hidden1 = ROAD_PERCENTAGES["long_hidden"] / hidden_speed1
                    time_hidden2 = ROAD_PERCENTAGES["short_hidden"] / hidden_speed2
                else:
                    time_hidden1 = ROAD_PERCENTAGES["short_hidden"] / hidden_speed1
                    time_hidden2 = ROAD_PERCENTAGES["long_hidden"] / hidden_speed2
                
                total_time = time_visible + time_hidden1 + time_hidden2
                
                # تعديل الوقت حسب خصائص السيارة
                if road in ["dirt", "potholes", "desert", "bumpy"]:
                    handling_factor = car_properties[car]["handling"]
                    total_time *= (1.0 - handling_factor * 0.2)
                else:
                    power_factor = car_properties[car]["power"]
                    total_time *= (1.0 / power_factor)
                
                combined_times.append(total_time)
            
            prediction = cars[combined_times.index(min(combined_times))]
            prediction_method = "المدمج (الوقت: 46%+27%+27%)"
    else:
        # --- نفس الحساب للبيانات الأولية ---
        combined_times = []
        
        is_long_hidden1 = (hidden_positions[0] == "L")
        is_long_hidden2 = (hidden_positions[1] == "L")
        
        if is_long_hidden1 and is_long_hidden2:
            is_long_hidden1 = True
            is_long_hidden2 = False
        elif not is_long_hidden1 and not is_long_hidden2:
            is_long_hidden1 = True
            is_long_hidden2 = False
          for car in cars:
            car_idx = speed_data["Vehicle"].index(car)
            visible_speed = speed_data[road][car_idx] * weight
            
            h1_weight = weight_map.get(hidden_positions[0], 1.0)
            h2_weight = weight_map.get(hidden_positions[1], 1.0)
            hidden_speed1 = speed_data[hidden_roads[0]][car_idx] * h1_weight
            hidden_speed2 = speed_data[hidden_roads[1]][car_idx] * h2_weight
            
            time_visible = ROAD_PERCENTAGES["visible"] / visible_speed
            
            if is_long_hidden1:
                time_hidden1 = ROAD_PERCENTAGES["long_hidden"] / hidden_speed1
                time_hidden2 = ROAD_PERCENTAGES["short_hidden"] / hidden_speed2
            else:
                time_hidden1 = ROAD_PERCENTAGES["short_hidden"] / hidden_speed1
                time_hidden2 = ROAD_PERCENTAGES["long_hidden"] / hidden_speed2
            
            total_time = time_visible + time_hidden1 + time_hidden2
            
            if road in ["dirt", "potholes", "desert", "bumpy"]:
                handling_factor = car_properties[car]["handling"]
                total_time *= (1.0 - handling_factor * 0.2)
            else:
                power_factor = car_properties[car]["power"]
                total_time *= (1.0 / power_factor)
            
            combined_times.append(total_time)
        
        prediction = cars[combined_times.index(min(combined_times))]
        prediction_method = "الوقت (بيانات أولية)"
    
    st.success(f"التنبؤ: **{prediction}**")
    st.caption(f"الطريقة: {prediction_method}")
    st.caption(f"الطرق المخفية: {hidden_roads[0]} ({hidden_positions[0]}) + {hidden_roads[1]} ({hidden_positions[1]})")
    
    st.markdown("---")
    actual_winner = st.selectbox("Actual Winner", cars)
    
    st.subheader("الطرق المخفية الفعلية")
    hidden_road1 = st.selectbox("الطريق المخفي الأول", list(speed_data.keys())[1:], key="hr1")
    hidden_road1_pos = st.selectbox("موضع الطريق الأول", ["L", "C", "R"], key="hr1p")
    hidden_road2 = st.selectbox("الطريق المخفي الثاني", list(speed_data.keys())[1:], key="hr2")
    hidden_road2_pos = st.selectbox("موضع الطريق الثاني", ["L", "C", "R"], key="hr2p")
    
    if st.button("Save This Race"):
        st.session_state.history.append({
            "Position": position,
            "Road": road,
            "Hidden_Road_1": hidden_road1,            "Hidden_Road_1_Position": hidden_road1_pos,
            "Hidden_Road_2": hidden_road2,
            "Hidden_Road_2_Position": hidden_road2_pos,
            "Car1": car1,
            "Car2": car2,
            "Car3": car3,
            "Winner": actual_winner,
            "Prediction": prediction,
            "Prediction_Method": prediction_method
        })
        save_history()
        st.balloons()
        st.success(f"تم الحفظ! الإجمالي: {len(st.session_state.history)}")
    
    if st.session_state.history:
        st.markdown("---")
        st.subheader("سجل السباقات")
        display_df = pd.DataFrame(st.session_state.history)
        if 'Hidden_Road_1_Position' in display_df.columns:
            display_df['Hidden_Details'] = (
                display_df['Hidden_Road_1'] + ' (' + display_df['Hidden_Road_1_Position'] + ') + ' +
                display_df['Hidden_Road_2'] + ' (' + display_df['Hidden_Road_2_Position'] + ')'
            )
            cols_to_show = ['Position', 'Road', 'Hidden_Details', 'Car1', 'Car2', 'Car3', 'Winner', 'Prediction']
        else:
            cols_to_show = ['Position', 'Road', 'Car1', 'Car2', 'Car3', 'Winner', 'Prediction']
        
        st.dataframe(display_df[cols_to_show] if all(col in display_df.columns for col in cols_to_show) else display_df)

elif page == "نسبة الربح":
    st.title("نسبة ربح التوقعات")
    
    if not st.session_state.history or len(st.session_state.history) < 10:
        st.warning(f"يجب أن يكون لديك 10 جولات على الأقل. لديك الآن: {len(st.session_state.history)}")
    else:
        hist_df = pd.DataFrame(st.session_state.history)
        
        total_races = len(hist_df)
        correct_predictions = 0
        car_stats = {}
        for car in speed_data["Vehicle"]:
            car_stats[car] = {"wins": 0, "correct_predictions": 0}
        
        for idx, row in hist_df.iterrows():
            if 'Prediction' in row and 'Winner' in row:
                if row['Prediction'] == row['Winner']:
                    correct_predictions += 1
                    car_stats[row['Winner']]['correct_predictions'] += 1
                car_stats[row['Winner']]['wins'] += 1
                overall_accuracy = (correct_predictions / total_races) * 100 if total_races > 0 else 0
        
        st.metric("النسبة الإجمالية للربح", f"{overall_accuracy:.1f}%")
        st.progress(overall_accuracy / 100)
        st.write(f"✅ التنبؤات الصحيحة: {correct_predictions}/{total_races}")
        
        st.markdown("---")
        st.subheader("نسبة نجاح توقع كل سيارة")
        
        car_accuracy_list = []
        for car, stats in car_stats.items():
            if stats['wins'] > 0:
                accuracy = (stats['correct_predictions'] / stats['wins']) * 100
                car_accuracy_list.append((car, accuracy, stats['wins'], stats['correct_predictions']))
        
        car_accuracy_list.sort(key=lambda x: (-x[1], -x[2]))
        
        for car, accuracy, total_wins, correct in car_accuracy_list:
            st.write(f"**{car}**: {accuracy:.1f}%")
            st.caption(f"✅ {correct}/{total_wins} جولة فازت فيها")
            st.progress(accuracy / 100)
        
        st.markdown("---")
        st.subheader("ملخص الأداء")
        st.write(f"📊 إجمالي الجولات: {total_races}")
        st.write(f"✅ التنبؤات الصحيحة: {correct_predictions}")
        st.write(f"❌ التنبؤات الخاطئة: {total_races - correct_predictions}")
        
        if car_accuracy_list:
            best_car = car_accuracy_list[0]
            worst_car = car_accuracy_list[-1]
            st.write(f"🏆 أفضل سيارة في التنبؤ: **{best_car[0]}** ({best_car[1]:.1f}%)")
            st.write(f"⚠️ أسوأ سيارة في التنبؤ: **{worst_car[0]}** ({worst_car[1]:.1f}%)")
        
        st.markdown("### نصائح لتحسين الدقة:")
        st.info(
            "1. ركز على السيارات ذات النسبة المنخفضة (< 70%)\n"
            "2. أكمل 50 جولة إضافية مع إدخال مواقع الطرق المخفية\\n"
            "3. الطريق الطويل (46%) غالبًا في الموضع L — ركز على هذا النمط"
        )
