import math

def calculate_angle(a, b, c):
    """Returns angle between 3 points."""
    ax, ay = a
    bx, by = b
    cx, cy = c

    ab = (ax - bx, ay - by)
    cb = (cx - bx, cy - by)

    dot = ab[0]*cb[0] + ab[1]*cb[1]
    mag_ab = math.sqrt(ab[0]**2 + ab[1]**2)
    mag_cb = math.sqrt(cb[0]**2 + cb[1]**2)

    if mag_ab * mag_cb == 0:
        return 0

    cos = dot / (mag_ab * mag_cb)
    cos = min(1.0, max(-1.0, cos))

    return math.degrees(math.acos(cos))


class ExerciseCounter:
    def __init__(self, exercise):
        self.exercise = exercise
        self.count = 0
        self.stage = None
        self.feedback = ""

    def update(self, lm):

        if not lm:
            return self.count, "Move into frame", False

        rep_flag = False

        # Extract major joints (RIGHT SIDE)
        shoulder = (lm[12].x, lm[12].y)
        elbow    = (lm[14].x, lm[14].y)
        wrist    = (lm[16].x, lm[16].y)

        hip      = (lm[24].x, lm[24].y)
        knee     = (lm[26].x, lm[26].y)
        ankle    = (lm[28].x, lm[28].y)

        # Main angles
        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        knee_angle  = calculate_angle(hip, knee, ankle)
        shoulder_angle = calculate_angle(elbow, shoulder, hip)

        # ------------------------------------------------
        # 1️⃣ SQUATS
        # ------------------------------------------------
        if self.exercise == "Squats":
            # DOWN position
            if knee_angle < 90:
                self.stage = "down"
                self.feedback = "Go Up"

            # UP position → COUNT REP
            if knee_angle > 160 and self.stage == "down":
                self.stage = "up"
                self.count += 1
                rep_flag = True
                self.feedback = "Perfect Squat!"

        # ------------------------------------------------
        # 2️⃣ PUSH-UPS
        # ------------------------------------------------
        elif self.exercise == "Push-ups":
            # DOWN
            if elbow_angle < 90:
                self.stage = "down"
                self.feedback = "Push Up!"

            # UP → count
            if elbow_angle > 160 and self.stage == "down":
                self.stage = "up"
                self.count += 1
                rep_flag = True
                self.feedback = "Good Push-up!"

        # ------------------------------------------------
        # 3️⃣ BICEP CURLS
        # ------------------------------------------------
        elif self.exercise == "Bicep Curls":

            # CURL UP
            if elbow_angle < 40:
                self.stage = "up"
                self.feedback = "Lower Down"

            # CURL DOWN → count
            if elbow_angle > 160 and self.stage == "up":
                self.stage = "down"
                self.count += 1
                rep_flag = True
                self.feedback = "Great Curl!"

        # ------------------------------------------------
        # 4️⃣ SHOULDER PRESS
        # ------------------------------------------------
        elif self.exercise == "Shoulder Press":

            # DOWN = hands at shoulder level
            if shoulder_angle < 40:
                self.stage = "down"
                self.feedback = "Press Up"

            # UP → count
            if shoulder_angle > 80 and self.stage == "down":
                self.stage = "up"
                self.count += 1
                rep_flag = True
                self.feedback = "Nice Press!"

        # ------------------------------------------------
        # 5️⃣ TRICEP DIPS
        # ------------------------------------------------
        elif self.exercise == "Tricep Dips":

            # DIP DOWN
            if elbow_angle < 80:
                self.stage = "down"
                self.feedback = "Push Up"

            # DIP UP → count
            if elbow_angle > 160 and self.stage == "down":
                self.stage = "up"
                self.count += 1
                rep_flag = True
                self.feedback = "Great Dip!"

        return self.count, self.feedback, rep_flag
