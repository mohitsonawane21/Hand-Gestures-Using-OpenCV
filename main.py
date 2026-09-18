import cv2
import mediapipe as mp
import pyautogui
import math
import time
import os
from datetime import datetime


# ============================================================
# HAND GESTURE CONTROLLER
# Developed by: Mohit Sonawane
# ============================================================

# -------------------- SETTINGS --------------------

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Compact webcam window for smoother performance
DISPLAY_WIDTH = 500
DISPLAY_HEIGHT = 450

SCREENSHOT_HOLD_TIME = 5.0

LEFT_CLICK_HOLD = 0.28
RIGHT_CLICK_HOLD = 0.40

LEFT_CLICK_COOLDOWN = 0.90
RIGHT_CLICK_COOLDOWN = 1.00

SCROLL_REPEAT_INTERVAL = 0.08
SCROLL_AMOUNT = 3

CURSOR_SMOOTHING = 0.35
CURSOR_DEADZONE = 8

SCREENSHOT_FOLDER = "screenshots"

os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

pyautogui.FAILSAFE = True
# PyAutoGUI pauses after every action by default; reduce it to prevent lag.
pyautogui.PAUSE = 0.01

screen_width, screen_height = pyautogui.size()


# -------------------- MEDIAPIPE --------------------

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.55,
    min_tracking_confidence=0.55
)


# -------------------- CAMERA --------------------

cap = cv2.VideoCapture(0)

# Reduce camera buffering/latency when the webcam driver supports it.
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

cv2.namedWindow(
    "Hand Gesture Controller",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "Hand Gesture Controller",
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT
)


# -------------------- VARIABLES --------------------

last_action = "Ready"
last_action_time = 0

last_left_click = 0
last_right_click = 0
last_scroll = 0

left_click_start = None
right_click_start = None

screenshot_start = None
screenshot_taken = False

previous_pinky_direction = "NONE"

smooth_x = screen_width // 2
smooth_y = screen_height // 2

fps_start = time.time()
fps_counter = 0
fps = 0


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def distance(p1, p2):
    """Calculate Euclidean distance between two landmarks."""
    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


def show_action(action):
    global last_action, last_action_time

    last_action = action
    last_action_time = time.time()


def finger_extended(landmarks, tip, pip):
    """
    Basic vertical finger extension detection.
    Works best when hand is reasonably upright.
    """
    return landmarks[tip].y < landmarks[pip].y


def get_finger_states(landmarks):
    """
    Returns:
    index, middle, ring, pinky
    """
    index = finger_extended(landmarks, 8, 6)
    middle = finger_extended(landmarks, 12, 10)
    ring = finger_extended(landmarks, 16, 14)
    pinky = finger_extended(landmarks, 20, 18)

    return index, middle, ring, pinky


def is_pinch(landmarks):
    """
    Detect index finger + thumb pinch.
    """
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]

    return distance(thumb_tip, index_tip) < 0.055


def thumb_direction(landmarks):
    """
    Detect thumb-only gesture.

    Returns:
        UP
        DOWN
        NONE
    """

    index, middle, ring, pinky = get_finger_states(landmarks)

    # Thumb gesture should have the other four fingers folded.
    if index or middle or ring or pinky:
        return "NONE"

    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    thumb_mcp = landmarks[2]

    # Thumb pointing upward
    if (
        thumb_tip.y < thumb_ip.y
        and thumb_tip.y < thumb_mcp.y - 0.04
    ):
        return "UP"

    # Thumb pointing downward
    if (
        thumb_tip.y > thumb_ip.y
        and thumb_tip.y > thumb_mcp.y + 0.04
    ):
        return "DOWN"

    return "NONE"


def is_open_palm(landmarks):
    index, middle, ring, pinky = get_finger_states(landmarks)

    return (
        index and
        middle and
        ring and
        pinky
    )


def is_fist(landmarks):
    index, middle, ring, pinky = get_finger_states(landmarks)

    # No four-finger extension
    if index or middle or ring or pinky:
        return False

    # Avoid treating thumb-up/down as a fist
    if thumb_direction(landmarks) != "NONE":
        return False

    return True


def is_index_only(landmarks):
    index, middle, ring, pinky = get_finger_states(landmarks)

    return (
        index and
        not middle and
        not ring and
        not pinky
    )


def is_two_fingers(landmarks):
    index, middle, ring, pinky = get_finger_states(landmarks)

    return (
        index and
        middle and
        not ring and
        not pinky
    )


def is_three_fingers(landmarks):
    index, middle, ring, pinky = get_finger_states(landmarks)

    return (
        index and
        middle and
        ring and
        not pinky
    )


def landmark_angle(a, b, c):
    """Return angle ABC in degrees."""
    ba_x = a.x - b.x
    ba_y = a.y - b.y
    bc_x = c.x - b.x
    bc_y = c.y - b.y

    mag_ba = math.hypot(ba_x, ba_y)
    mag_bc = math.hypot(bc_x, bc_y)

    if mag_ba == 0 or mag_bc == 0:
        return 0.0

    cosine = (ba_x * bc_x + ba_y * bc_y) / (mag_ba * mag_bc)
    cosine = max(-1.0, min(1.0, cosine))
    return math.degrees(math.acos(cosine))


def is_finger_extended_robust(landmarks, mcp, pip, tip):
    """Fast, rotation-tolerant finger extension detection."""
    return landmark_angle(
        landmarks[mcp],
        landmarks[pip],
        landmarks[tip]
    ) > 140.0


def is_pinky_only(landmarks):
    """
    Detect a pinky-only gesture using joint angles.
    This is more reliable when the hand is tilted than
    checking only the Y coordinate of each fingertip.
    """
    index_extended = is_finger_extended_robust(landmarks, 5, 6, 8)
    middle_extended = is_finger_extended_robust(landmarks, 9, 10, 12)
    ring_extended = is_finger_extended_robust(landmarks, 13, 14, 16)
    pinky_extended = is_finger_extended_robust(landmarks, 17, 18, 20)

    return (
        not index_extended
        and not middle_extended
        and not ring_extended
        and pinky_extended
    )


def get_pinky_direction(landmarks):
    """
    Fast pinky direction detection.

    Pinky UP   -> Scroll Up
    Pinky DOWN -> Scroll Down

    Only the pinky gesture is used for scrolling.
    """
    if not is_pinky_only(landmarks):
        return "NONE"

    pinky_pip = landmarks[18]
    pinky_tip = landmarks[20]

    # Use the pinky PIP -> TIP vector. This reacts faster than
    # waiting for a large movement from the MCP landmark.
    dy = pinky_tip.y - pinky_pip.y
    palm_size = max(distance(landmarks[0], landmarks[9]), 1e-6)

    # Small threshold = faster response while still filtering jitter.
    if abs(dy) < palm_size * 0.12:
        return "NONE"

    # MediaPipe Y increases downward.
    return "UP" if dy < 0 else "DOWN"


def get_palm_center(landmarks):
    wrist = landmarks[0]

    return wrist.x, wrist.y


def move_mouse(landmarks):
    """
    Move mouse using index finger position.
    """

    global smooth_x, smooth_y

    index_tip = landmarks[8]

    target_x = int(index_tip.x * screen_width)
    target_y = int(index_tip.y * screen_height)

    # Smooth cursor movement
    smooth_x = (
        smooth_x * (1 - CURSOR_SMOOTHING)
        + target_x * CURSOR_SMOOTHING
    )

    smooth_y = (
        smooth_y * (1 - CURSOR_SMOOTHING)
        + target_y * CURSOR_SMOOTHING
    )

    current_x, current_y = pyautogui.position()

    new_x = int(smooth_x)
    new_y = int(smooth_y)

    # Deadzone prevents tiny unwanted movement
    if (
        abs(new_x - current_x) > CURSOR_DEADZONE
        or
        abs(new_y - current_y) > CURSOR_DEADZONE
    ):
        pyautogui.moveTo(
            new_x,
            new_y,
            duration=0
        )


def take_screenshot():
    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    filename = os.path.join(
        SCREENSHOT_FOLDER,
        f"screenshot_{timestamp}.png"
    )

    image = pyautogui.screenshot()
    image.save(filename)

    return filename


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = cap.read()

    if not success:
        print("Unable to access webcam.")
        break

    # Mirror webcam
    frame = cv2.flip(frame, 1)

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    result = hands.process(rgb_frame)

    current_gesture = "No Hand"

    # --------------------------------------------------------
    # HAND DETECTED
    # --------------------------------------------------------

    if result.multi_hand_landmarks:

        hand_landmarks = result.multi_hand_landmarks[0]

        # Draw hand landmarks
        mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS
        )

        lm = hand_landmarks.landmark

        # ----------------------------------------------------
        # THUMB UP / DOWN
        # ----------------------------------------------------

        thumb_state = thumb_direction(lm)

        if thumb_state == "UP":

            current_gesture = "Thumb Up"

            pyautogui.press("volumeup")
            show_action("Volume Up")

        elif thumb_state == "DOWN":

            current_gesture = "Thumb Down"

            pyautogui.press("volumedown")
            show_action("Volume Down")

        # ----------------------------------------------------
        # SCREENSHOT — 3 FINGERS FOR 5 SECONDS
        # ----------------------------------------------------

        elif is_three_fingers(lm):

            current_gesture = "3 Fingers - Hold 5 sec"

            if screenshot_start is None:
                screenshot_start = time.time()
                screenshot_taken = False

            hold_time = time.time() - screenshot_start

            if hold_time >= SCREENSHOT_HOLD_TIME:

                if not screenshot_taken:

                    filename = take_screenshot()

                    show_action("Screenshot Saved")

                    screenshot_taken = True

        else:

            # Reset screenshot timer
            screenshot_start = None
            screenshot_taken = False

            # ------------------------------------------------
            # OPEN PALM
            # ------------------------------------------------

            if is_open_palm(lm):

                current_gesture = "Open Palm"

                if time.time() - last_action_time > 0.8:

                    pyautogui.press("space")
                    show_action("Play / Toggle")

            # ------------------------------------------------
            # PINKY SCROLL
            # ------------------------------------------------

            elif is_pinky_only(lm):

                pinky_direction = get_pinky_direction(lm)
                current_time = time.time()

                if pinky_direction == "UP":

                    current_gesture = "Pinky Up - Scroll Up"

                    # Keep scrolling while the pinky remains UP.
                    if current_time - last_scroll >= SCROLL_REPEAT_INTERVAL:
                        pyautogui.scroll(SCROLL_AMOUNT)
                        show_action("Scroll Up")
                        last_scroll = current_time

                    previous_pinky_direction = "UP"

                elif pinky_direction == "DOWN":

                    current_gesture = "Pinky Down - Scroll Down"

                    # Keep scrolling while the pinky remains DOWN.
                    if current_time - last_scroll >= SCROLL_REPEAT_INTERVAL:
                        pyautogui.scroll(-SCROLL_AMOUNT)
                        show_action("Scroll Down")
                        last_scroll = current_time

                    previous_pinky_direction = "DOWN"

                else:

                    current_gesture = "Pinky - Direction unclear"
                    previous_pinky_direction = "NONE"

            else:

                # Reset pinky direction
                previous_pinky_direction = "NONE"

                # ------------------------------------------------
                # PINCH — LEFT CLICK
                # ------------------------------------------------

                if (
                    is_pinch(lm)
                    and
                    is_index_only(lm)
                ):

                    current_gesture = "Pinch - Left Click"

                    if left_click_start is None:
                        left_click_start = time.time()

                    held_time = (
                        time.time()
                        - left_click_start
                    )

                    if (
                        held_time >= LEFT_CLICK_HOLD
                        and
                        time.time() - last_left_click
                        > LEFT_CLICK_COOLDOWN
                    ):

                        pyautogui.click()

                        show_action("Left Click")

                        last_left_click = time.time()

                        left_click_start = None

                else:

                    left_click_start = None

                    # --------------------------------------------
                    # TWO FINGERS — RIGHT CLICK
                    # --------------------------------------------

                    if (
                        is_two_fingers(lm)
                        and
                        not is_pinch(lm)
                    ):

                        current_gesture = "Two Fingers - Right Click"

                        if right_click_start is None:
                            right_click_start = time.time()

                        held_time = (
                            time.time()
                            - right_click_start
                        )

                        if (
                            held_time >= RIGHT_CLICK_HOLD
                            and
                            time.time() - last_right_click
                            > RIGHT_CLICK_COOLDOWN
                        ):

                            pyautogui.rightClick()

                            show_action("Right Click")

                            last_right_click = time.time()

                            right_click_start = None

                    else:

                        right_click_start = None

                        # ----------------------------------------
                        # INDEX FINGER — MOUSE
                        # ----------------------------------------

                        if is_index_only(lm):

                            current_gesture = "Index - Mouse"

                            move_mouse(lm)

                        # ----------------------------------------
                        # FIST — PAUSE / TOGGLE
                        # ----------------------------------------

                        elif is_fist(lm):

                            current_gesture = "Fist"

                            if time.time() - last_action_time > 0.8:

                                pyautogui.press("space")

                                show_action("Pause / Toggle")

                        else:

                            current_gesture = "Unknown"


    else:

        # No hand
        screenshot_start = None
        screenshot_taken = False
        left_click_start = None
        right_click_start = None

        previous_pinky_direction = "NONE"


    # ========================================================
    # FPS CALCULATION
    # ========================================================

    fps_counter += 1

    elapsed = time.time() - fps_start

    if elapsed >= 1:

        fps = fps_counter / elapsed

        fps_counter = 0
        fps_start = time.time()


    # ========================================================
    # UI
    # ========================================================

    cv2.rectangle(
        frame,
        (10, 10),
        (590, 190),
        (0, 0, 0),
        -1
    )

    cv2.putText(
        frame,
        "HAND GESTURE CONTROLLER",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"Gesture: {current_gesture}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"Action: {last_action}",
        (20, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (20, 140),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "Q = Exit",
        (20, 170),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


    # Screenshot countdown
    if screenshot_start is not None:

        hold_time = time.time() - screenshot_start

        remaining = max(
            0,
            SCREENSHOT_HOLD_TIME - hold_time
        )

        cv2.putText(
            frame,
            f"Screenshot in: {remaining:.1f}s",
            (400, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )


    # Display frame
    cv2.imshow(
        "Hand Gesture Controller",
        frame
    )


    # ========================================================
    # EXIT
    # ========================================================

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()
cv2.destroyAllWindows()
hands.close()

print("\n======================================")
print(" Hand Gesture Controller")
print(" Developed by: Mohit Sonawane")
print(" Program Closed Successfully")
print("======================================")
