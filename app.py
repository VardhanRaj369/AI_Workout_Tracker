import streamlit as st
import cv2
import time
import base64

from pose_module import PoseDetector
from exercise_module import ExerciseCounter

# ---------------- AUDIO ----------------

def load_sound(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def play_audio(sound):
    st.markdown(
        f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{sound}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True
    )

sounds = {
    "start": load_sound("sounds/start_exercise.mp3"),
    "finish": load_sound("sounds/finish_workout.mp3"),
    "perfect": load_sound("sounds/good_form.mp3"),
    "keepgoing": load_sound("sounds/keep_going.mp3")
}

# ---------------- STATE ----------------

if "running" not in st.session_state:
    st.session_state.running = False

if "counter" not in st.session_state:
    st.session_state.counter = None

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "last_perfect" not in st.session_state:
    st.session_state.last_perfect = 0

if "last_keepgoing" not in st.session_state:
    st.session_state.last_keepgoing = 0

# ---------------- UI ----------------

# ---------------- HEADER ----------------

st.title("💪 AI Workout Tracker")

# Short description for users
st.markdown("""
Welcome to the **AI Workout Tracker**!  
Track your exercise reps in real time using your webcam — no equipment or body sensors are required.  
Just choose an exercise, start your session, and let the AI count your reps while you focus on form and consistency!
""")

# Cloud loading notice
st.info("⏳ *Note: The app may take a few seconds to start as it runs on cloud resources.*")

# Exercise selector
exercise_list = ["Squats", "Push-ups", "Bicep Curls", "Shoulder Press", "Tricep Dips"]
exercise = st.selectbox("Choose Exercise", exercise_list)


col1, col2 = st.columns(2)

if col1.button("Start Workout"):
    st.session_state.running = True
    st.session_state.counter = ExerciseCounter(exercise)
    st.session_state.start_time = time.time()
    play_audio(sounds["start"])

if col2.button("Finish Workout"):
    st.session_state.running = False

frame_placeholder = st.empty()
detector = PoseDetector()

# ---------------- WORKOUT LOOP ----------------

if st.session_state.running:
    cap = cv2.VideoCapture(0)

    while st.session_state.running:

        ret, frame = cap.read()
        if not ret:
            st.error("Webcam error.")
            break

        frame = cv2.flip(frame, 1)

        results = detector.detect(frame)
        landmarks = detector.get_landmarks(results)

        count, feedback, rep_flag = st.session_state.counter.update(landmarks)

        now = time.time()

        # PERFECT every 10 reps
        if count % 10 == 0 and count > 0:
            if now - st.session_state.last_perfect > 2:
                play_audio(sounds["perfect"])
                st.session_state.last_perfect = now

        # KEEP GOING every 20 reps
        if count % 20 == 0 and count > 0:
            if now - st.session_state.last_keepgoing > 2:
                play_audio(sounds["keepgoing"])
                st.session_state.last_keepgoing = now

        cv2.putText(frame, exercise, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        cv2.putText(frame, f"Reps: {count}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 2)
        cv2.putText(frame, feedback, (10, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

        frame_placeholder.image(frame, channels="BGR")

        time.sleep(0.01)

        if not st.session_state.running:
            break

    cap.release()

# ---------------- SUMMARY ----------------

if not st.session_state.running and st.session_state.counter:
    play_audio(sounds["finish"])
    duration = int(time.time() - st.session_state.start_time)

    st.success("🏁 Workout Completed!")

    # --- Workout Summary ---
    st.markdown("## 📊 Workout Summary")
    st.write(f"**Exercise:** {exercise}")
    st.write(f"**Total Reps:** {st.session_state.counter.count}")
    st.write(f"**Duration:** {duration} seconds")

    st.markdown("---")
    st.markdown("## 🌟 Great Work!")

    st.markdown("""
You did an amazing job today! Showing up and completing your workout is a big step toward becoming healthier and stronger.  
Keep believing in yourself — consistency is the key to real progress. 💪✨
""")

    st.markdown("### 💡 Helpful Tips for Better Results")
    st.markdown("""
- 💧 **Stay hydrated** — drink enough water throughout the day  
- 🍎 **Focus on balanced nutrition** — your diet fuels your progress  
- 💤 **Get proper sleep** for muscle recovery  
- 🚶 **Stay active** — even small daily movements matter  
- 😊 **Keep a positive mindset** — progress takes time, and you’re on the right path  
""")

    st.markdown("---")
    st.markdown("You're doing amazing — keep going and stay consistent! 🌟")

