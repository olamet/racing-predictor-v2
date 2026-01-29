import streamlit as st
import pandas as pd
from supabase import create_client
import io

# --- تهيئة Supabase ---
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"❌ خطأ في تهيئة Supabase: {str(e)}")
    st.stop()

# --- دالة تحميل البيانات من Supabase ---
def load_history():
    try:
        response = supabase.table('races').select('*').execute()
        if response.data:
            # إزالة الحقل 'id' غير الضروري
            return [{k: v for k, v in row.items() if k != 'id'} for row in response.data]
        return []
    except Exception as e:
        st.sidebar.warning(f"⚠️ لم يتم تحميل البيانات: {str(e)}")
        return []

# --- دالة حفظ البيانات في Supabase ---
def save_history():
    try:
        # حذف جميع السجلات القديمة
        supabase.table('races').delete().neq('id', 0).execute()
        # إدخال السجلات الجديدة
        supabase.table('races').insert(st.session_state.history).execute()
        return True
    except Exception as e:
        st.sidebar.error(f"❌ فشل الحفظ: {str(e)}")
        return False

# --- تهيئة التطبيق ---
if 'history' not in st.session_state:
    st.session_state.history = load_history()

# --- الشريط الجانبي ---
st.sidebar.title("Racing Predictor Pro")
page = st.sidebar.radio("اختر الصفحة", ["الرئيسية", "نسبة الربح"])

# --- زر رفع البيانات ---
st.sidebar.markdown("---")
st.sidebar.subheader("📥 استعادة البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف CSV", type=["csv"])
if uploaded_file is not None and 'upload_processed' not in st.session_state:
    try:
        df = pd.read_csv(uploaded_file)
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])
        
        restored = []
        for _, row in df.iterrows():
            # تحليل Hidden_Details
            h1, p1, h2, p2 = "dirt", "C", "potholes", "R"
            if 'Hidden_Details' in row and pd.notna(row['Hidden_Details']):
                parts = str(row['Hidden_Details']).split('+')
                if len(parts) == 2:
                    try:
                        h1 = parts[0].split('(')[0].strip()
                        p1 = parts[0].split('(')[1].replace(')', '').strip()
                        h2 = parts[1].split('(')[0].strip()
                        p2 = parts[1].split('(')[1].replace(')', '').strip()
                    except:
                        pass
            
            restored.append({
                "Position": row.get("Position", "C"),
                "Road": row.get("Road", "expressway"),
                "Hidden_Road_1": h1,
                "Hidden_Road_1_Position": p1,
                "Hidden_Road_2": h2,
                "Hidden_Road_2_Position": p2,
                "Long_Road": row.get("Long_Road", "المرئي"),
                "Car1": row.get("Car1", "Car"),
                "Car2": row.get("Car2", "Sport"),
                "Car3": row.get("Car3", "Super"),
                "Winner": row.get("Winner", "Car"),
                "Prediction": row.get("Prediction", row.get("Car1", "Car")),
                "Prediction_Method": row.get("Prediction_Method", "Restored")
            })
        
        st.session_state.history = restored
        st.session_state.upload_processed = True
        
        if save_history():
            st.sidebar.success(f"✅ تم استعادة {len(restored)} سباق!")
            st.sidebar.balloons()
            st.rerun()
        else:
            st.sidebar.error("❌ فشل الحفظ")
    except Exception as e:
        st.sidebar.error(f"❌ خطأ: {str(e)}")
# --- زر تنزيل البيانات ---
st.sidebar.markdown("---")
st.sidebar.subheader("📤 تصدير البيانات")
if st.sidebar.button("تنزيل CSV"):
    try:
        df = pd.DataFrame(st.session_state.history)
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.sidebar.download_button(
            "⬇️ حمل الملف",
            data=csv,
            file_name="racing_backup.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.sidebar.error(f"❌ خطأ: {str(e)}")

# --- باقي الكود (الرئيسية ونسبة الربح) ---
if page == "الرئيسية":
    st.title("Racing Predictor Pro")
    st.markdown("تنبؤ ذكي مع تحديد الطريق الأطول بدقة")
    
    col1, col2 = st.columns(2)
    with col1:
        position = st.selectbox("Visible Road Position", ["L", "C", "R"])
        road = st.selectbox("Visible Road Type", ["expressway", "highway", "dirt", "potholes", "bumpy", "desert"])
    with col2:
        car1 = st.selectbox("Car 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "ORV", "SUV", "Truck", "ATV"])
        car2 = st.selectbox("Car 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "ORV", "SUV", "Truck", "ATV"])
        car3 = st.selectbox("Car 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "ORV", "SUV", "Truck", "ATV"])
    
    cars = [car1, car2, car3]
    
    st.markdown("---")
    st.subheader("التنبؤ الذكي")
    
    weight_map = {"L": 0.8, "C": 1.0, "R": 1.3}
    weight = weight_map[position]
    
    hidden_roads_map = {
        "expressway": ["highway", "bumpy"],
        "highway": ["expressway", "dirt"],
        "dirt": ["potholes", "desert"],
        "potholes": ["dirt", "bumpy"],
        "bumpy": ["highway", "potholes"],
        "desert": ["dirt", "potholes"]
    }
    
    hidden_roads = hidden_roads_map.get(road, ["dirt", "potholes"])
    hidden_positions = ["C", "C"]
    if st.session_state.history and len(st.session_state.history) > 20:
        hist_temp = pd.DataFrame(st.session_state.history)
        if 'Hidden_Road_1' in hist_temp.columns and 'Hidden_Road_1_Position' in hist_temp.columns:
            road_matches = hist_temp[
                (hist_temp['Road'] == road) & 
                (hist_temp['Position'] == position)
            ]
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
    
    long_road = "المرئي"
    if st.session_state.history and len(st.session_state.history) > 20:
        hist_temp = pd.DataFrame(st.session_state.history)
        if 'Long_Road' in hist_temp.columns:
            road_matches = hist_temp[
                (hist_temp['Road'] == road) & 
                (hist_temp['Position'] == position)
            ]
            if not road_matches.empty:
                mode_series = road_matches['Long_Road'].mode()
                if not mode_series.empty:
                    long_road = mode_series.iloc[0]
    
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
            combined_times = []
            
            for car in cars:
                car_idx = ["Car", "Sport", "Super", "Bigbike", "Moto", "ORV", "SUV", "Truck", "ATV"].index(car)
                speed_data = {
                    "expressway": [264, 432, 480, 264, 220.8, 286, 348, 240, 115.2],
                    "highway": [290.4, 480, 528, 230.4, 225.6, 240, 360, 276, 115.2],
                    "dirt": [153.6, 360, 264, 165.6, 144, 220.8, 336, 87.6, 187.2],
                    "potholes": [67.2, 57.6, 52.8, 187.2, 96, 134.4, 110.4, 108, 144],
                    "bumpy": [98.4, 168, 151.2, 259.2, 108, 218.4, 213.6, 216, 187.2],
                    "desert": [132, 96, 62.4, 132, 72, 58.08, 139.2, 98.28, 168]
                }
                
                visible_speed = speed_data[road][car_idx] * weight
                
                h1_weight = weight_map.get(hidden_positions[0], 1.0)
                h2_weight = weight_map.get(hidden_positions[1], 1.0)
                hidden_speed1 = speed_data[hidden_roads[0]][car_idx] * h1_weight
                hidden_speed2 = speed_data[hidden_roads[1]][car_idx] * h2_weight
                
                if long_road == "المرئي":
                    time_visible = 0.46 / visible_speed
                    time_hidden1 = 0.27 / hidden_speed1
                    time_hidden2 = 0.27 / hidden_speed2
                elif long_road == "المخفي الأول":
                    time_visible = 0.27 / visible_speed
                    time_hidden1 = 0.46 / hidden_speed1
                    time_hidden2 = 0.27 / hidden_speed2
                else:
                    time_visible = 0.27 / visible_speed
                    time_hidden1 = 0.27 / hidden_speed1
                    time_hidden2 = 0.46 / hidden_speed2
                
                total_time = time_visible + time_hidden1 + time_hidden2
                
                combined_times.append(total_time)
            
            prediction = cars[combined_times.index(min(combined_times))]
            prediction_method = f"المدمج (الطريق الأطول: {long_road})"
    else:
        combined_times = []
        
        for car in cars:
            car_idx = ["Car", "Sport", "Super", "Bigbike", "Moto", "ORV", "SUV", "Truck", "ATV"].index(car)
            speed_data = {
                "expressway": [264, 432, 480, 264, 220.8, 286, 348, 240, 115.2],
                "highway": [290.4, 480, 528, 230.4, 225.6, 240, 360, 276, 115.2],
                "dirt": [153.6, 360, 264, 165.6, 144, 220.8, 336, 87.6, 187.2],
                "potholes": [67.2, 57.6, 52.8, 187.2, 96, 134.4, 110.4, 108, 144],
                "bumpy": [98.4, 168, 151.2, 259.2, 108, 218.4, 213.6, 216, 187.2],
                "desert": [132, 96, 62.4, 132, 72, 58.08, 139.2, 98.28, 168]
            }
            
            visible_speed = speed_data[road][car_idx] * weight
            
            h1_weight = weight_map.get(hidden_positions[0], 1.0)
            h2_weight = weight_map.get(hidden_positions[1], 1.0)
            hidden_speed1 = speed_data[hidden_roads[0]][car_idx] * h1_weight
            hidden_speed2 = speed_data[hidden_roads[1]][car_idx] * h2_weight
            
            if long_road == "المرئي":
                time_visible = 0.46 / visible_speed
                time_hidden1 = 0.27 / hidden_speed1
                time_hidden2 = 0.27 / hidden_speed2
            elif long_road == "المخفي الأول":
                time_visible = 0.27 / visible_speed
                time_hidden1 = 0.46 / hidden_speed1
                time_hidden2 = 0.27 / hidden_speed2
            else:
                time_visible = 0.27 / visible_speed
                time_hidden1 = 0.27 / hidden_speed1
                time_hidden2 = 0.46 / hidden_speed2
            
            total_time = time_visible + time_hidden1 + time_hidden2
            
            combined_times.append(total_time)
        
        prediction = cars[combined_times.index(min(combined_times))]
        prediction_method = f"الوقت (الطريق الأطول: {long_road})"
    
    st.success(f"التنبؤ: **{prediction}**")
    st.caption(f"الطريقة: {prediction_method}")
    st.caption(f"الطرق المخفية: {hidden_roads[0]} ({hidden_positions[0]}) + {hidden_roads[1]} ({hidden_positions[1]})")
    
    st.markdown("---")
    actual_winner = st.selectbox("Actual Winner", cars)
    
    st.subheader("الطرق المخفية الفعلية")
    hidden_road1 = st.selectbox("الطريق المخفي الأول", ["expressway", "highway", "dirt", "potholes", "bumpy", "desert"], key="hr1")
    hidden_road1_pos = st.selectbox("موضع الطريق الأول", ["L", "C", "R"], key="hr1p")
    hidden_road2 = st.selectbox("الطريق المخفي الثاني", ["expressway", "highway", "dirt", "potholes", "bumpy", "desert"], key="hr2")
    hidden_road2_pos = st.selectbox("موضع الطريق الثاني", ["L", "C", "R"], key="hr2p")
    
    st.subheader("تحديد الطريق الأطول")
    long_road_index = st.radio(
        "أي طريق هو الأطول؟",
        options=["المرئي", "المخفي الأول", "المخفي الثاني"],
        key="long_road"
    )
    
    if st.button("Save This Race"):
        st.session_state.history.append({
            "Position": position,
            "Road": road,
            "Hidden_Road_1": hidden_road1,
            "Hidden_Road_1_Position": hidden_road1_pos,
            "Hidden_Road_2": hidden_road2,
            "Hidden_Road_2_Position": hidden_road2_pos,
            "Long_Road": long_road_index,
            "Car1": car1,
            "Car2": car2,
            "Car3": car3,
            "Winner": actual_winner,
            "Prediction": prediction,
            "Prediction_Method": prediction_method
        })
        if save_history():
            st.balloons()
            st.success(f"تم الحفظ! الإجمالي: {len(st.session_state.history)}")
        else:
            st.error("فشل الحفظ! تأكد من الصلاحيات.")
    
    if st.session_state.history:
        st.markdown("---")
        st.subheader("سجل السباقات")
        display_df = pd.DataFrame(st.session_state.history)
        if 'Hidden_Road_1_Position' in display_df.columns and 'Long_Road' in display_df.columns:
            display_df['Hidden_Details'] = (
                display_df['Hidden_Road_1'] + ' (' + display_df['Hidden_Road_1_Position'] + ') + ' +
                display_df['Hidden_Road_2'] + ' (' + display_df['Hidden_Road_2_Position'] + ')'
            )
            cols_to_show = ['Position', 'Road', 'Hidden_Details', 'Long_Road', 'Car1', 'Car2', 'Car3', 'Winner', 'Prediction']
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
        for car in ["Car", "Sport", "Super", "Bigbike", "Moto", "ORV", "SUV", "Truck", "ATV"]:
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
        st.info(            "1. ركز على السيارات ذات النسبة المنخفضة (< 70%)\n"
            "2. أكمل 50 جولة إضافية مع تحديد الطريق الأطول بدقة\\n"
            "3. الطريق الأطول قد يكون في أي موضع (L/C/R) — لا تفترض أنه دائمًا في L"
        )
