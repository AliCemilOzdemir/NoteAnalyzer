import streamlit as st
import re
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

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
