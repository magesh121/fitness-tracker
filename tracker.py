# Updated: tracker.py

import cv2
from detection import PoseDetection

class ExerciseTracker:
    def __init__(self):
        self.pose_detector = PoseDetection()

    def run(self, selected_exercise):
        cap = cv2.VideoCapture(0)  # Use webcam
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame, count = self.pose_detector.process(frame, selected_exercise)
            
            # Draw rep count on frame
            cv2.rectangle(frame, (0, 0), (300, 80), (0, 0, 0), -1)
            cv2.putText(frame, f"{selected_exercise.capitalize()} Reps: {count[selected_exercise]}", 
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('AI Fitness Tracker', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return count