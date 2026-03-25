# Eye Controlled Wheelchair

A prototype assistive mobility system that maps eye blink and head pose gestures to vehicle movement commands, with Bluetooth HC-05 communication to Arduino platform.

## Project overview
This project was developed by 4 students in Taranga Hardware Hackthon.

This repository implements multiple approaches for detecting:

- face / eye presence via OpenCV 
- eye blink detection via Eye Aspect Ratio (EAR) using dlib facial landmarks
- head direction (left/center/right) via nose/face geometry
- double-blink toggle behavior

One script supports Bluetooth/RFCOMM control to send motor commands to a microcontroller.

### Core goals

- hands-free direction control for wheelchair-like vehicle
- blink-based START/STOP toggle
- (variant) left/right driving via head orientation
- robustness through blink cooldown / double blink windows

---

## 📁 Repository content

- `AI Powered Eye Controlled Assistive Mobility System.pptx`  
  project slide 
- `blink.py`  
  basic OpenCV Haar cascade blink presence detector + double-blink alert (console)
- `hackthonAi.py`  
  full feature: dlib EAR + direction + HC-05 Bluetooth commands + Arduino feedback handshake
- `step2_face.py`  
  refined OpenCV blinking with start/stop state and visual status in UI
- `shape.py`  
  reusable dlib-based head direction + blink detection + command lock gate (non-Bluetooth)
- `bluetooth.py`  
  empty placeholder, unused in current code
- `haarcascade_eye.xml`, `haarcascade_frontalface_default.xml`  
  detector models for `blink.py` and `step2_face.py`
- `shape_predictor_68_face_landmarks.dat` (required externally, not in repo)

---

## 🛠️ Requirements

### Hardware
- USB camera (but we used laptop camera here) 0
- Bluetooth HC-05 module + Arduino 
- Powered wheelchair/robot with serial command acceptance (e.g., `L`, `R`, `F`, `S`)

### Software
- Python 3.8+
- `pip` packages:
  - `opencv-python`
  - `dlib`
  - `numpy`
  - `scipy`
- (Linux/Mac/Win) Python socket BTPROTO_RFCOMM might require proper Bluetooth support.
- `shape_predictor_68_face_landmarks.dat` (dlib model file) in working directory.

---

## ▶️ Installation

```bash
cd "c:/Users/Predator/Downloads/Eye Controlled Wheelchair/Eye Controlled Wheelchair"

python -m venv venv
venv\Scripts\activate   # Windows
pip install opencv-python dlib numpy scipy
```

Download dlib shape model:
- `http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2`
- unzip to same folder.

---

## ▶️ Usage

### 1. blink.py (quick test)
```bash
python blink.py
```
- detects closed eyes vs open using Haar
- prints `Double blink detected!`

### 2. step2_face.py (car start/stop via blink)
```bash
python step2_face.py
```
- Best blink window constants:
  - blink <=0.25 sec = valid
  - 2 blinks within 0.7 sec toggles `car_running`
- UI shows `CAR: RUNNING`/`STOPPED`

### 3. shape.py (head+double blink command simulation)
```bash
python shape.py
```
- prints `COMMAND: TURN LEFT/RIGHT`
- requires dlib model + webcam

### 4. hackthonAi.py (Bluetooth wheelchair command)
```bash
python hackthonAi.py
```
- Bluetooth HC-05 MAC: `BT_ADDR="00:00:13:10:42:FE"` (edit as needed)
- commands:
  - `F` forward center
  - `L` left
  - `R` right
  - `S` stop
- double blink triggers `S` stop command
- includes send confirmation with expected receiver response `"OK"`; else auto send `'S'`.

---

## ⚙️ Behavior summary

### Blink detection methods
- `blink.py` / `step2_face.py`: OpenCV Haar-based eye detection
- `hackthonAi.py`, `shape.py`: dlib landmarks and EAR metrics

### Head direction
- measured by ratio of nose x coordinate to left/right facial boundary:
  - `RIGHT` if ratio > 1.3
  - `LEFT` if ratio < 0.75
  - `CENTER` otherwise

---

## 💡 Improvements / next steps

1. integrate gaze estimation model and automatic calibration
2. use CNN face landmarks instead of pure dlib 68 points
3. use cam module + esp32 more robust development
4. robust Bluetooth connection recovery

---

## 🛡️ Safety

- Do not run on real wheelchair without:
  - emergency physical kill switch 
  - supervised user
  - safety protocols for false positives
- Treat as prototype research / POC, not medical device.

---

## 📌 FAQ

Q: Can i use it for further research
A: Yes; but would suggest to contact us as a permission before using it

Q: `shape_predictor_68_face_landmarks.dat` missing?
A: Download from dlib site before running dlib-based scripts.

Q: How to stop?
A: Press `q` window or terminate process.

---
