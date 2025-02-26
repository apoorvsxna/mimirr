from typing import List, Optional, Union
from pynput.keyboard import Key, KeyCode, Controller
from time import sleep
from .config import ServerConfig

class GamepadManager:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.keyboard = Controller()
        self.gamepads = []
        self._initialize_gamepads()

    def _initialize_gamepads(self) -> None:
        """Initialize virtual Xbox 360 gamepads."""
        try:
            from vgamepad import VX360Gamepad
            self.gamepads = [VX360Gamepad() for _ in range(self.config.max_gamepads)]
            if self.config.debug:
                print(f"Successfully initialized {len(self.gamepads)} virtual gamepads")
        except ModuleNotFoundError:
            print("vgamepad module not found. Virtual gamepad support disabled.")
        except Exception as e:
            print(f"Failed to initialize gamepads: {e}")

    def get_key(self, key_name: str) -> Union[Key, KeyCode, str]:
        """Convert string key name to pynput key object."""
        if len(key_name) > 1:
            return KeyCode(int(key_name)) if key_name.isdigit() else Key[key_name]
        return key_name

    def execute_command(self, client, command: str, key: str, player: int, use_gamepad: bool = False) -> None:
        """Execute keyboard or gamepad command."""
        if self.config.debug:
            print(f'[PLAYER {player + 1}] Command: {command}, Key: {key}')

        try:
            if use_gamepad:
                self._handle_gamepad_command(client, command, key, player)
            else:
                self._handle_keyboard_command(command, key)
        except Exception as e:
            if self.config.debug:
                print(f"Error executing command: {e}")
            client.sendMessage(f"ERROR: {str(e)}")

    def _handle_gamepad_command(self, client, command: str, key: str, player: int) -> None:
        """Handle gamepad-specific commands."""
        if not self.gamepads:
            client.sendMessage('INFO: Virtual gamepad control is not available')
            return

        if command.startswith('vj'):  # Virtual joystick command
            self._handle_joystick(command, key, player)
        else:  # Button command
            self._handle_button(command, key, player)

    def _handle_joystick(self, command: str, key: str, player: int) -> None:
        """Handle joystick movement commands."""
        try:
            x, y = map(int, key.split('|'))
            # Map the input values (0-65535) to the correct range (-32768 to 32767)
            x = max(-32768, min(32767, x - 32768))
            y = max(-32768, min(32767, y - 32768))
            
            if command == 'vjl':  # Left joystick
                self.gamepads[player].left_joystick(x_value=x, y_value=y)
            else:  # Right joystick
                self.gamepads[player].right_joystick(x_value=x, y_value=y)
            
            self.gamepads[player].update()
        except Exception as e:
            if self.config.debug:
                print(f"Error handling joystick: {e}")

    def _handle_button(self, command: str, key: str, player: int) -> None:
        """Handle gamepad button commands."""
        try:
            from vgamepad import XUSB_BUTTON
            
            def press_button(pressed: bool) -> None:
                value = 255 if pressed else 0
                if key == 'xusb_gamepad_left_trigger':
                    self.gamepads[player].left_trigger(value=value)
                elif key == 'xusb_gamepad_right_trigger':
                    self.gamepads[player].right_trigger(value=value)
                else:
                    method = 'press_button' if pressed else 'release_button'
                    getattr(self.gamepads[player], method)(button=XUSB_BUTTON[key.upper()])

            if command == 'p':  # Press
                press_button(True)
            elif command == 'r':  # Release
                press_button(False)
            elif command == 't':  # Tap (press and release)
                press_button(True)
                self.gamepads[player].update()
                sleep(self.config.button_press_time)
                press_button(False)

            self.gamepads[player].update()
        except Exception as e:
            if self.config.debug:
                print(f"Error handling button: {e}")

    def _handle_keyboard_command(self, command: str, key: Union[Key, KeyCode, str]) -> None:
        """Handle keyboard-specific commands."""
        try:
            if command == 'p':  # Press
                self.keyboard.press(key)
            elif command == 'r':  # Release
                self.keyboard.release(key)
            elif command == 't':  # Tap
                self.keyboard.press(key)
                sleep(self.config.button_press_time)
                self.keyboard.release(key)
        except Exception as e:
            if self.config.debug:
                print(f"Error handling keyboard command: {e}")