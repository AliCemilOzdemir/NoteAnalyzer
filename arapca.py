import streamlit as st
import re
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# العنوان
st.title("تطبيق محلل الدرجات باستخدام Streamlit")

# حالة عرض الصور
if "show_images" not in st.session_state:
    st.session_state.show_images = True  # الافتراضي: يتم عرض الصور

# منطقة إدخال البيانات في الشريط الجانبي
st.sidebar.header("حقول الإدخال")

# اختيار رفع ملف أو إدخال النصوص يدويًا
input_method = st.sidebar.radio(
    "كيف ستقدم الدرجات؟",
    options=["رفع ملف", "نسخ ولصق"]
)

uploaded_file = None
text_input = None

if input_method == "رفع ملف":
    uploaded_file = st.sidebar.file_uploader("قم برفع ملف الدرجات (TXT)", type=["txt"])
elif input_method == "نسخ ولصق":
    text_input = st.sidebar.text_area("قم بلصق الدرجات هنا", height=200)

# المعلمات الأخرى
lecture_name = st.sidebar.text_input("اسم المادة", value="اسم المادة")
perfect_score = st.sidebar.number_input("الدرجة الكاملة", value=100, step=1)
my_note = st.sidebar.number_input("درجتي", value=0.0, step=0.1)
note_s_axis_diff = st.sidebar.number_input("حجم خطوات المحور السيني للدرجات", value=5, step=1)
amount_s_axis_diff = st.sidebar.number_input("حجم خطوات المحور الصادي للتكرار", value=1, step=1)
first_step = st.sidebar.number_input("الخطوة الأولى", value=0, step=1)
increase_amount = st.sidebar.number_input("مقدار الزيادة", value=1, step=1)

if st.sidebar.button("تشغيل التحليل"):
    # إخفاء الصور عند النقر على الزر
    st.session_state.show_images = False

# عرض الصور فقط إذا كانت show_images صحيحة
if st.session_state.show_images:
    st.subheader("كيفية عمل التطبيق")

    # قائمة بأسماء ملفات الصور بالترتيب
    image_files = ["arabic/a.png", "arabic/b.png", "arabic/c.png", "arabic/d.png"]

    # عرض الصور واحدة تحت الأخرى
    for image_file in image_files:
        st.image(image_file, use_container_width=True)

# تحميل ومعالجة الدرجات (يعمل فقط إذا تم النقر على الزر)
if not st.session_state.show_images:
    if input_method == "رفع ملف" and uploaded_file is None:
        st.error("يرجى رفع ملف!")
    elif input_method == "نسخ ولصق" and not text_input:
        st.error("يرجى لصق الدرجات في مربع النص!")
    else:
        try:
            # قراءة المحتوى من الملف أو مربع النص
            if uploaded_file:
                content = uploaded_file.read().decode("utf-8")
            elif text_input:
                content = text_input

            # معالجة البيانات
            result = re.split(r'[ \n]+', content)

            # تنظيف وتصنيف البيانات
            notes_result = [x.strip() for x in result[first_step::increase_amount] if x.strip() != '∅' and x.strip() != "NA"]
            notes_result = list(map(lambda x: float(x), notes_result))
            notes_result = np.array(notes_result)

            # الإحصائيات
            average_x = np.average(notes_result)
            min_x = notes_result.min()
            max_x = notes_result.max()
            std = np.std(notes_result)
            z_score = (my_note - average_x) / std

            # عرض الإحصائيات
            st.subheader("المعلومات العامة")
            st.write(f"عدد المشاركين: {len(notes_result)}")
            st.write(f"أقل درجة: {min_x:.2f}")
            st.write(f"أعلى درجة: {max_x:.2f}")
            st.write(f"متوسط الدرجات: {average_x:.2f}")
            st.write(f"الانحراف المعياري: {std:.2f}")
            st.write(f"درجة Z: {z_score:.2f}")

            # إنشاء الرسم البياني
            st.subheader("رسم توزيع الدرجات")
            unique_values, counts = np.unique(notes_result, return_counts=True)
            plt.figure(figsize=(10, 6))
            bars = plt.bar(unique_values, counts, width=0.3)
            plt.axvline(x=average_x, color='red', linestyle='--')
            plt.text(average_x + 1.5, max(counts), 'متوسط الدرجات', color='red', rotation=0, ha='center', va='bottom')

            if my_note in unique_values:
                plt.text(my_note, counts[unique_values == my_note][0], 'درجتي', color='green', rotation=0, ha='center', va='bottom')

            for bar in bars:
                if bar.get_x() <= my_note < bar.get_x() + bar.get_width():
                    bar.set_color('green')

            plt.title(f'رسم توزيع الدرجات لمادة {lecture_name}')
            plt.xlabel('الدرجات')
            plt.ylabel('التكرار')
            plt.xticks(range(0, int(perfect_score), note_s_axis_diff), rotation=90)
            plt.yticks(range(0, max(counts), amount_s_axis_diff), rotation=0)

            # إضافة معلومات إلى الرسم البياني
            info_text = (
                f"عدد المشاركين: {len(notes_result)}\n"
                f"أقل درجة: {min_x:.2f}\n"
                f"أعلى درجة: {max_x:.2f}\n"
                f"درجتي: {my_note:.2f}\n"
                f"متوسط الدرجات: {average_x:.2f}\n"
                f"الانحراف المعياري: {std:.2f}\n"
                f"درجة Z: {z_score:.2f}"
            )
            plt.text(
                1.05 * max(unique_values), 0.8 * max(counts),
                info_text,
                fontsize=10,
                color="black",
                ha="left",
                va="top",
                bbox=dict(boxstyle="round,pad=0.3", edgecolor="blue", facecolor="lightgrey")
            )
            plt.subplots_adjust(left=0.055, bottom=0.065, right=0.90, top=0.962, wspace=0.2, hspace=0.2)

            # عرض الرسم البياني
            st.pyplot(plt)

            # زر لتحميل الرسم البياني
            buf = BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            st.download_button(
                label="تحميل الرسم البياني",
                data=buf,
                file_name="score_distribution.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"خطأ: {e}")

# التذييل
st.markdown("---")
st.write("تم التطوير بواسطة: علي جميل أوزدمير")
st.write("التاريخ: 01.12.2024")
st.write("للتعليقات والاقتراحات، يمكنك التواصل عبر: alicemilozdemir7@gmail.com")

# إضافة ملاحظة أسفل الزاوية اليمنى
st.markdown("""
    <p style="position:absolute; bottom:0px; right:0px; font-size: 12px; color: gray;">
        تم الإنشاء باستخدام محلل الدرجات
    </p>
    """, unsafe_allow_html=True)
