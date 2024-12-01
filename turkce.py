import streamlit as st
import re
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

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
