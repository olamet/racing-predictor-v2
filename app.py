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

page = st.sidebar.radio("اختر الصفحة", ["الرئيسية", "📊 نسبة الربح"])

if page == "الرئيسية":
    st.title("Racing Predictor Pro")
    st.markdown("تنبؤ ذكي مع تحسين تلقائي")
    
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
    
    hidden_roads_map = {
        "expressway": ["highway", "bumpy"],
        "highway": ["expressway", "dirt"],        "dirt": ["potholes", "desert"],
        "potholes": ["dirt", "bumpy"],
        "bumpy": ["highway", "potholes"],
        "desert": ["dirt", "potholes"]
    }
    hidden_roads = hidden_roads_map.get(road, ["dirt", "potholes"])
    
    weight_map = {"L": 0.8, "C": 1.0, "R": 1.3}
    weight = weight_map[position]
    
    # --- التنبؤ الذكي ---
    prediction_method = ""
    
    # 1. التحقق من وجود بيانات تاريخية كافية
    if st.session_state.history and len(st.session_state.history) > 20:
        hist_df = pd.DataFrame(st.session_state.history)
        
        # البحث عن جولات مشابهة (ليس بالضرورة مطابقة تمامًا)
        similar_matches = hist_df[
            (hist_df['Position'] == position) &
            (hist_df['Road'] == road) &
            (hist_df['Car1'].isin(cars)) &
            (hist_df['Car2'].isin(cars)) &
            (hist_df['Car3'].isin(cars))
        ]
        
        # 2. إذا وجدنا 5 جولات مشابهة على الأقل
        if len(similar_matches) >= 5:
            # حساب عدد الانتصارات لكل سيارة في الظروف المشابهة
            win_counts = {}
            for car in cars:
                wins = len(similar_matches[similar_matches['Winner'] == car])
                win_counts[car] = wins
            
            # اختيار السيارة ذات أكبر عدد انتصارات
            prediction = max(win_counts, key=win_counts.get)
            prediction_method = "📊 التاريخي (دقة عالية)"
        else:
            # 3. نموذج مدمج عندما تكون البيانات غير كافية
            combined_speeds = []
            for car in cars:
                car_idx = speed_data["Vehicle"].index(car)
                visible_speed = speed_data[road][car_idx] * weight
                hidden_speed1 = speed_data[hidden_roads[0]][car_idx]
                hidden_speed2 = speed_data[hidden_roads[1]][car_idx]
                combined_speed = (visible_speed * 0.7) + (hidden_speed1 * 0.15) + (hidden_speed2 * 0.15)
                combined_speeds.append(combined_speed)
            
            prediction = cars[combined_speeds.index(max(combined_speeds))]
            prediction_method = "⚡ المدمج (السرعة + التاريخ)"    
        else:
        # 4. الاعتماد على السرعة عند نقص البيانات
        combined_speeds = []
        for car in cars:
            car_idx = speed_data["Vehicle"].index(car)
            visible_speed = speed_data[road][car_idx] * weight
            hidden_speed1 = speed_data[hidden_roads[0]][car_idx]
            hidden_speed2 = speed_data[hidden_roads[1]][car_idx]
            combined_speed = (visible_speed * 0.6) + (hidden_speed1 * 0.2) + (hidden_speed2 * 0.2)
            combined_speeds.append(combined_speed)
        
        prediction = cars[combined_speeds.index(max(combined_speeds))]
        prediction_method = "🚀 السرعة (بيانات أولية)"
    
    # --- عرض النتيجة ---
    st.success(f"التنبؤ: **{prediction}**")
    st.caption(f"الطريقة المستخدمة: {prediction_method}")
    
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

elif page == "📊 نسبة الربح":
    st.title("📊 نسبة ربح التوقعات")
    
    if not st.session_state.history or len(st.session_state.history) < 10:
        st.warning("يجب أن يكون لديك 10 جولات على الأقل لحساب النسبة. أنت لديك الآن: " + str(len(st.session_state.history)))
    else:
        hist_df = pd.DataFrame(st.session_state.history)
        
        speed_data_dict = {}
        for i, vehicle in enumerate(speed_data["Vehicle"]):
            speed_data_dict[vehicle] = [
                speed_data["expressway"][i],                speed_data["highway"][i],
                speed_data["dirt"][i],
                speed_data["potholes"][i],
                speed_data["bumpy"][i],
                speed_data["desert"][i]
            ]
        
        road_index = {
            "expressway": 0,
            "highway": 1,
            "dirt": 2,
            "potholes": 3,
            "bumpy": 4,
            "desert": 5
        }
        
        correct_smart = 0
        total_races = len(hist_df)
        
        for idx, row in hist_df.iterrows():
            cars = [row['Car1'], row['Car2'], row['Car3']]
            position = row['Position']
            road = row['Road']
            
            # --- إعادة حساب التنبؤ الذكي ---
            prediction_method = ""
            prediction = cars[0]  # افتراضي
            
            if len(st.session_state.history) > 20:
                # البحث عن جولات مشابهة
                similar_matches = hist_df[
                    (hist_df['Position'] == position) &
                    (hist_df['Road'] == road) &
                    (hist_df['Car1'].isin(cars)) &
                    (hist_df['Car2'].isin(cars)) &
                    (hist_df['Car3'].isin(cars))
                ]
                
                if len(similar_matches) >= 5:
                    win_counts = {}
                    for car in cars:
                        wins = len(similar_matches[similar_matches['Winner'] == car])
                        win_counts[car] = wins
                    prediction = max(win_counts, key=win_counts.get)
                else:
                    # نموذج مدمج
                    weight = {"L": 0.8, "C": 1.0, "R": 1.3}[position]
                    hidden_roads = {
                        "expressway": ["highway", "bumpy"],
                        "highway": ["expressway", "dirt"],                        "dirt": ["potholes", "desert"],
                        "potholes": ["dirt", "bumpy"],
                        "bumpy": ["highway", "potholes"],
                        "desert": ["dirt", "potholes"]
                    }.get(road, ["dirt", "potholes"])
                    
                    combined_speeds = []
                    for car in cars:
                        visible_speed = speed_data_dict[car][road_index[road]] * weight
                        hidden_speed1 = speed_data_dict[car][road_index[hidden_roads[0]]]
                        hidden_speed2 = speed_data_dict[car][road_index[hidden_roads[1]]]
                        combined_speed = (visible_speed * 0.7) + (hidden_speed1 * 0.15) + (hidden_speed2 * 0.15)
                        combined_speeds.append(combined_speed)
                    
                    prediction = cars[combined_speeds.index(max(combined_speeds))]
            else:
                # نموذج السرعة
                weight = {"L": 0.8, "C": 1.0, "R": 1.3}[position]
                hidden_roads = {
                    "expressway": ["highway", "bumpy"],
                    "highway": ["expressway", "dirt"],
                    "dirt": ["potholes", "desert"],
                    "potholes": ["dirt", "bumpy"],
                    "bumpy": ["highway", "potholes"],
                    "desert": ["dirt", "potholes"]
                }.get(road, ["dirt", "potholes"])
                
                combined_speeds = []
                for car in cars:
                    visible_speed = speed_data_dict[car][road_index[road]] * weight
                    hidden_speed1 = speed_data_dict[car][road_index[hidden_roads[0]]]
                    hidden_speed2 = speed_data_dict[car][road_index[hidden_roads[1]]]
                    combined_speed = (visible_speed * 0.6) + (hidden_speed1 * 0.2) + (hidden_speed2 * 0.2)
                    combined_speeds.append(combined_speed)
                
                prediction = cars[combined_speeds.index(max(combined_speeds))]
            
            actual = row['Winner']
            if prediction == actual:
                correct_smart += 1
        
        accuracy_smart = (correct_smart / total_races) * 100
        
        st.metric("نسبة النجاح الذكية", f"{accuracy_smart:.1f}%")
        st.progress(accuracy_smart / 100)
        
        st.markdown("---")
        st.subheader("التفاصيل")
        st.write(f"✅ التخمينات الصحيحة: {correct_smart}/{total_races}")
        st.write(f"📈 الهدف: 95%+ (كلما زادت البيانات، زادت الدقة)")        
        # نصائح تحسين
        st.markdown("### نصائح لتحسين الدقة:")
        st.info("1. أكمل 50 جولة إضافية\n2. ركز على الظروف النادرة (L + desert + سيارات ثقيلة)\n3. حافظ على تناسق إدخال البيانات")
