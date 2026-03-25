import cv2
import time

# Load Haar cascades
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier("haarcascade_eye.xml")

# Initialize video capture
cap = cv2.VideoCapture(0)

# Blink tracking variables
blink_start_time = 0
last_blink_time = 0
blink_counter = 0
blink_cooldown = 0.2  # min blink duration in seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    eyes_detected = False

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) > 0:
            eyes_detected = True
        # Draw rectangle around eyes (optional)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 2)

    current_time = time.time()

    # Blink detection logic
    if not eyes_detected:
        if blink_start_time == 0:
            blink_start_time = current_time
    else:
        if blink_start_time != 0:
            blink_duration = current_time - blink_start_time
            if blink_duration >= blink_cooldown:
                # Count blink
                if current_time - last_blink_time <= 1.0:
                    blink_counter += 1
                else:
                    blink_counter = 1
                last_blink_time = current_time

                # Double blink check
                if blink_counter >= 2:
                    print("Double blink detected!")
                    blink_counter = 0

            blink_start_time = 0

    # Show frame (optional)
    cv2.imshow("Blink Detector", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
