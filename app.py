import streamlit as st
import numpy as np
import mediapipe as mp
import time
import plotly.graph_objects as go
from PIL import Image

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
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle

    def detect_exercise(self, landmarks, exercise_type):
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
                elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                
                vertical_movement = shoulder[1] - wrist[1]
                angles['vertical'] = vertical_movement
                
        except Exception as e:
            st.error(f"Error in pose detection: {e}")
            
        return angles

def initialize_workout_state():
    """Initialize workout state in session state"""
    if 'workout_state' not in st.session_state:
        st.session_state.workout_state = {
            'rep_count': 0,
            'stage': None,
            'start_time': time.time(),
            'exercise_type': "Push-ups",
            'last_update': time.time(),
            'workout_active': False
        }
    if 'detector' not in st.session_state:
        st.session_state.detector = PoseDetector()
    if 'show_report' not in st.session_state:
        st.session_state.show_report = False

def reset_workout():
    """Reset workout state for new exercise"""
    st.session_state.workout_state = {
        'rep_count': 0,
        'stage': None,
        'start_time': time.time(),
        'exercise_type': st.session_state.workout_state['exercise_type'],
        'last_update': time.time(),
        'workout_active': False
    }

def generate_workout_report():
    """Generate a comprehensive workout report"""
    workout_state = st.session_state.workout_state
    
    if workout_state['rep_count'] == 0:
        return None
    
    duration = time.time() - workout_state['start_time']
    
    # Create report
    report = {
        'exercise_type': workout_state['exercise_type'],
        'total_reps': workout_state['rep_count'],
        'workout_duration': duration,
        'average_reps_per_minute': (workout_state['rep_count'] / duration * 60) if duration > 0 else 0,
        'calories_burned': workout_state['rep_count'] * 0.5,
        'performance_score': min(100, (workout_state['rep_count'] / 20) * 100)
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

def process_image(image, exercise_type, workout_state):
    """Process image and detect exercises"""
    detector = st.session_state.detector
    
    # Convert PIL Image to numpy array
    image_np = np.array(image)
    
    # Convert RGB to BGR for mediapipe
    image_rgb = image_np[:, :, ::-1] if len(image_np.shape) == 3 else image_np
    
    results = detector.pose.process(image_rgb)
    
    if results.pose_landmarks:
        # Draw pose landmarks
        detector.mp_drawing.draw_landmarks(
            image_np,
            results.pose_landmarks,
            detector.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=detector.mp_drawing_styles.get_default_pose_landmarks_style())
        
        # Exercise detection
        angles = detector.detect_exercise(results.pose_landmarks.landmark, exercise_type)
        
        if angles:
            workout_state['workout_active'] = True
            workout_state['last_update'] = time.time()
            
            # Exercise-specific rep counting
            if exercise_type == "Push-ups":
                main_angle = angles.get('elbow', 0)
                if main_angle > 160 and workout_state['stage'] != "up":
                    workout_state['stage'] = "up"
                if main_angle < 90 and workout_state['stage'] == "up":
                    workout_state['stage'] = "down"
                    workout_state['rep_count'] += 1
                    
            elif exercise_type == "Squats":
                main_angle = angles.get('knee', 0)
                if main_angle > 160 and workout_state['stage'] != "up":
                    workout_state['stage'] = "up"
                if main_angle < 100 and workout_state['stage'] == "up":
                    workout_state['stage'] = "down"
                    workout_state['rep_count'] += 1
                    
            elif exercise_type == "Bicep Curls":
                main_angle = angles.get('elbow', 0)
                if main_angle > 160 and workout_state['stage'] != "down":
                    workout_state['stage'] = "down"
                if main_angle < 30 and workout_state['stage'] == "down":
                    workout_state['stage'] = "up"
                    workout_state['rep_count'] += 1
            
            elif exercise_type == "Jumping Jacks":
                wrist_distance = angles.get('wrist_distance', 0)
                
                if wrist_distance > 0.3 and workout_state['stage'] != "arms_up":
                    workout_state['stage'] = "arms_up"
                if wrist_distance < 0.15 and workout_state['stage'] == "arms_up":
                    workout_state['stage'] = "arms_down"
                    workout_state['rep_count'] += 1
            
            elif exercise_type == "Shoulder Press":
                vertical_movement = angles.get('vertical', 0)
                
                if vertical_movement > 0.15 and workout_state['stage'] != "down":
                    workout_state['stage'] = "down"
                if vertical_movement < -0.1 and workout_state['stage'] == "down":
                    workout_state['stage'] = "up"
                    workout_state['rep_count'] += 1
    
    return image_np, workout_state

def main():
    st.markdown('<h1 class="main-title">💪 AI Workout Tracker</h1>', unsafe_allow_html=True)
    st.markdown("Track your exercises using your camera and AI pose detection!")
    
    # Initialize workout state
    initialize_workout_state()
    
    # Sidebar
    with st.sidebar:
        st.header("🏋️ Workout Settings")
        
        exercise_type = st.selectbox(
            "Choose Exercise",
            ["Push-ups", "Squats", "Bicep Curls", "Jumping Jacks", "Shoulder Press"]
        )
        
        # Update exercise type in workout state
        if exercise_type != st.session_state.workout_state['exercise_type']:
            st.session_state.workout_state['exercise_type'] = exercise_type
            reset_workout()
        
        st.header("📊 Exercise Instructions")
        if exercise_type == "Push-ups":
            st.write("**Instructions:** Keep body straight, lower to 90°, push up completely")
        elif exercise_type == "Squats":
            st.write("**Instructions:** Feet shoulder-width, lower until parallel, knees behind toes")
        elif exercise_type == "Bicep Curls":
            st.write("**Instructions:** Elbows close to body, full range of motion, no swinging")
        elif exercise_type == "Jumping Jacks":
            st.write("**Instructions:** Coordinate arms and legs, land softly, maintain rhythm")
        elif exercise_type == "Shoulder Press":
            st.write("**Instructions:** Keep core tight, press fully overhead, controlled movement")
        
        # Current workout stats in sidebar
        st.header("📈 Current Stats")
        workout_state = st.session_state.workout_state
        st.metric("Repetitions", workout_state['rep_count'])
        st.metric("Current Stage", workout_state['stage'] or "Starting...")
        st.metric("Workout Duration", f"{time.time() - workout_state['start_time']:.1f}s")
    
    # Main content
    st.markdown('<div class="section-header">🎥 Camera Input</div>', unsafe_allow_html=True)
    
    # Use Streamlit's camera input
    camera_image = st.camera_input("Take a picture for workout tracking", key="workout_camera")
    
    if camera_image is not None:
        workout_state = st.session_state.workout_state
        exercise_type = workout_state['exercise_type']
        
        # Process the image
        processed_image, updated_state = process_image(camera_image, exercise_type, workout_state)
        
        # Display the processed image with pose landmarks
        st.image(processed_image, caption="Pose Detection Result", use_column_width=True)
        
        # Display current status
        if updated_state['workout_active']:
            st.success(f"✅ Active - {updated_state['rep_count']} reps completed!")
            st.info(f"Current stage: {updated_state['stage']}")
        else:
            st.warning("⏸️ Get in position and start exercising!")
    
    # Finish Workout Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏁 Finish Workout & Generate Report", use_container_width=True, type="primary"):
            workout_state = st.session_state.workout_state
            if workout_state['rep_count'] > 0:
                report = generate_workout_report()
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
            st.session_state.show_report = False
            st.rerun()

if __name__ == "__main__":
    main()
