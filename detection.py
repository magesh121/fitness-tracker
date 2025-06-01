import cv2
import mediapipe as mp
import math
from config import EXERCISES

class PoseDetection:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.drawing = mp.solutions.drawing_utils

        self.count = {exercise: 0 for exercise in EXERCISES}
        self.stage = {exercise: None for exercise in EXERCISES}

    def calculate_angle(self, a, b, c):
        """Returns angle between 3 points in degrees"""
        a = [a.x, a.y]
        b = [b.x, b.y]
        c = [c.x, c.y]

        radians = math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0])
        angle = abs(radians * 180.0 / math.pi)
        if angle > 180.0:
            angle = 360 - angle
        return angle

    def get_angle_by_exercise(self, landmarks, exercise):
        if exercise in ["pushup", "bicep_curl", "tricep_extension", "flat_press", "incline_press", "decline_press"]:
            # Use right arm by default
            shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
            wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            return self.calculate_angle(shoulder, elbow, wrist)
        
        elif exercise in ["squat", "leg_curl", "leg_extension", "leg_press"]:
            hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
            knee = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE]
            ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
            return self.calculate_angle(hip, knee, ankle)
        
        elif exercise in ["pullup", "lat_pulldown"]:
            # Optional: shoulder angle (less precise)
            shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
            wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            return self.calculate_angle(shoulder, elbow, wrist)

        return None

    def process(self, frame, selected_exercise):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            self.drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            angle = self.get_angle_by_exercise(landmarks, selected_exercise)
            if angle is not None:
                # Display angle on frame
                cv2.putText(frame, f'Angle: {int(angle)}', (30, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                # Count logic (adjust based on exercise needs)
                if angle < 70:
                    self.stage[selected_exercise] = "down"
                elif angle > 160 and self.stage[selected_exercise] == "down":
                    self.stage[selected_exercise] = "up"
                    self.count[selected_exercise] += 1
                    print(f"[{selected_exercise}] Count: {self.count[selected_exercise]}")

        return frame, self.count
