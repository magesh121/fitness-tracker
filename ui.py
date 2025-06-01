# Updated: ui.py

import streamlit as st
import threading
import time
from tracker import ExerciseTracker
from config import EXERCISES

# Thread wrapper to run tracker without blocking UI
class TrackerThread(threading.Thread):
    def __init__(self, exercise_name):
        super().__init__()
        self.exercise_name = exercise_name
        self.tracker = ExerciseTracker()
        self.count = {exercise_name: 0}
        self.running = True

    def run(self):
        self.count = self.tracker.run(self.exercise_name)
        self.running = False

# Streamlit App
def main():
    st.set_page_config(page_title="AI Fitness Tracker", layout="centered")
    st.title("🏋️ AI Fitness Tracker")

    exercises = list(EXERCISES.keys())
    selected_exercise = st.selectbox("Select Exercise:", exercises)

    start = st.button("▶ Start Workout")
    stop_placeholder = st.empty()
    rep_display = st.empty()

    if start:
        tracker_thread = TrackerThread(selected_exercise)
        tracker_thread.start()

        stop = stop_placeholder.button("⏹ Stop Workout")

        while tracker_thread.running and not stop:
            rep_display.markdown(
                f"### {selected_exercise.capitalize()} Reps: `{tracker_thread.count[selected_exercise]}`"
            )
            time.sleep(1)
            stop = stop_placeholder.button("⏹ Stop Workout")

        if not tracker_thread.running:
            rep_display.markdown(
                f"### Final Count: **{tracker_thread.count[selected_exercise]}**"
            )

if __name__ == "__main__":
    main()
