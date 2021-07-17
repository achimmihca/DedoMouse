from typing import Any
from cv2 import cv2 # type: ignore
import mediapipe as mp # type: ignore
from Config import Config
from GestureRecognizer import GestureRecognizer

class WebcamControl:
    def __init__(self, config: Config, gesture_regocnizer: GestureRecognizer):
        self.config = config
        self.gesture_regocnizer = gesture_regocnizer

    def start_video_capture(self) -> None:
        if not self.config.running:
            return

        cap = cv2.VideoCapture(0)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.capture_size.x)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.capture_size.y)
        cap.set(cv2.CAP_PROP_FPS, self.config.capture_fps)

        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"Frames per second: {fps}")

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

    def draw_overlay(self, frame: Any) -> None:
        pass
