import mediapipe as mp
import cv2

class PoseDetector:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.pose.process(rgb)

    def get_landmarks(self, results):
        if results.pose_landmarks:
            return results.pose_landmarks.landmark
        return []
