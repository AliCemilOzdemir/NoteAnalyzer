import streamlit as st
import re
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

def run_turkish():
    # Başlık
    st.title("Note Analyzer Streamlit Uygulaması")

    # Uygulamanın çalışma prensibi görüntüleme durumu
    if "show_images" not in st.session_state:
        st.session_state.show_images = True  # Varsayılan olarak resimler gösterilsin

    # Kullanıcıdan veri alma (Sidebar sabit kalıyor)
    st.sidebar.header("Girdi Alanları")

    # Dosya yükleme veya metin girişi seçimi
    input_method = st.sidebar.radio(
        "Notları nasıl gireceksiniz?",
        options=["Dosya Yükle", "Kopyala-Yapıştır"]
    )

    uploaded_file = None
    text_input = None

    if input_method == "Dosya Yükle":
        uploaded_file = st.sidebar.file_uploader("Notlar Dosyasını Yükleyin (TXT)", type=["txt"])
    elif input_method == "Kopyala-Yapıştır":
        text_input = st.sidebar.text_area("Notları Yapıştırın", height=200)

    # Diğer parametreler
    lecture_name = st.sidebar.text_input("Ders Adı", value="Ders Adı")
    perfect_score = st.sidebar.number_input("Sınav Puanı Üst Limiti", value=100, step=1)
    my_note = st.sidebar.number_input("Benim Notum", value=0.0, step=0.1)
    note_s_axis_diff = st.sidebar.number_input("Notlar X Ekseni Ortak Farkı", value=5, step=1)
    amount_s_axis_diff = st.sidebar.number_input("Miktar Y Ekseni Ortak Farkı", value=1, step=1)
    first_step = st.sidebar.number_input("İlk Adım", value=0, step=1)
    increase_amount = st.sidebar.number_input("Artış Miktarı", value=1, step=1)

    if st.sidebar.button("Analizi Çalıştır"):
        # Butona basıldığında resimleri gizle
        st.session_state.show_images = False

    # Resimler yalnızca show_images True ise gösterilir
    if st.session_state.show_images:
        st.subheader("Uygulamanın Çalışma Prensibi")

        # Resimlerin dosya isimlerini sırayla listele
        image_files = ["turkish/a.png", "turkish/b.png", "turkish/c.png", "turkish/d.png"]

        # Resimleri alt alta ekle
        for image_file in image_files:
            st.image(image_file, use_container_width=True)

    # Notları yükleme ve işleme işlemleri (Butona basıldıysa çalışır)
    if not st.session_state.show_images:
        if input_method == "Dosya Yükle" and uploaded_file is None:
            st.error("Lütfen bir dosya yükleyin!")
        elif input_method == "Kopyala-Yapıştır" and not text_input:
            st.error("Lütfen notları metin kutusuna yapıştırın!")
        else:
            try:
                # Dosya veya metin kutusundan içerik okuma
                if uploaded_file:
                    content = uploaded_file.read().decode("utf-8")
                elif text_input:
                    content = text_input

                # Veriyi işleme
                result = re.split(r'[ \n]+', content)

                # Strip fonksiyonu ve kaçış dizisi temizliği
                notes_result = [x.strip() for x in result[first_step::increase_amount] if x.strip() != '∅' and x.strip() != "NA"]
                notes_result = list(map(lambda x: float(x), notes_result))
                notes_result = np.array(notes_result)

                # İstatistikler
                average_x = np.average(notes_result)
                min_x = notes_result.min()
                max_x = notes_result.max()
                std = np.std(notes_result)
                z_score = (my_note - average_x) / std

                # İstatistikleri ekrana yazdırma
                st.subheader("Genel Bilgiler")
                st.write(f"Katilimci Sayısı: {len(notes_result)}")
                st.write(f"En Düşük Not: {min_x:.2f}")
                st.write(f"En Yüksek Not: {max_x:.2f}")
                st.write(f"Ortalama Not: {average_x:.2f}")
                st.write(f"Standart Sapma: {std:.2f}")
                st.write(f"Z-Skoru: {z_score:.2f}")

                # Grafik oluşturma
                st.subheader("Not Dağılım Grafiği")
                unique_values, counts = np.unique(notes_result, return_counts=True)
                plt.figure(figsize=(10, 6))
                bars = plt.bar(unique_values, counts, width=0.3)
                plt.axvline(x=average_x, color='red', linestyle='--')
                plt.text(average_x + 1.5, max(counts), 'Ortalama Not', color='red', rotation=0, ha='center', va='bottom')

                if my_note in unique_values:
                    plt.text(my_note, counts[unique_values == my_note][0], 'Benim\nNotum', color='green', rotation=0, ha='center', va='bottom')

                for bar in bars:
                    if bar.get_x() <= my_note < bar.get_x() + bar.get_width():
                        bar.set_color('green')

                plt.title(f'{lecture_name} Not Sayıları Grafiği')
                plt.xlabel('Notlar')
                plt.ylabel('Adet')
                plt.xticks(range(0, int(perfect_score), note_s_axis_diff), rotation=90)
                plt.yticks(range(0, max(counts), amount_s_axis_diff), rotation=0)

                # Grafik bilgileri
                info_text = (
                    f"Katilimci sayısı: {len(notes_result)}\n"
                    f"En düşük not: {min_x:.2f}\n"
                    f"En yüksek not: {max_x:.2f}\n"
                    f"Benim notum: {my_note:.2f}\n"
                    f"Ortalama not: {average_x:.2f}\n"
                    f"Standart sapma: {std:.2f}\n"
                    f"Z-skoru: {z_score:.2f}"
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
                
                # Sağ alt köşeye "Generated by Note Analyzer" metni ekle
                plt.text(
                    0.99, -0.15,  # Sağ alt köşeye konumlandır
                    "Generated by Note Analyzer at HuggingFace aliicemill/NoteAnalyzer space",
                    fontsize=8,
                    color="gray",
                    ha="right",
                    va="top",
                    transform=plt.gca().transAxes  # Koordinatları grafiğe göre ayarla
                )

                # Grafik gösterimi
                st.pyplot(plt)

                # Grafik indirme bağlantısı
                buf = BytesIO()
                plt.savefig(buf, format="png")
                buf.seek(0)
                st.download_button(
                    label="Grafiği İndir",
                    data=buf,
                    file_name="not_dagilimi.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Hata: {e}")

    # Web sayfasının altına isim ve tarih
    st.markdown("---")
    st.write("Developed by: Ali Cemil Özdemir")
    st.write("Date: 01.12.2024")
    st.write("For feedback and suggestions, you can contact me at alicemilozdemir7@gmail.com")

    # Grafiklerin sağ alt köşesine yazı ekleme
    st.markdown("""
        <p style="position:absolute; bottom:0px; right:0px; font-size: 12px; color: gray;">
            Created with Note Analyzer
        </p>
        """, unsafe_allow_html=True)


def run_arabic():
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
                # Sağ alt köşeye "Generated by Note Analyzer" metni ekle
                plt.text(
                    0.99, -0.15,  # Sağ alt köşeye konumlandır
                    "Generated by Note Analyzer at HuggingFace aliicemill/NoteAnalyzer space",
                    fontsize=8,
                    color="gray",
                    ha="right",
                    va="top",
                    transform=plt.gca().transAxes  # Koordinatları grafiğe göre ayarla
                )
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


def run_english():
    # Title
    st.title("Note Analyzer Streamlit Application")

    # Image display state
    if "show_images" not in st.session_state:
        st.session_state.show_images = True  # Default: images are shown

    # Sidebar input area
    st.sidebar.header("Input Fields")

    # File upload or text input selection
    input_method = st.sidebar.radio(
        "How will you provide the notes?",
        options=["Upload File", "Copy-Paste"]
    )

    uploaded_file = None
    text_input = None

    if input_method == "Upload File":
        uploaded_file = st.sidebar.file_uploader("Upload the Notes File (TXT)", type=["txt"])
    elif input_method == "Copy-Paste":
        text_input = st.sidebar.text_area("Paste the Notes Here", height=200)

    # Other parameters
    lecture_name = st.sidebar.text_input("Course Name", value="Course Name")
    perfect_score = st.sidebar.number_input("Maximum Exam Score", value=100, step=1)
    my_note = st.sidebar.number_input("My Score", value=0.0, step=0.1)
    note_s_axis_diff = st.sidebar.number_input("Score X-Axis Step Size", value=5, step=1)
    amount_s_axis_diff = st.sidebar.number_input("Frequency Y-Axis Step Size", value=1, step=1)
    first_step = st.sidebar.number_input("First Step", value=0, step=1)
    increase_amount = st.sidebar.number_input("Step Increase", value=1, step=1)

    if st.sidebar.button("Run Analysis"):
        # Hide images when the button is clicked
        st.session_state.show_images = False

    # Show images only if show_images is True
    if st.session_state.show_images:
        st.subheader("How the Application Works")

        # List the image filenames in order
        image_files = ["english/a.png", "english/b.png", "english/c.png", "english/d.png"]

        # Display images one below the other
        for image_file in image_files:
            st.image(image_file, use_container_width=True)

    # Load and process notes (Only works if the button is clicked)
    if not st.session_state.show_images:
        if input_method == "Upload File" and uploaded_file is None:
            st.error("Please upload a file!")
        elif input_method == "Copy-Paste" and not text_input:
            st.error("Please paste the notes into the text area!")
        else:
            try:
                # Read content from file or text area
                if uploaded_file:
                    content = uploaded_file.read().decode("utf-8")
                elif text_input:
                    content = text_input

                # Process the data
                result = re.split(r'[ \n]+', content)

                # Clean and filter the data
                notes_result = [x.strip() for x in result[first_step::increase_amount] if x.strip() != '∅' and x.strip() != "NA"]
                notes_result = list(map(lambda x: float(x), notes_result))
                notes_result = np.array(notes_result)

                # Statistics
                average_x = np.average(notes_result)
                min_x = notes_result.min()
                max_x = notes_result.max()
                std = np.std(notes_result)
                z_score = (my_note - average_x) / std

                # Display statistics
                st.subheader("General Information")
                st.write(f"Number of Participants: {len(notes_result)}")
                st.write(f"Lowest Score: {min_x:.2f}")
                st.write(f"Highest Score: {max_x:.2f}")
                st.write(f"Average Score: {average_x:.2f}")
                st.write(f"Standard Deviation: {std:.2f}")
                st.write(f"Z-Score: {z_score:.2f}")

                # Create plot
                st.subheader("Score Distribution Graph")
                unique_values, counts = np.unique(notes_result, return_counts=True)
                plt.figure(figsize=(10, 6))
                bars = plt.bar(unique_values, counts, width=0.3)
                plt.axvline(x=average_x, color='red', linestyle='--')
                plt.text(average_x + 1.5, max(counts), 'Average Score', color='red', rotation=0, ha='center', va='bottom')

                if my_note in unique_values:
                    plt.text(my_note, counts[unique_values == my_note][0], 'My\nScore', color='green', rotation=0, ha='center', va='bottom')

                for bar in bars:
                    if bar.get_x() <= my_note < bar.get_x() + bar.get_width():
                        bar.set_color('green')

                plt.title(f'{lecture_name} Score Distribution')
                plt.xlabel('Scores')
                plt.ylabel('Count')
                plt.xticks(range(0, int(perfect_score), note_s_axis_diff), rotation=90)
                plt.yticks(range(0, max(counts), amount_s_axis_diff), rotation=0)

                # Add graph information
                info_text = (
                    f"Number of participants: {len(notes_result)}\n"
                    f"Lowest score: {min_x:.2f}\n"
                    f"Highest score: {max_x:.2f}\n"
                    f"My score: {my_note:.2f}\n"
                    f"Average score: {average_x:.2f}\n"
                    f"Standard deviation: {std:.2f}\n"
                    f"Z-score: {z_score:.2f}"
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
                # Sağ alt köşeye "Generated by Note Analyzer" metni ekle
                plt.text(
                    0.99, -0.15,  # Sağ alt köşeye konumlandır
                    "Generated by Note Analyzer at HuggingFace aliicemill/NoteAnalyzer space",
                    fontsize=8,
                    color="gray",
                    ha="right",
                    va="top",
                    transform=plt.gca().transAxes  # Koordinatları grafiğe göre ayarla
                )

                # Display the plot
                st.pyplot(plt)

                # Download button for the plot
                buf = BytesIO()
                plt.savefig(buf, format="png")
                buf.seek(0)
                st.download_button(
                    label="Download Graph",
                    data=buf,
                    file_name="score_distribution.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Error: {e}")

    # Footer
    st.markdown("---")
    st.write("Developed by: Ali Cemil Özdemir")
    st.write("Date: 01.12.2024")
    st.write("For feedback and suggestions, you can contact me at alicemilozdemir7@gmail.com")

    # Add a note at the bottom right corner of the page
    st.markdown("""
        <p style="position:absolute; bottom:0px; right:0px; font-size: 12px; color: gray;">
            Created with Note Analyzer
        </p>
        """, unsafe_allow_html=True)

# Session State'i başlat
if "language" not in st.session_state:
    st.session_state.language = None

# Dil seçimi ekranı
if st.session_state.language is None:
    st.title("Select language / Dili seçin / اختر اللغة")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Türkçe"):
            st.session_state.language = "turkish"
    with col2:
        if st.button("English"):
            st.session_state.language = "english"
    with col3:
        if st.button("عربي"):
            st.session_state.language = "arabic"

# Seçilen dilin programını çalıştır
else:
    if st.session_state.language == "turkish":
        run_turkish()
    elif st.session_state.language == "english":
        run_english()
    elif st.session_state.language == "arabic":
        run_arabic()
