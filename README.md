💪 AI Workout Tracker
Real-time exercise counting & posture analysis using AI + MediaPipe + Streamlit

The AI Workout Tracker is a real-time fitness application that uses computer vision to analyze human movements through your webcam.
It automatically tracks Push-ups, Squats, Bicep Curls, Jumping Jacks, and Shoulder Press, counts reps, monitors posture angles, and generates a complete workout summary report.

Built with Streamlit, MediaPipe, OpenCV, Plotly, and streamlit-webrtc.

🚀 Features
🎥 Real-Time Computer Vision

Detects human pose via MediaPipe Pose

Tracks landmarks accurately

Draws live skeleton overlay

Works directly in the browser with webcam

🧮 Automatic Rep Counting

Custom logic for each exercise:

Push-ups → elbow angle

Squats → knee angle

Bicep Curls → elbow flexion

Jumping Jacks → wrist distance

Shoulder Press → vertical arm movement

📊 Detailed Workout Report

After finishing your workout:

Total reps

Duration

Reps per minute

Calories burned

Performance score

Fitness recommendations

Interactive gauge chart

🎨 Clean UI

Sidebar workout selection

Exercise instructions

Elegant metrics & charts

Supports light/dark themes

🧰 Tech Stack
Category	Technologies / Tools
Frontend	Streamlit, Custom CSS, Plotly (Visualizations)
Backend / Core Logic	Python 3, MediaPipe Pose, OpenCV, NumPy
WebRTC / Live Video	streamlit-webrtc, aiortc, av
Data Visualization	Plotly Graph Objects
Real-Time Tracking	Pose estimation, Angle calculations, Rep counting logic
Deployment	Streamlit Cloud / Local Execution
Environment	cv2, mediapipe, numpy, streamlit, streamlit-webrtc, plotly
📂 Project Structure
/
├── app.py                     # Main Streamlit application
├── requirements.txt           # Dependencies
└── README.md                  # Documentation

🛠️ Installation & Setup
1️⃣ Clone the Repository
git clone <your-repo-url>
cd AI_Workout_Tracker

2️⃣ Create Virtual Environment (Optional)
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

3️⃣ Install Dependencies
pip install -r requirements.txt

▶️ Run the App Locally
streamlit run app.py


App will open at:

http://localhost:8501

🧠 How It Works
1. Pose Detection

MediaPipe extracts:

33 body landmarks

Skeletal connections

Coordinates for angle calculation

2. Angle Calculations

Example: elbow or knee angles computed using arctan2.

3. Rep Counting Logic

Each exercise has thresholds:

Exercise	Parameter	Logic
Push-ups	Elbow angle	>160° → UP, <90° → DOWN (rep counted)
Squats	Knee angle	>160° → UP, <100° → DOWN
Bicep Curls	Elbow	>160° → DOWN, <30° → UP
Jumping Jacks	Wrist distance	>0.3 → UP, <0.15 → DOWN
Shoulder Press	Vertical movement	>0.15 → DOWN, <−0.1 → UP
4. Workout Report Generation

After “Finish Workout”:

Total reps

Duration

Calories burned (rep × 0.5)

Reps/min

Performance score

Fitness tips

Gauge visualization (Plotly)


📦 requirements.txt (Recommended)
streamlit
opencv-python
mediapipe
numpy
plotly
streamlit-webrtc
av
aiortc



🤝 Contributing

Pull requests are welcome!
Feel free to add:

More exercises

Voice feedback

History dashboard

AI form-correction

⭐ Support

If this project helped you, please ⭐ star the repo — it motivates me to build more features!
