import streamlit as st
import time
import plotly.graph_objects as go
import random

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
    .demo-box {
        border: 2px dashed #ccc;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def initialize_workout_state():
    """Initialize workout state in session state"""
    if 'workout_state' not in st.session_state:
        st.session_state.workout_state = {
            'rep_count': 0,
            'stage': None,
            'start_time': time.time(),
            'exercise_type': "Push-ups",
            'last_update': time.time(),
            'workout_active': False,
            'demo_mode': True
        }
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
        'workout_active': False,
        'demo_mode': True
    }

def simulate_exercise_detection(exercise_type, workout_state):
    """Simulate exercise detection for demo purposes"""
    # Simulate random rep detection (for demo)
    if random.random() < 0.3:  # 30% chance of detecting a rep
        if workout_state['stage'] is None:
            workout_state['stage'] = "starting"
        elif workout_state['stage'] == "starting":
            workout_state['stage'] = "halfway"
        elif workout_state['stage'] == "halfway":
            workout_state['stage'] = "complete"
            workout_state['rep_count'] += 1
            workout_state['last_update'] = time.time()
        elif workout_state['stage'] == "complete":
            workout_state['stage'] = "starting"
    
    workout_state['workout_active'] = True
    return workout_state

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

def main():
    st.markdown('<h1 class="main-title">💪 AI Workout Tracker</h1>', unsafe_allow_html=True)
    st.markdown("Track your exercises and get personalized fitness insights!")
    
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
        
        # Current workout stats in sidebar
        st.header("📈 Current Stats")
        workout_state = st.session_state.workout_state
        st.metric("Repetitions", workout_state['rep_count'])
        st.metric("Current Stage", workout_state['stage'] or "Starting...")
        st.metric("Workout Duration", f"{time.time() - workout_state['start_time']:.1f}s")
        
        # Manual rep counter for demo
        st.header("🎮 Demo Controls")
        if st.button("➕ Add Rep", use_container_width=True):
            workout_state['rep_count'] += 1
            workout_state['last_update'] = time.time()
            workout_state['workout_active'] = True
        
        if st.button("🔄 Reset Counter", use_container_width=True):
            reset_workout()
    
    # Main content
    st.markdown('<div class="section-header">🎥 Workout Interface</div>', unsafe_allow_html=True)
    
    # Demo mode explanation
    st.markdown("""
    <div class="demo-box">
        <h3>🏗️ Demo Mode</h3>
        <p>This is a demonstration version of the AI Workout Tracker.</p>
        <p>In a full implementation, this would use computer vision to track your exercises in real-time.</p>
        <p>For now, use the controls in the sidebar to simulate your workout!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Exercise visualization
    workout_state = st.session_state.workout_state
    exercise = workout_state['exercise_type']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"Current Exercise: {exercise}")
        
        # Simple ASCII art for different exercises
        exercise_art = {
            "Push-ups": """
            🤸 Push-up Position:
                __________
               |          |
               |   YOU    |
               |__________|
                /        \\
            """,
            "Squats": """
            🏋️ Squat Position:
                ╔════════╗
                ║   🧍   ║
                ╚════════╝
                  /    \\
            """,
            "Bicep Curls": """
            💪 Bicep Curl:
                🧍‍♂️↑
                | |
                💪💪
            """,
            "Jumping Jacks": """
            🤸 Jumping Jack:
                🧍‍♂️✖️
                / \\
            """,
            "Shoulder Press": """
            🏋️ Shoulder Press:
                🧍‍♂️↑
                💪💪
                | |
            """
        }
        
        st.text(exercise_art.get(exercise, "Select an exercise to see form"))
    
    with col2:
        st.subheader("Real-time Feedback")
        if workout_state['workout_active']:
            if workout_state['rep_count'] > 0:
                st.success(f"✅ Great form! Keep going!")
                st.info(f"**Reps completed:** {workout_state['rep_count']}")
                st.info(f"**Current stage:** {workout_state['stage']}")
            else:
                st.warning("🔄 Get ready to start your first rep!")
        else:
            st.info("🏁 Click 'Add Rep' in sidebar to start tracking!")
        
        # Progress bar
        if workout_state['rep_count'] > 0:
            progress = min(workout_state['rep_count'] / 20, 1.0)  # Cap at 20 reps for progress
            st.progress(progress)
            st.caption(f"Progress: {workout_state['rep_count']}/20 reps")
    
    # Auto-simulate button
    if st.button("🎬 Auto-Simulate Workout (Add 5 reps)", use_container_width=True):
        workout_state = st.session_state.workout_state
        workout_state['rep_count'] += 5
        workout_state['workout_active'] = True
        workout_state['last_update'] = time.time()
        st.success("Added 5 reps to your workout!")
        st.rerun()
    
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
