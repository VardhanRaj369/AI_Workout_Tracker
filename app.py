import os
# Disable OpenCV GUI backends (fixes libGL on headless)
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "0"
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"
os.environ["QT_QPA_PLATFORM"] = "offscreen"  # Extra for any Qt deps in MediaPipe


import cv2
import numpy as np
import mediapipe as mp
import time
import plotly.graph_objects as go
import av
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration

# Page configuration
st.set_page_config(
    page_title="AI Workout Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean CSS that works in both light and dark themes
st.markdown("""
<style>
    .main-title {
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .workout-button {
        width: 100%;
        margin: 1rem 0;
    }
    .metric-value {
        font-size: 1.2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def detect_exercise(self, landmarks, exercise_type):
        angles = {}

        if exercise_type == "Push-ups":
            shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            angles['elbow'] = self.calculate_angle(shoulder, elbow, wrist)

        elif exercise_type == "Squats":
            hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            angles['knee'] = self.calculate_angle(hip, knee, ankle)

        elif exercise_type == "Bicep Curls":
            shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            angles['elbow'] = self.calculate_angle(shoulder, elbow, wrist)

        elif exercise_type == "Jumping Jacks":
            left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                           landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            wrist_distance = np.sqrt((left_wrist[0] - right_wrist[0]) ** 2 + (left_wrist[1] - right_wrist[1]) ** 2)
            angles['wrist_distance'] = wrist_distance

        elif exercise_type == "Shoulder Press":
            shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            vertical_movement = shoulder[1] - wrist[1]
            angles['vertical'] = vertical_movement

        return angles


class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.detector = PoseDetector()
        self.exercise_type = "Push-ups"
        self.rep_count = 0
        self.stage = None
        self.start_time = time.time()
        self.workout_data = []

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Process image
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.detector.pose.process(img_rgb)

        current_time = time.time() - self.start_time

        if results.pose_landmarks:
            # Draw pose landmarks
            self.detector.mp_drawing.draw_landmarks(
                img,
                results.pose_landmarks,
                self.detector.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.detector.mp_drawing_styles.get_default_pose_landmarks_style())

            # Exercise detection logic
            angles = self.detector.detect_exercise(results.pose_landmarks.landmark, self.exercise_type)

            if angles:
                # Store workout data
                self.workout_data.append({
                    'time': current_time,
                    'rep_count': self.rep_count,
                    'stage': self.stage,
                    'angles': angles
                })

                # Exercise-specific rep counting
                if self.exercise_type == "Push-ups":
                    main_angle = angles.get('elbow', 0)
                    if main_angle > 160 and self.stage != "up":
                        self.stage = "up"
                    if main_angle < 90 and self.stage == "up":
                        self.stage = "down"
                        self.rep_count += 1

                elif self.exercise_type == "Squats":
                    main_angle = angles.get('knee', 0)
                    if main_angle > 160 and self.stage != "up":
                        self.stage = "up"
                    if main_angle < 100 and self.stage == "up":
                        self.stage = "down"
                        self.rep_count += 1

                elif self.exercise_type == "Bicep Curls":
                    main_angle = angles.get('elbow', 0)
                    if main_angle > 160 and self.stage != "down":
                        self.stage = "down"
                    if main_angle < 30 and self.stage == "down":
                        self.stage = "up"
                        self.rep_count += 1

                elif self.exercise_type == "Jumping Jacks":
                    wrist_distance = angles.get('wrist_distance', 0)

                    if wrist_distance > 0.3 and self.stage != "arms_up":
                        self.stage = "arms_up"
                    if wrist_distance < 0.15 and self.stage == "arms_up":
                        self.stage = "arms_down"
                        self.rep_count += 1

                elif self.exercise_type == "Shoulder Press":
                    vertical_movement = angles.get('vertical', 0)

                    if vertical_movement > 0.15 and self.stage != "down":
                        self.stage = "down"
                    if vertical_movement < -0.1 and self.stage == "down":
                        self.stage = "up"
                        self.rep_count += 1

                # Display information
                cv2.putText(img, f'Exercise: {self.exercise_type}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, f'REPS: {self.rep_count}', (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, f'STAGE: {self.stage}', (10, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Show angle/distance info
                if self.exercise_type == "Jumping Jacks":
                    cv2.putText(img, f'DISTANCE: {wrist_distance:.2f}', (10, 150),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif self.exercise_type == "Shoulder Press":
                    cv2.putText(img, f'MOVEMENT: {vertical_movement:.2f}', (10, 150),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    main_angle = list(angles.values())[0]
                    cv2.putText(img, f'ANGLE: {main_angle:.1f}', (10, 150),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


def generate_workout_report(workout_data, exercise_type, rep_count, duration):
    """Generate a comprehensive workout report"""
    if not workout_data:
        return None

    # Create report
    report = {
        'exercise_type': exercise_type,
        'total_reps': rep_count,
        'workout_duration': duration,
        'average_reps_per_minute': (rep_count / duration * 60) if duration > 0 else 0,
        'calories_burned': rep_count * 0.5,
        'performance_score': min(100, (rep_count / 20) * 100)
    }

    return report


def get_health_tips(performance_score, reps_count):
    """Generate health and fitness tips based on performance"""
    tips = []

    # Basic health tips (always show)
    tips.append("💧 Stay Hydrated: Drink at least 8 glasses of water daily")
    tips.append("🛌 Maintain Sleep Cycles: Aim for 7-9 hours of quality sleep")
    tips.append("🥗 Focus on Balanced Diet: Include proteins, carbs, and healthy fats")

    # Performance-based tips
    if performance_score >= 80:
        tips.append("🎯 Excellent Progress: Consider increasing intensity gradually")
        tips.append("🔥 Maintain Consistency: Keep up the great work!")
    elif performance_score >= 60:
        tips.append("📈 Good Effort: Try to increase reps by 10% next session")
        tips.append("💪 Focus on Form: Quality over quantity always wins")
    else:
        tips.append("🌱 Building Foundation: Start with lighter sessions and build up")
        tips.append("🎯 Set Small Goals: Celebrate every improvement")

    return tips


def main():
    st.markdown('<h1 class="main-title">💪 AI Workout Tracker</h1>', unsafe_allow_html=True)
    st.markdown("Track your exercises in real-time using computer vision!")

    # Initialize session state
    if 'show_report' not in st.session_state:
        st.session_state.show_report = False
    if 'current_exercise' not in st.session_state:
        st.session_state.current_exercise = "Push-ups"

    # Sidebar
    with st.sidebar:
        st.header("🏋️ Workout Settings")

        exercise_type = st.selectbox(
            "Choose Exercise",
            ["Push-ups", "Squats", "Bicep Curls", "Jumping Jacks", "Shoulder Press"]
        )

        st.session_state.current_exercise = exercise_type

        st.header("📊 Exercise Instructions")
        if exercise_type == "Push-ups":
            st.write("""
            **Instructions:**
            - Keep your body straight
            - Lower until elbows are at 90°
            - Push back up to starting position
            """)
        elif exercise_type == "Squats":
            st.write("""
            **Instructions:**
            - Feet shoulder-width apart
            - Lower until thighs are parallel to floor
            - Keep knees behind toes
            """)
        elif exercise_type == "Bicep Curls":
            st.write("""
            **Instructions:**
            - Keep elbows close to body
            - Curl weight up to shoulders
            - Lower slowly with control
            """)
        elif exercise_type == "Jumping Jacks":
            st.write("""
            **Instructions:**
            - Start with feet together, arms at sides
            - Jump while spreading legs and raising arms
            - Return to starting position
            """)
        elif exercise_type == "Shoulder Press":
            st.write("""
            **Instructions:**
            - Start with hands at shoulder level
            - Press upward until arms are fully extended
            - Lower back to starting position
            """)

    # Main content
    st.markdown('<div class="section-header">🎥 Live Camera Feed</div>', unsafe_allow_html=True)

    # Initialize video processor
    webrtc_ctx = webrtc_streamer(
        key="workout-tracker",
        video_processor_factory=VideoProcessor,
        rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
        media_stream_constraints={"video": True, "audio": False},
    )

    # Update exercise type in video processor
    if webrtc_ctx.video_processor:
        webrtc_ctx.video_processor.exercise_type = st.session_state.current_exercise

    # Finish Workout Button - Centered
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏁 Finish Workout & Generate Report", use_container_width=True, type="primary",
                     key="finish_workout"):
            if webrtc_ctx.video_processor:
                rep_count = webrtc_ctx.video_processor.rep_count
                workout_duration = time.time() - webrtc_ctx.video_processor.start_time

                if rep_count > 0:
                    report = generate_workout_report(
                        webrtc_ctx.video_processor.workout_data,
                        st.session_state.current_exercise,
                        rep_count,
                        workout_duration
                    )

                    if report:
                        st.session_state.workout_report = report
                        st.session_state.show_report = True
                        st.rerun()
                else:
                    st.error("❌ Complete at least 1 rep to generate a workout report!")
            else:
                st.warning("Please start the camera first!")

    # Workout Report Section
    if st.session_state.get('show_report', False) and st.session_state.get('workout_report'):
        st.markdown("---")
        st.markdown('<div class="section-header">📋 Workout Summary Report</div>', unsafe_allow_html=True)

        report = st.session_state.workout_report

        # Appreciation Message
        st.markdown("### 🎉 Workout Complete!")
        if report['performance_score'] >= 80:
            st.success(
                "**Outstanding Performance!** You crushed your workout! Your dedication and form are impressive. Keep up this amazing energy!")
        elif report['performance_score'] >= 60:
            st.info("**Great Job!** Solid workout session! You're making excellent progress toward your fitness goals.")
        else:
            st.warning("**Good Start!** Every workout counts! You're building a strong foundation for future success.")

        # Workout Statistics
        st.markdown("### 📊 Workout Statistics")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Exercise", report['exercise_type'])
        with col2:
            st.metric("Total Reps", report['total_reps'])
        with col3:
            st.metric("Duration", f"{report['workout_duration']:.1f}s")
        with col4:
            st.metric("Performance", f"{report['performance_score']:.1f}%")

        col5, col6 = st.columns(2)
        with col5:
            st.metric("Calories Burned", f"{report['calories_burned']:.1f}")
        with col6:
            st.metric("Reps/Minute", f"{report['average_reps_per_minute']:.1f}")

        # Health and Fitness Tips
        st.markdown("### 💡 Health & Fitness Tips")
        tips = get_health_tips(report['performance_score'], report['total_reps'])

        for tip in tips:
            st.write(f"- {tip}")

        # Performance Gauge
        st.markdown("### 📈 Performance Overview")

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=report['performance_score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Performance"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 60], 'color': "lightcoral"},
                    {'range': [60, 80], 'color': "lightyellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ]
            }
        ))

        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Option to start new workout
        st.markdown("---")
        if st.button("🔄 Start New Workout", use_container_width=True, key="new_workout"):
            if webrtc_ctx.video_processor:
                webrtc_ctx.video_processor.rep_count = 0
                webrtc_ctx.video_processor.stage = None
                webrtc_ctx.video_processor.start_time = time.time()
                webrtc_ctx.video_processor.workout_data = []
            st.session_state.show_report = False
            st.rerun()


if __name__ == "__main__":

    main()
