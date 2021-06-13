from Config import Config
from cv2 import cv2
from GestureRecognizer import GestureRecognizer
import mediapipe as mp

class WebcamControl:
    def __init__(self, config: Config, gesture_regocnizer: GestureRecognizer):
        self.config = config
        self.gesture_regocnizer = gesture_regocnizer

    def start_video_capture(self):
        global mouse_controller

        if not self.config.running:
            return

        cap = cv2.VideoCapture(0)
        cap.set(3, self.config.capture_width)
        cap.set(4, self.config.capture_height)

        hands = mp.solutions.hands.Hands(max_num_hands=1)
        
        while self.config.running:
            ret,frame = cap.read()
            
            # mirror vertically
            frame = cv2.flip(frame, 1)
            
            # analyze image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                self.gesture_regocnizer.process_hand_landmarks(frame, results.multi_hand_landmarks)

            # draw overlay
            self.draw_overlay(frame)
            
            cv2.imshow("Dedo Mouse", frame)
            cv2.waitKey(33)

        cap.release()
        cv2.destroyAllWindows()

    def draw_overlay(self, frame):
        cv2.rectangle(frame, (10, 10), (20, 20), (0, 255, 255), -1)
        cv2.putText(frame, "Double Click", (25, 22), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 255, 255), 1)

        cv2.rectangle(frame, (170, 10), (180, 20), (0, 255, 0), -1)
        cv2.putText(frame, "Click", (185, 22), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 255, 0), 1)

