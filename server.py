#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from time import sleep
from typing import List, Optional
from dataclasses import dataclass
from pynput.keyboard import Key, KeyCode, Controller
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

@dataclass
class ServerConfig:
    http_port: int = 8080
    ws_port: int = 8000
    debug: bool = True
    max_gamepads: int = 4

class GamepadManager:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.keyboard = Controller()
        self.gamepads = []
        self._initialize_gamepads()

    def _initialize_gamepads(self) -> None:
        try:
            from vgamepad import VX360Gamepad
            self.gamepads = [VX360Gamepad() for _ in range(self.config.max_gamepads)]
            if self.config.debug:
                print(f"Successfully initialized {len(self.gamepads)} virtual gamepads")
        except ModuleNotFoundError:
            print("vgamepad module not found. Virtual gamepad support disabled.")
        except Exception as e:
            print(f"Failed to initialize gamepads: {e}")

    def get_key(self, key_name: str) -> Key | KeyCode | str:
        """Convert string key name to pynput key object."""
        if len(key_name) > 1:
            return KeyCode(int(key_name)) if key_name.isdigit() else Key[key_name]
        return key_name

    def execute_command(self, client: WebSocket, command: str, key: str, player: int, use_gamepad: bool = False) -> None:
        """Execute keyboard or gamepad command."""
        if self.config.debug:
            print(f'[PLAYER {player + 1} COMMAND] {key}')

        try:
            if use_gamepad:
                self._handle_gamepad_command(client, command, key, player)
            else:
                self._handle_keyboard_command(command, key)
        except Exception as e:
            if self.config.debug:
                print(f"Error executing command: {e}")
            client.sendMessage(f"ERROR: {str(e)}")

    def _handle_gamepad_command(self, client: WebSocket, command: str, key: str, player: int) -> None:
        """Handle gamepad-specific commands."""
        if not self.gamepads:
            client.sendMessage('INFO: Virtual gamepad control is not available')
            return

        if command in ('vjl', 'vjr'):
            self._handle_joystick(command, key, player)
        else:
            self._handle_button(command, key, player)

    def _handle_joystick(self, command: str, key: str, player: int) -> None:
        """Handle joystick movement commands."""
        x, y = map(int, key.split('|'))
        # Map the input values (0-65535) to the correct range (-32768 to 32767)
        x = max(-32768, min(32767, x - 32768))
        y = max(-32768, min(32767, y - 32768))
        
        stick = 'left' if command == 'vjl' else 'right'
        getattr(self.gamepads[player], f'{stick}_joystick')(x_value=x, y_value=y)
        self.gamepads[player].update()

    def _handle_button(self, command: str, key: str, player: int) -> None:
        """Handle gamepad button commands."""
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

        if command == 'p':
            press_button(True)
        elif command == 'r':
            press_button(False)
        elif command == 't':
            press_button(True)
            self.gamepads[player].update()
            sleep(0.05)
            press_button(False)

        self.gamepads[player].update()

    def _handle_keyboard_command(self, command: str, key: Key | KeyCode | str) -> None:
        """Handle keyboard-specific commands."""
        if command == 'p':
            self.keyboard.press(key)
        elif command == 'r':
            self.keyboard.release(key)
        elif command == 't':
            self.keyboard.press(key)
            sleep(0.05)
            self.keyboard.release(key)

class GamepadWebSocketHandler(WebSocket):
    clients: List[WebSocket] = []
    gamepad_manager: Optional[GamepadManager] = None

    def handleMessage(self) -> None:
        try:
            msg_parts = self.data.lower().split(' ')
            command = msg_parts[0]

            if command == 'ping':
                self.sendMessage(f'pong {msg_parts[1]}')
                return

            keys = msg_parts[1].split(',')
            player = int(msg_parts[2]) if len(msg_parts) >= 3 else 0

            for key in keys:
                use_gamepad = command.startswith('v') or key.startswith('xusb_gamepad')
                key_obj = key if use_gamepad else self.gamepad_manager.get_key(key)
                self.gamepad_manager.execute_command(self, command, key_obj, player, use_gamepad)

        except Exception as e:
            if self.gamepad_manager.config.debug:
                print(f'WebSocket message error: {e}')
            self.sendMessage(f'ERROR: {str(e)}')

    def handleConnected(self) -> None:
        GamepadWebSocketHandler.clients.append(self)
        if self.gamepad_manager.config.debug:
            print(f'Client connected: {self.address}')

    def handleClose(self) -> None:
        GamepadWebSocketHandler.clients.remove(self)
        if self.gamepad_manager.config.debug:
            print(f'Client disconnected: {self.address}')

class NoCacheHTTPHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format: str, *args) -> None:
        pass

class GamepadServer:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.gamepad_manager = GamepadManager(config)
        GamepadWebSocketHandler.gamepad_manager = self.gamepad_manager
        
        # Set working directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    def start(self) -> None:
        """Start both HTTP and WebSocket servers in separate threads."""
        http_thread = threading.Thread(target=self._run_http_server)
        ws_thread = threading.Thread(target=self._run_websocket_server)

        http_thread.daemon = True
        ws_thread.daemon = True

        http_thread.start()
        ws_thread.start()

        if self.config.debug:
            print(f'Server started - HTTP: {self.config.http_port}, WebSocket: {self.config.ws_port}')

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down servers...")

    def _run_http_server(self) -> None:
        """Run the HTTP server."""
        server = ThreadingHTTPServer(('', self.config.http_port), NoCacheHTTPHandler)
        if self.config.debug:
            print(f'HTTP server starting on port {self.config.http_port}')
        server.serve_forever()

    def _run_websocket_server(self) -> None:
        """Run the WebSocket server."""
        server = SimpleWebSocketServer('0.0.0.0', self.config.ws_port, GamepadWebSocketHandler)
        if self.config.debug:
            print(f'WebSocket server starting on port {self.config.ws_port}')
        server.serveforever()

if __name__ == "__main__":
    config = ServerConfig()
    server = GamepadServer(config)
    server.start()