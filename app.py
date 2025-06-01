import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import time
import os
import pandas as pd
import base64

# === Must be the very first Streamlit command ===
st.set_page_config(page_title="🏋️ AI Fitness Tracker", layout="centered")

# Function to set background image from local path
def set_background_local(image_path):
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{b64_string}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Set your background image here (adjust path if needed)
set_background_local("assests/jay_cutler.jpg")

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
CSV_PATH = os.path.join(LOG_DIR, "reps_data.csv")

EXERCISES = [
    "Bicep Curl",
    "Chest Press",
    "Pec Flies",
    "Lat Pulldown",
    "Seated Rowing",
    "Landmine Rowing",
    "T-Bar Rowing",
    "Barbell Rowing",
    "Leg Curl",
    "Leg Extension",
    "Leg Press",
    "Weighted Squats",
    "Shoulder Press",
    "Lateral Raises",
    "Face Pull",
    "Reverse Fly (Shoulders)",
    "Upright Rowing",
    "Abs Exercises",
    "Custom Exercise"  # Add this option at end
]

if "running" not in st.session_state:
    st.session_state.running = False
if "counter" not in st.session_state:
    st.session_state.counter = 0
if "direction" not in st.session_state:
    st.session_state.direction = 0
if "rep_log" not in st.session_state:
    st.session_state.rep_log = []

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

def rep_count_logic(exercise, angle, direction):
    if exercise in ["Bicep Curl", "Shoulder Press", "Lateral Raises", "Face Pull", "Reverse Fly (Shoulders)", "Upright Rowing"]:
        if angle > 160:
            direction = 0
        if angle < 45 and direction == 0:
            direction = 1
            return 1, direction
    elif exercise in ["Chest Press", "Pec Flies", "Lat Pulldown", "Seated Rowing", "Landmine Rowing", "T-Bar Rowing", "Barbell Rowing"]:
        if angle > 150:
            direction = 0
        if angle < 60 and direction == 0:
            direction = 1
            return 1, direction
    elif exercise in ["Leg Curl", "Leg Extension", "Leg Press", "Weighted Squats"]:
        if angle > 160:
            direction = 0
        if angle < 70 and direction == 0:
            direction = 1
            return 1, direction
    elif exercise == "Abs Exercises":
        if angle > 140:
            direction = 0
        if angle < 50 and direction == 0:
            direction = 1
            return 1, direction
    else:
        if angle > 160:
            direction = 0
        if angle < 45 and direction == 0:
            direction = 1
            return 1, direction
    return 0, direction

st.markdown("<h1 style='text-align: center; color: #FF5733;'>🏋️ AI Fitness Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:16px;'>Count your exercise reps using webcam or video upload.</p>", unsafe_allow_html=True)

exercise_selected = st.selectbox("Select Exercise", EXERCISES)

if exercise_selected == "Custom Exercise":
    custom_exercise = st.text_input("Enter custom exercise name", max_chars=50)
    exercise = custom_exercise.strip() if custom_exercise.strip() != "" else None
else:
    exercise = exercise_selected

input_type = st.radio("Choose Input", ["Webcam", "Upload Video"])

video_file = None
if input_type == "Upload Video":
    video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

col1, col2 = st.columns(2)
with col1:
    start_clicked = st.button("▶️ Start")
with col2:
    stop_clicked = st.button("⏹ Stop")

if start_clicked:
    if exercise is None or exercise == "":
        st.warning("Please enter a valid custom exercise name.")
    else:
        st.session_state.running = True
        st.session_state.counter = 0
        st.session_state.direction = 0
        st.session_state.rep_log = []
        st.success(f"Started {exercise} detection!")

if stop_clicked:
    st.session_state.running = False
    st.success("Workout stopped!")

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

frame_placeholder = st.empty()
rep_placeholder = st.empty()

if st.session_state.running and exercise is not None:
    pose = mp_pose.Pose()

    if input_type == "Webcam":
        cap = cv2.VideoCapture(0)
    else:
        if video_file is None:
            st.warning("Please upload a video file to start.")
            st.stop()
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        cap = cv2.VideoCapture(tfile.name)

    while cap.isOpened() and st.session_state.running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            shoulder = [landmarks[12].x, landmarks[12].y]
            elbow = [landmarks[14].x, landmarks[14].y]
            wrist = [landmarks[16].x, landmarks[16].y]

            angle = calculate_angle(shoulder, elbow, wrist)

            reps_inc, new_direction = rep_count_logic(exercise, angle, st.session_state.direction)
            if reps_inc:
                st.session_state.counter += reps_inc
                st.session_state.rep_log.append({
                    "timestamp": time.time(),
                    "exercise": exercise,
                    "reps": st.session_state.counter
                })
            st.session_state.direction = new_direction

            cv2.putText(frame, f'Exercise: {exercise}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 105, 180), 2)
            cv2.putText(frame, f'Reps: {st.session_state.counter}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (50, 205, 50), 3)
            cv2.putText(frame, f'Angle: {int(angle)}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        frame_placeholder.image(frame, channels="BGR")
        rep_placeholder.metric(label="💪 Repetitions", value=st.session_state.counter)

        if input_type == "Upload Video":
            time.sleep(0.03)

    cap.release()
    pose.close()

if not st.session_state.running and st.session_state.counter > 0:
    df = pd.DataFrame(st.session_state.rep_log)
    df.to_csv(CSV_PATH, index=False)
    st.success(f"Workout complete! Total reps: {st.session_state.counter}")

    with open(CSV_PATH, "rb") as f:
        st.download_button(
            label="Download Reps CSV",
            data=f,
            file_name="reps_data.csv",
            mime="text/csv"
        )
