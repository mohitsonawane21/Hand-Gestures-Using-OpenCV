# 🖐️ AI Hand Gesture Controller

A real-time **AI-powered Hand Gesture Controller** built with Python and Computer Vision.

> **Developed by: Mohit Sonawane**

## 🚀 Project Overview

The **AI Hand Gesture Controller** provides a touch-free way to interact with a computer using hand gestures.

The system captures live video through a webcam, detects hand landmarks using **MediaPipe**, processes frames using **OpenCV**, and performs computer actions using **PyAutoGUI**.

## ✨ Features

| Gesture | Action |
|---|---|
| 🖐️ Open Palm | Play / Toggle Video |
| ✊ Fist | Pause / Toggle Video |
| 👍 Thumb Up | Increase Volume |
| 👎 Thumb Down | Decrease Volume |
| ☝️ Index Finger | Move Mouse Cursor |
| 🤏 Index + Thumb Pinch | Left Click |
| ✌️ Two Fingers | Right Click |
| ☝️ Pinky Up | Scroll Up |
| 👇 Pinky Down | Scroll Down |
| 🖐️ Three Fingers — Hold 3 Seconds | Take Screenshot |
| ⌨️ Q | Exit Program |

### 📸 Screenshot Control

Hold the **three-finger gesture for 3 seconds** to capture a screenshot.

Screenshots are saved automatically in:

```text
screenshots/
```

## 🛠️ Technologies Used

- Python 3.11
- OpenCV
- MediaPipe
- PyAutoGUI
- Visual Studio Code

## 💻 System Requirements

### Hardware
- Laptop/Desktop
- Working webcam
- Minimum 4 GB RAM
- Dual-core processor or better
- Keyboard and mouse

### Software
- Windows 10 / Windows 11
- Python 3.9–3.11
- Visual Studio Code
- Webcam drivers

## 📂 Project Structure

```text
AI_Hand_Gesture_Controller/
│
├── main.py
├── test.py
├── screenshots/
├── gesture_log.txt
├── Hand_Gesture_Controller_GitHub_Guide.pdf
└── README.md
```

> `gesture_log.txt` is created automatically if activity logging is enabled in the program version.

## ⚙️ Installation

### 1. Check Python

```powershell
python --version
```

If Windows does not recognize `python`, use:

```powershell
py --version
```

Python **3.11** is recommended.

### 2. Create a Virtual Environment

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
python -m pip install opencv-python
python -m pip install mediapipe==0.10.21
python -m pip install pyautogui
```

Or:

```powershell
python -m pip install opencv-python mediapipe==0.10.21 pyautogui
```

## ▶️ Run the Project

With the virtual environment activated:

```powershell
python main.py
```

If you use the Windows Python launcher:

```powershell
py main.py
```

## 🎮 How to Use

### 🖱️ Mouse Control
Show only your **index finger** to control the mouse cursor.

### 🤏 Left Click
Bring your **index finger and thumb together** to perform a left click.

### ✌️ Right Click
Show **two fingers** to perform a right click.

### 👍👎 Volume Control
- 👍 Thumb Up → Volume Up
- 👎 Thumb Down → Volume Down

### 🖐️✊ Video Control
- 🖐️ Open Palm → Play / Toggle Video
- ✊ Fist → Pause / Toggle Video

### 📜 Pinky Scrolling
Scrolling uses **only the pinky finger**:

- ☝️ Pinky pointing upward → Scroll Up
- 👇 Pinky pointing downward → Scroll Down

The three-finger gesture is **not used for scrolling**.

Keep the mouse cursor over the webpage, PDF, document, or other scrollable area.

### 📸 Screenshot
Show three fingers and hold the gesture for **3 seconds**.

The screenshot will be saved in the `screenshots` folder.

### ❌ Exit
Press:

```text
Q
```

to exit the program.

## 🧠 How It Works

```text
Webcam
   ↓
OpenCV Frame Capture
   ↓
MediaPipe Hand Landmark Detection
   ↓
Gesture Recognition
   ↓
Gesture Smoothing / Validation
   ↓
PyAutoGUI Computer Action
   ↓
Mouse / Volume / Media / Scroll / Screenshot
```

## 📸 Screenshot Storage

Captured screenshots are stored inside:

```text
screenshots/
```

Example:

```text
screenshots/
├── screenshot_2026-09-27_234500.png
├── screenshot_2026-09-27_234615.png
└── ...
```

## 📝 Activity Logging

If logging is enabled in the current program version, actions can also be recorded in:

```text
gesture_log.txt
```

Example:

```text
[23:45:10] THUMB UP → VOLUME UP
[23:45:13] THUMB DOWN → VOLUME DOWN
[23:45:16] PINCH → LEFT CLICK
[23:45:19] PINKY DOWN → SCROLL DOWN
```

## 🔧 Troubleshooting

### `ModuleNotFoundError: No module named 'cv2'`

```powershell
python -m pip install opencv-python
```

### `ModuleNotFoundError: No module named 'mediapipe'`

```powershell
python -m pip install mediapipe==0.10.21
```

### Webcam does not open

- Check that the webcam is connected.
- Make sure another application is not using it.
- Enable camera permissions in Windows.
- Check the camera index in the Python program.

### Gestures are inaccurate

- Keep the complete hand inside the camera frame.
- Use good lighting.
- Avoid a busy background.
- Keep a moderate distance from the camera.
- Perform one gesture at a time.
- Hold the gesture briefly so detection can stabilize.

### Scrolling is not working

1. Only the pinky should be extended.
2. Point the pinky clearly upward or downward.
3. Keep the mouse cursor over the content you want to scroll.
4. Make sure the hand is clearly visible to the webcam.

## 🔒 Privacy

The project uses the webcam locally for real-time gesture detection. Webcam frames do not need to be uploaded to an external server.

## 📌 Future Improvements

- More customizable gestures
- Multi-hand support
- Gesture calibration
- Application-specific controls
- Improved gesture confidence scoring
- Voice + gesture hybrid control
- Custom user gesture training
- Cross-platform support
- Accessibility-focused controls

## 👨‍💻 Author

### Mohit Sonawane

**Computer Engineering Student | AI & Computer Vision Enthusiast**

This project explores **Computer Vision, Hand Gesture Recognition, and Human-Computer Interaction**.

---

⭐ **Built with Python + OpenCV + MediaPipe + PyAutoGUI.**
