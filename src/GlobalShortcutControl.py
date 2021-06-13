from pynput import keyboard
from Config import Config

class GlobalShortcutControl:
    def __init__(self, config: Config):
        self.config = config
        self.exit_keys = [keyboard.Key.esc, keyboard.Key.f7]
        self.toggle_control_mouse_position_keys = [keyboard.Key.f9]
        self.toggle_control_click_keys = [keyboard.Key.f10]

    def start_listener(self):
        keyboard_listener = keyboard.Listener(on_press=self.on_keyboard_pressed)
        # start to listen on a separate thread
        keyboard_listener.start()  

    def on_keyboard_pressed(self, key):
        key_name = self.get_key_name(key)
        print('key pressed: ' + key_name)
        
        if key in self.exit_keys:
            print('on_keyboard_pressed - stopping main loop because of key press: ' + key_name)
            self.config.running = False
            # stop listener by returning False
            return False

        if key in self.toggle_control_mouse_position_keys:
            self.config.is_control_mouse_position = not self.config.is_control_mouse_position
            print(f"Control mouse position: {self.config.is_control_mouse_position}")

        if key in self.toggle_control_click_keys:
            self.config.is_control_click = not self.config.is_control_click
            print(f"Control click: {self.config.is_control_click}")

    def get_key_name(self, key):
        try:
            # single-char keys
            return key.char
        except:
            # other keys
            return key.name