import cv2
import dlib
import time
import numpy as np
from scipy.spatial import distance as dist

# ------------------ FUNCTIONS ------------------

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def shape_to_np(shape):
    coords = np.zeros((68, 2), dtype=int)
    for i in range(68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def get_head_direction(shape):
    nose_x = shape[30][0]
    left_x = shape[1][0]
    right_x = shape[15][0]

    left_dist = nose_x - left_x
    right_dist = right_x - nose_x
    ratio = left_dist / right_dist

    if ratio > 1.3:
        return "RIGHT"
    elif ratio < 0.75:
        return "LEFT"
    else:
        return "CENTER"

# ------------------ CONSTANTS ------------------

EAR_THRESHOLD = 0.20
CONSEC_FRAMES = 2
DOUBLE_BLINK_TIME = 1.0

COMMAND_COOLDOWN = 0.5  # seconds

# ------------------ VARIABLES ------------------

frame_counter = 0
last_blink_time = 0
last_command_time = 0
locked = False

current_direction = "CENTER"

# ------------------ MODELS ------------------

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# ------------------ CAMERA ------------------

cap = cv2.VideoCapture(0)
print("System ready. Turn head + double blink to confirm.")

# ------------------ MAIN LOOP ------------------

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        shape = predictor(gray, face)
        shape = shape_to_np(shape)

        # ---- HEAD DIRECTION ----
        direction = get_head_direction(shape)
        if direction != "CENTER":
            current_direction = direction

        # ---- EYE BLINK ----
        leftEye = shape[42:48]
        rightEye = shape[36:42]

        ear = (eye_aspect_ratio(leftEye) + eye_aspect_ratio(rightEye)) / 2.0

        if ear < EAR_THRESHOLD:
            frame_counter += 1
        else:
            if frame_counter >= CONSEC_FRAMES:
                now = time.time()

                if (now - last_blink_time <= DOUBLE_BLINK_TIME
                        and not locked
                        and now - last_command_time > COMMAND_COOLDOWN):

                    if current_direction == "LEFT":
                        print("COMMAND: TURN LEFT")
                    elif current_direction == "RIGHT":
                        print("COMMAND: TURN RIGHT")

                    locked = True
                    last_command_time = now

                last_blink_time = now

            frame_counter = 0

        # ---- UNLOCK AFTER COOLDOWN ----
        if locked and time.time() - last_command_time > COMMAND_COOLDOWN:
            locked = False

        # ---- UI ----
        cv2.putText(frame, f"DIR: {current_direction}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Eye + Head Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
