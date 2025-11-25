# 💪 AI Workout Tracker

AI Workout Tracker is a real-time, webcam-based fitness assistant that tracks your exercise repetitions using computer vision and pose detection.  
No smart devices or sensors needed — simply enable your webcam, choose an exercise, and start moving!

This project helps you stay consistent, track your reps accurately, and get instant feedback and motivational summaries.

---

## 🚀 Features

- 🎥 **Real-time webcam tracking**
- 🤖 **AI-powered pose detection (MediaPipe)**
- 🔁 **Automatic rep counting** for:
  - Squats  
  - Push-ups  
  - Bicep Curls  
  - Shoulder Press  
  - Tricep Dips  
- 🔊 **Audio cues** (start, perfect, keep going, finish)
- 💬 **Motivational workout summary**
- ✔️ **Simple UI built with Streamlit**
- 🌐 **Cloud-friendly deployment**

---

## 🧠 How It Works

The app uses MediaPipe Pose to detect body landmarks and compute joint angles.  
Each exercise has its own logic to detect:

- Down position  
- Up position  
- Complete rep cycle  
- Form-based feedback  

The app tracks your reps and displays a workout summary at the end.


---

## 🛠️ Installation (Local)

### 1️⃣ Clone the repo
git clone https://github.com/VardhanRaj369/AI_Workout_Tracker.git  \n
cd ai-workout-tracker
streamlit run app.py
3️⃣ Run the app
streamlit run app.py

🧩 Tech Stack

Python 3.10+

Streamlit (UI)

MediaPipe 0.10.21 (pose detection)

OpenCV (video processing)

NumPy (math calculations)
