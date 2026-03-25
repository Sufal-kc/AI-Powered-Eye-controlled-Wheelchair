import cv2
import time

# ─── Configuration ───────────────────────────────────────────────
BLINK_THRESHOLD     = 0.25      # max duration to consider normal blink (seconds)
DOUBLE_BLINK_WINDOW = 0.7       # max time between two blinks to consider double (seconds)
LONG_BLINK_THRESHOLD = 1.2      # longer than this → long blink (optional)

# ─── Init ────────────────────────────────────────────────────────
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade  = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

cap = cv2.VideoCapture(0)
cv2.namedWindow("Eye Blink Control", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Eye Blink Control", 640, 480)

# State variables
eyes_were_open = True           # previous frame state
blink_start_time = None
last_blink_time = 0
blink_count_in_window = 0
car_running = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    eyes_detected_this_frame = False

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=4, minSize=(25,25))

        if len(eyes) >= 1:  # at least one eye visible → consider open
            eyes_detected_this_frame = True

        # Optional: draw eyes
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 100), 2)

        # Optional: draw face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 180, 100), 2)

    current_time = time.time()

    # ─── Blink state machine ─────────────────────────────────────
    if eyes_detected_this_frame:
        # Eyes are open now
        if not eyes_were_open:
            # Just opened eyes → blink ended
            if blink_start_time is not None:
                duration = current_time - blink_start_time

                if duration <= BLINK_THRESHOLD:
                    # Normal short blink
                    if current_time - last_blink_time <= DOUBLE_BLINK_WINDOW:
                        blink_count_in_window += 1
                    else:
                        blink_count_in_window = 1

                    last_blink_time = current_time
                    print(f"Blink detected! Count in window: {blink_count_in_window}")

                    # Decide action
                    if blink_count_in_window >= 2:
                        car_running = not car_running
                        print("DOUBLE BLINK → Car", "STARTED" if car_running else "STOPPED")
                        blink_count_in_window = 0  # reset after action

                elif duration >= LONG_BLINK_THRESHOLD:
                    print(f"Long blink detected ({duration:.2f}s)")

                # else: medium length blink → ignored

        eyes_were_open = True
        blink_start_time = None

    else:
        # No eyes detected → probably closed
        if eyes_were_open:
            # Just closed eyes → blink started
            blink_start_time = current_time

        eyes_were_open = False

    # ─── Visual feedback ─────────────────────────────────────────
    status = "RUNNING" if car_running else "STOPPED"
    color = (0, 255, 0) if car_running else (0, 0, 255)

    cv2.putText(frame, f"CAR: {status}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)
    cv2.putText(frame, f"blinks: {blink_count_in_window}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 50), 2)

    cv2.imshow("Eye Blink Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()