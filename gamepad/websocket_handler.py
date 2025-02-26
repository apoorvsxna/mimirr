from SimpleWebSocketServer import WebSocket
from typing import List, Optional
from .gamepad_manager import GamepadManager

class GamepadWebSocketHandler(WebSocket):
    clients: List[WebSocket] = []
    gamepad_manager: Optional[GamepadManager] = None

    def handleMessage(self) -> None:
        """Handle incoming WebSocket messages."""
        try:
            msg_parts = self.data.lower().split(' ')
            command = msg_parts[0]

            # Handle ping messages
            if command == 'ping':
                self.sendMessage(f'pong {msg_parts[1]}')
                return

            # Handle gamepad/keyboard commands
            keys = msg_parts[1].split(',')
            player = int(msg_parts[2]) if len(msg_parts) >= 3 else 0

            for key in keys:
                # Determine if this is a gamepad or keyboard command
                use_gamepad = command.startswith('v') or key.startswith('xusb_gamepad')
                key_obj = key if use_gamepad else self.gamepad_manager.get_key(key)
                self.gamepad_manager.execute_command(self, command, key_obj, player, use_gamepad)

        except Exception as e:
            if self.gamepad_manager.config.debug:
                print(f'WebSocket message error: {e}')
            self.sendMessage(f'ERROR: {str(e)}')

    def handleConnected(self) -> None:
        """Handle new WebSocket connections."""
        GamepadWebSocketHandler.clients.append(self)
        if self.gamepad_manager.config.debug:
            print(f'Client connected: {self.address}')
        self.sendMessage('INFO: Connected to gamepad server')

    def handleClose(self) -> None:
        """Handle WebSocket disconnections."""
        GamepadWebSocketHandler.clients.remove(self)
        if self.gamepad_manager.config.debug:
            print(f'Client disconnected: {self.address}')