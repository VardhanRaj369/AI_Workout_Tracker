import streamlit as st
import numpy as np
import time
import plotly.graph_objects as go
from PIL import Image
import tempfile
import os

# Try to import computer vision dependencies with fallbacks
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError as e:
    st.error(f"OpenCV not available: {e}")
    CV2_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError as e:
    st.error(f"MediaPipe not available: {e}")
    MEDIAPIPE_AVAILABLE = False

try:
    from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
    import av
    WEBRTC_AVAILABLE = True
except ImportError as e:
    st.error(f"WebRTC not available: {e}")
    WEBRTC_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="AI Workout Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean CSS
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
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

class PoseDetector:
    def __init__(self):
        if not MEDIAPIPE_AVAILABLE:
            raise ImportError("MediaPipe is not available")
        
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            model_complexity=1
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle

    def detect_exercise(self, landmarks, exercise_type):
        """Detect specific exercise based on pose landmarks"""
        angles = {}
        
        try:
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
                
                wrist_distance = np.sqrt((left_wrist[0]-right_wrist[0])**2 + (left_wrist[1]-right_wrist[1])**2)
                angles['wrist_distance'] = wrist_distance
                
            elif exercise_type == "Shoulder Press":
                shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                           landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                
                vertical_movement = shoulder[1] - wrist[1]
                angles['vertical'] = vertical_movement
                
        except Exception as e:
            st.error(f"Error in pose detection: {e}")
            
        return angles

class VideoProcessor:
    def __init__(self):
        self.detector = PoseDetector() if MEDIAPIPE_AVAILABLE else None
        self.exercise_type = "Push-ups"
        self.rep_count = 0
        self.stage = None
        self.start_time = time.time()
        self.workout_data = []
        
    def process_frame(self, image):
        """Process a single image frame"""
        if not CV2_AVAILABLE or not MEDIAPIPE_AVAILABLE:
            return image, self.rep_count, self.stage
            
        try:
            # Convert PIL Image to numpy array for OpenCV
            if isinstance(image, Image.Image):
                image_np = np.array(image)
                # Convert RGB to BGR for OpenCV
                if len(image_np.shape) == 3:
                    image_np = image_np[:, :, ::-1]
            else:
                image_np = image
            
            # Process image with MediaPipe
            image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            results = self.detector.pose.process(image_rgb)
            
            current_time = time.time() - self.start_time
            
            if results.pose_landmarks:
                # Draw pose landmarks
                self.detector.mp_drawing.draw_landmarks(
                    image_np,
                    results.pose_landmarks,
                    self.detector.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.detector.mp_drawing_styles.get_default_pose_landmarks_style())
                
                # Exercise detection
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
                    self._count_reps(angles)
                    
                    # Add text overlay
                    cv2.putText(image_np, f'Exercise: {self.exercise_type}', (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(image_np, f'REPS: {self.rep_count}', (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(image_np, f'STAGE: {self.stage}', (10, 110), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Convert back to RGB for display
            if len(image_np.shape) == 3:
                image_np = image_np[:, :, ::-1]
                
            return Image.fromarray(image_np), self.rep_count, self.stage
            
        except Exception as e:
            st.error(f"Error processing frame: {e}")
            return image, self.rep_count, self.stage
    
    def _count_reps(self, angles):
        """Count repetitions based on exercise type and angles"""
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

def initialize_workout_state():
    """Initialize workout state in session state"""
    if 'workout_active' not in st.session_state:
        st.session_state.workout_active = False
    if 'show_report' not in st.session_state:
        st.session_state.show_report = False
    if 'current_exercise' not in st.session_state:
        st.session_state.current_exercise = "Push-ups"
    if 'video_processor' not in st.session_state:
        st.session_state.video_processor = VideoProcessor()

def reset_workout():
    """Reset workout state"""
    st.session_state.workout_active = False
    st.session_state.show_report = False
    st.session_state.video_processor = VideoProcessor()

def generate_workout_report(rep_count, exercise_type, duration):
    """Generate a comprehensive workout report"""
    if rep_count == 0:
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
    
    # Check dependencies
    if not CV2_AVAILABLE or not MEDIAPIPE_AVAILABLE:
        st.markdown("""
        <div class="warning-box">
            <h3>⚠️ Limited Functionality Mode</h3>
            <p>Some computer vision dependencies are not available in this environment.</p>
            <p><strong>For full functionality:</strong></p>
            <ul>
                <li>Deploy on a platform that supports OpenCV system dependencies</li>
                <li>Use a local development environment</li>
                <li>Try Google Colab for testing</li>
            </ul>
            <p><em>You can still use the manual tracking mode below.</em></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="success-box">
            <h3>✅ Full Computer Vision Mode Active</h3>
            <p>Real-time pose detection and exercise tracking is enabled!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize workout state
    initialize_workout_state()
    
    # Sidebar
    with st.sidebar:
        st.header("🏋️ Workout Settings")
        
        exercise_type = st.selectbox(
            "Choose Exercise",
            ["Push-ups", "Squats", "Bicep Curls", "Jumping Jacks", "Shoulder Press"]
        )
        
        st.session_state.current_exercise = exercise_type
        st.session_state.video_processor.exercise_type = exercise_type
        
        st.header("📊 Exercise Instructions")
        if exercise_type == "Push-ups":
            st.write("**Detection:** Tracks elbow angle (90° for rep count)")
        elif exercise_type == "Squats":
            st.write("**Detection:** Tracks knee angle (parallel for rep count)")
        elif exercise_type == "Bicep Curls":
            st.write("**Detection:** Tracks elbow flexion (30°-160°)")
        elif exercise_type == "Jumping Jacks":
            st.write("**Detection:** Tracks arm distance expansion")
        elif exercise_type == "Shoulder Press":
            st.write("**Detection:** Tracks vertical arm movement")
        
        # Manual controls for demo
        st.header("🎮 Manual Controls")
        if st.button("➕ Add Rep", use_container_width=True):
            st.session_state.video_processor.rep_count += 1
            st.session_state.video_processor.stage = "manual"
            st.rerun()
        
        if st.button("🔄 Reset Counter", use_container_width=True):
            reset_workout()
            st.rerun()
    
    # Main content
    st.markdown('<div class="section-header">🎥 Camera Input</div>', unsafe_allow_html=True)
    
    if CV2_AVAILABLE and MEDIAPIPE_AVAILABLE:
        # Use camera input with real processing
        camera_image = st.camera_input("Take a picture for pose detection", key="workout_camera")
        
        if camera_image is not None:
            # Process the image
            processed_image, rep_count, stage = st.session_state.video_processor.process_frame(camera_image)
            
            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.image(processed_image, caption="Pose Detection Result", use_column_width=True)
            with col2:
                st.metric("Repetitions", rep_count)
                st.metric("Current Stage", stage or "Starting...")
                st.metric("Exercise", st.session_state.current_exercise)
    else:
        # Manual mode
        st.info("📷 Camera input requires OpenCV. Using manual tracking mode.")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Repetitions", st.session_state.video_processor.rep_count)
            st.metric("Current Stage", st.session_state.video_processor.stage or "Use sidebar to add reps")
        with col2:
            st.metric("Exercise", st.session_state.current_exercise)
            st.metric("Status", "Manual Mode")
    
    # Finish Workout Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏁 Finish Workout & Generate Report", use_container_width=True, type="primary"):
            rep_count = st.session_state.video_processor.rep_count
            workout_duration = time.time() - st.session_state.video_processor.start_time
            
            if rep_count > 0:
                report = generate_workout_report(
                    rep_count,
                    st.session_state.current_exercise,
                    workout_duration
                )
                
                if report:
                    st.session_state.workout_report = report
                    st.session_state.show_report = True
                    st.rerun()
            else:
                st.error("❌ Complete at least 1 rep to generate a workout report!")
    
    # Workout Report Section
    if st.session_state.get('show_report', False) and st.session_state.get('workout_report'):
        st.markdown("---")
        st.markdown('<div class="section-header">📋 Workout Summary Report</div>', unsafe_allow_html=True)
        
        report = st.session_state.workout_report
        
        # Appreciation Message
        st.markdown("### 🎉 Workout Complete!")
        if report['performance_score'] >= 80:
            st.success("**Outstanding Performance!** You crushed your workout! Your dedication and form are impressive. Keep up this amazing energy!")
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
            mode = "gauge+number",
            value = report['performance_score'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Performance"},
            gauge = {
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
        if st.button("🔄 Start New Workout", use_container_width=True):
            reset_workout()
            st.rerun()

if __name__ == "__main__":
    main()
