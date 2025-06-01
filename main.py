from tracker import ExerciseTracker

def main():
    selected_exercise = input("Enter exercise name (e.g., pushup, squat, bicep_curl): ").strip()
    tracker = ExerciseTracker()
    tracker.run(selected_exercise)

if __name__ == "__main__":
    main()
