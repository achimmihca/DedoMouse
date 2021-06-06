import screeninfo
import cv2
import numpy as np
import mediapipe as mp
from math import sqrt
from pynput import keyboard
from pynput.mouse import Button, Controller
import time

def get_time_ms():
    return time.time_ns() // 1_000_000 

##########################################################
# Keyboard Listener
##########################################################

def on_keyboard_pressed(key):
    global do_loop
    try:
        key_name = key.char  # single-char keys
    except:
        key_name = key.name  # other keys
    
    if key == keyboard.Key.esc or key_name == 'esc' or key_name == 'space':
        print('on_keyboard_pressed - stopping main loop because of key press: ' + key_name)
        do_loop = False
        return False  # stop listener
    print('Key pressed: ' + key_name)

keyboard_listener = keyboard.Listener(on_press=on_keyboard_pressed)
keyboard_listener.start()  # start to listen on a separate thread

#########################################################
# Get screen size
#########################################################

screen_width = 0
screen_height = 0
for monitor in screeninfo.get_monitors():
    # assume horizontal alignment of monitors in landscape orientation
    screen_width += monitor.width
    screen_height = max(screen_height, monitor.height)

if screen_width <= 0 or screen_height <= 0:
    raise "could not determine screen size"

print(f"screen size: {screen_width} x {screen_height}")

##########################################################
# Control mouse via webcam and hand movement
##########################################################

click_distance_threshold = 20

last_click_time_ms = 0
click_delay_ms = 500
do_loop = True

damping_factor = 2

capture_width = 640
capture_height = 480

# Motion does not (cannot) use the full capture range
motion_border_percent = 0.2
motion_border_x = capture_width * motion_border_percent
motion_border_y = capture_height * motion_border_percent

mouse_controller  = Controller()

def process_hand_landmarks(frame, multi_hand_landmarks):
    global damping_factor
    global capture_width
    global capture_height
    global screen_width
    global screen_height
    global mouse_controller
    global motion_border_y
    global motion_border_x
    global last_click_time_ms

    time_ms = get_time_ms()

    wrist_x = 0
    wrist_y = 0
    thumb_x = 0
    thumb_y = 0

    # find landmark positions
    for hand_landmarks in multi_hand_landmarks:
        for landmark_id, landmark in enumerate(hand_landmarks.landmark):
            h, w, c = frame.shape
            try:
                if landmark_id == 0:
                    wrist_x, wrist_y = int(landmark.x * w), int(landmark.y * h)
                if landmark_id == 4:
                    thumb_x, thumb_y = int(landmark.x * w), int(landmark.y * h)
                if landmark_id == 8:
                    index_x, index_y = int(landmark.x * w), int(landmark.y * h)
            except:
                pass

    # draw landmark positions
    cv2.circle(frame, (index_x, index_y), 5, (0, 255, 0), -1)
    cv2.circle(frame, (thumb_x, thumb_y), 5, (0, 255, 255), -1)
    cv2.circle(frame, (wrist_x, wrist_y), 4, (255, 255, 255), 1)

    # position mouse
    pos_x = wrist_x
    pos_y = wrist_y
    pos_percent_x = (pos_x - motion_border_x) / (capture_width - motion_border_x * 2)
    pos_percent_x = max(0, min(1, pos_percent_x))
    pos_percent_y = (pos_y - motion_border_y) / (capture_height - motion_border_y * 2)
    pos_percent_y = max(0, min(1, pos_percent_y))
    mouse_x = int(screen_width * pos_percent_x)
    mouse_y = int(screen_height * pos_percent_y)

    mouse_controller.position = (mouse_x, mouse_y)

    # perform click
    dist_thumb_index = sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2)
    if dist_thumb_index < click_distance_threshold and (last_click_time_ms + click_delay_ms < time_ms):
        last_click_time_ms = time_ms
        cv2.putText(frame, "Click", (185, 22), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 255, 0), 2)
        mouse_controller.click(Button.left, 1)

def start_webcam():
    global do_loop
    global capture_width
    global capture_height
    global screen_width
    global screen_height
    global mouse_controller

    if not do_loop:
        return

    cap = cv2.VideoCapture(0)
    cap.set(3, capture_width)
    cap.set(4, capture_height)

    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=1)
    
    while do_loop:
        ret,frame = cap.read()
        
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        
        cv2.rectangle(frame, (10, 10), (20, 20), (0, 255, 255), -1)
        cv2.putText(frame, "Double Click", (25, 22), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 255, 255), 1)

        cv2.rectangle(frame, (170, 10), (180, 20), (0, 255, 0), -1)
        cv2.putText(frame, "Click", (185, 22), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 255, 0), 1)

        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            process_hand_landmarks(frame, results.multi_hand_landmarks)

        cv2.imshow("Dedo Mouse", frame)
        cv2.waitKey(33)

    cap.release()
    cv2.destroyAllWindows()

start_webcam()