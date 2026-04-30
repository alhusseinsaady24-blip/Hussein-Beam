import streamlit as st
import matplotlib.pyplot as plt
import io
import ezdxf
import numpy as np

# إعدادات الصفحة
st.set_page_config(page_title="Hussain Beam Pro", layout="wide")
st.title("Hussain Beam Pro - أداة تفريد وتسليح الكمرات")

# --- الجزء الأول: المدخلات ---
with st.sidebar:
    st.header("إعدادات القطاع")
    L = st.number_input("الطول الإجمالي (mm)", value=3000, step=100)
    t = st.number_input("العمق (mm)", value=600, step=50)
    col_w = st.number_input("عرض العمود (mm)", value=250, step=50)
    
    st.subheader("بيانات التسليح")
    top_txt = st.text_input("التسليح العلوي", "2 Φ 12")
    bot_txt = st.text_input("التسليح السفلي", "4 Φ 16")
    stirr_txt = st.text_input("الكانات", "5 Φ 8 / m'")
    
    cover = 25
    hook = 100 # طول الجنش

# --- الجزء الثاني: الرسم على صفحة الويب (Preview) ---
st.subheader("المعاينة الحية للقطاع الطولي")

fig, ax = plt.subplots(figsize=(12, 5))

# 1. رسم الخرسانة (الكمرة والأعمدة)
# جسم الكمرة
beam = plt.Rectangle((0, 0), L, t, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(beam)
# الأعمدة
left_col = plt.Rectangle((0, -200), col_w, 200, linewidth=2, edgecolor='black', facecolor='none')
right_col = plt.Rectangle((L - col_w, -200), col_w, 200, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(left_col)
ax.add_patch(right_col)

# 2. رسم الحديد العلوي (أزرق مع جنشات نازلة)
# المسار: (يمين تحت، يمين فوق، شمال فوق، شمال تحت)
top_x = [col_w - 50, col_w - 50, L - col_w + 50, L - col_w + 50]
top_y = [t - cover - hook, t - cover, t - cover, t - cover - hook]
ax.plot(top_x, top_y, color='blue', linewidth=2.5, label='Top Rebar')
ax.text(L/2, t - cover + 30, top_txt, color='blue', fontsize=12, ha='center', fontweight='bold')

# 3. رسم الحديد السفلي (أحمر مع جنشات طالعة)
# المسار: (شمال فوق، شمال تحت، يمين تحت، يمين فوق)
bot_x = [cover, cover, L - cover, L - cover]
bot_y = [cover + hook, cover, cover, cover + hook]
ax.plot(bot_x, bot_y, color='red', linewidth=3, label='Bottom Rebar')
ax.text(L/2, cover + 30, bot_txt, color='red', fontsize=12, ha='center', fontweight='bold')

# 4. رسم الكانات (أخضر موزع)
spacing = 200 # توزيع افتراضي
stirrup_pos = np.arange(col_w + 50, L - col_w, spacing)
for x in stirrup_pos:
    ax.plot([x, x], [cover, t - cover], color='green', linewidth=1, alpha=0.7)

ax.text(L/2, t/2, stirr_txt, color='green', fontsize=10, rotation=90, va='center', bbox=dict(facecolor='white', alpha=0.5))

# إعدادات لوحة الرسم
ax.set_xlim(-200, L + 200)
ax.set_ylim(-300, t + 200)
ax.set_aspect('equal')
ax.axis('off')

st.pyplot(fig)

# --- الجزء الثالث: كود الأوتوكاد (DXF) ---
def make_dxf():
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # رسم الخرسانة
    msp.add_lwpolyline([(0,0), (L,0), (L,t), (0,t), (0,0)])
    msp.add_lwpolyline([(0,-200), (col_w,-200), (col_w,0)])
    msp.add_lwpolyline([(L-col_w,-200), (L,-200), (L,0)])
    
    # رسم الحديد العلوي (أزرق - رقم 5)
    msp.add_lwpolyline([(top_x[0], top_y[0]), (top_x[1], top_y[1]), (top_x[2], top_y[2]), (top_x[3], top_y[3])], dxfattribs={'color': 5})
    
    # رسم الحديد السفلي (أحمر - رقم 1)
    msp.add_lwpolyline([(bot_x[0], bot_y[0]), (bot_x[1], bot_y[1]), (bot_x[2], bot_y[2]), (bot_x[3], bot_y[3])], dxfattribs={'color': 1})
    
    # رسم الكانات (أخضر - رقم 3)
    for x in stirrup_pos:
        msp.add_line((x, cover), (x, t - cover), dxfattribs={'color': 3})
    
    out = io.StringIO()
    doc.write(out)
    return out.getvalue()

st.download_button("تحميل ملف AutoCAD المطور", make_dxf(), "Beam_Shop_Drawing.dxf")