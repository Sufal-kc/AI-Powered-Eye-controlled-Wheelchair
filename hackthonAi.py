import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
import socket
import time

# ---------------- BLUETOOTH SETTINGS ----------------
BT_ADDR = "00:00:13:10:42:FE"  # Replace with your HC-05 MAC
BT_CHANNEL = 4                 # RFCOMM channel

# ---------------- CONNECT TO HC-05 ----------------
try:
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.connect((BT_ADDR, BT_CHANNEL))
    print("Bluetooth connected!")
except Exception as e:
    print("Bluetooth connection failed:", e)
    sock = None

# ---------------- DLIB MODELS ----------------
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# ---------------- CONSTANTS ----------------
EAR_THRESHOLD = 0.20
CONSEC_FRAMES = 2
DOUBLE_BLINK_TIME = 1.0
COMMAND_INTERVAL = 0.2

# ---------------- VARIABLES ----------------
frame_counter = 0
last_blink_time = 0
last_command_time = 0
prev_command = None

# ---------------- FUNCTIONS ----------------
def shape_to_np(shape):
    coords = np.zeros((68, 2), dtype=int)
    for i in range(68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

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

def send_command(cmd):
    global prev_command, last_command_time, sock
    current_time = time.time()
    
    if not sock:
        print("Bluetooth not connected. Cannot send:", cmd)
        return
    
    if cmd != prev_command or (current_time - last_command_time > COMMAND_INTERVAL):
        try:
            sock.send(cmd.encode())
            print("Sent command:", cmd)
            
            # wait for Arduino confirmation
            sock.settimeout(0.5)
            try:
                response = sock.recv(1024).decode().strip()
                print("Arduino response:", response)
                if response != "OK":
                    print("Arduino rejected command, stopping")
                    sock.send('S'.encode())
                    prev_command = 'S'
            except socket.timeout:
                print("No response from Arduino, stopping")
                sock.send('S'.encode())
                prev_command = 'S'
            
            prev_command = cmd
            last_command_time = current_time
        except Exception as e:
            print("Bluetooth send failed:", e)
            sock.close()
            sock = None

# ---------------- CAMERA SETUP ----------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot access camera")
    exit()

print("Starting eye/head control. Press 'q' to quit.")

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        shape = predictor(gray, face)
        shape = shape_to_np(shape)

        leftEye = shape[42:48]
        rightEye = shape[36:42]
        ear = (eye_aspect_ratio(leftEye) + eye_aspect_ratio(rightEye)) / 2.0

        # ---------- BLINK LOGIC ----------
        if ear < EAR_THRESHOLD:
            frame_counter += 1
        else:
            if frame_counter >= CONSEC_FRAMES:
                current_time = time.time()
                if current_time - last_blink_time <= DOUBLE_BLINK_TIME:
                    send_command('S')  # stop on double blink
                    print("Double blink detected → Car STOP/START toggle")
                last_blink_time = current_time
            frame_counter = 0

        # ---------- HEAD DIRECTION LOGIC ----------
        direction = get_head_direction(shape)
        if direction == "LEFT":
            send_command('L')
        elif direction == "RIGHT":
            send_command('R')
        else:
            send_command('F')

        # ---------- DISPLAY FRAME ----------
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"HEAD: {direction}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    cv2.imshow("Eye & Head Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if sock:
    sock.close()
