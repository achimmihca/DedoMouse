from util import get_time_ms
from math import sqrt
from cv2 import cv2
from MouseControl import MouseControl
from Config import Config

class GestureRecognizer:
    def __init__(self, config: Config, mouse_control: MouseControl):
        self.config = config
        self.mouse_control = mouse_control
        self.last_click_time_ms = 0

    def process_hand_landmarks(self, frame, multi_hand_landmarks):
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
        cv2.circle(frame, (index_x, index_y), 5, (255, 255, 0), -1)
        cv2.circle(frame, (thumb_x, thumb_y), 5, (0, 255, 255), -1)
        cv2.circle(frame, (wrist_x, wrist_y), 5, (255, 0, 0), -1)

        # detect mouse position
        pos_x = wrist_x
        pos_y = wrist_y
        pos_percent_x = (pos_x - self.config.motion_border_left) / (self.config.capture_width - self.config.motion_border_left - self.config.motion_border_right)
        pos_percent_x = max(0, min(1, pos_percent_x))
        pos_percent_y = (pos_y - self.config.motion_border_top) / (self.config.capture_height - self.config.motion_border_top - self.config.motion_border_bottom)
        pos_percent_y = max(0, min(1, pos_percent_y))
        mouse_x = int(self.config.screen_width * pos_percent_x)
        mouse_y = int(self.config.screen_height * pos_percent_y)

        cv2.putText(frame, f"{pos_percent_x * 100:.0f} | {pos_percent_y * 100:.0f}", (wrist_x, wrist_y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)
        
        self.mouse_control.on_new_mouse_position_detected(mouse_x, mouse_y)

        # detect click
        dist_thumb_index = sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2)
        if (dist_thumb_index < self.config.click_distance_threshold):
            if (self.last_click_time_ms + self.config.click_delay_ms < time_ms):
                self.mouse_control.on_click_detected()
            self.last_click_time_ms = time_ms