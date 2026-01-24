import streamlit as st
import pandas as pd

# --- جدول السرعات ---
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

# --- تخزين الجولات ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- الواجهة ---
st.title("🏎️ Racing Car Predictor")
st.write("أدخل تفاصيل الجولة للحصول على تنبؤ ذكي!")

col1, col2 = st.columns(2)
with col1:
    position = st.selectbox("📍 موقع الطريق الظاهر", ["L", "C", "R"])
    road = st.selectbox("🛣️ نوع الطريق الظاهر", list(df_speed.columns))
with col2:
    car1 = st.selectbox("🚗 السيارة 1", df_speed.index.tolist())
    car2 = st.selectbox("🚗 السيارة 2", df_speed.index.tolist())
    car3 = st.selectbox("🚗 السيارة 3", df_speed.index.tolist())

# --- التنبؤ بالسرعة ---
cars = [car1, car2, car3]
speeds = [df_speed.loc[car, road] for car in cars]
fastest_by_speed = cars[speeds.index(max(speeds))]

# --- عرض النتيجة ---
st.subheader("📊 التنبؤ:")
st.success(f"السيارة الأسرع على {road}: **{fastest_by_speed}**")

# --- تسجيل الجولة ---
actual_winner = st.selectbox("🏆 الفائز الفعلي", cars)
if st.button("💾 حفظ الجولة"):
    st.session_state.history.append({
        "Position": position,
        "Road": road,
        "Car1": car1,
        "Car2": car2,
        "Car3": car3,
        "Winner": actual_winner
    })
    st.balloons()
    st.success("تم حفظ الجولة بنجاح!")

# --- عرض السجل ---
if st.session_state.history:
    st.subheader("📜 سجلك التاريخي:")
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df, use_container_width=True)
