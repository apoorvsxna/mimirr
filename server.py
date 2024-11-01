#!/usr/bin/env python
# -*- coding: utf-8 -*-

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from pynput.keyboard import Key, KeyCode, Controller
from time import sleep
import os
import threading

# Constants for server ports
HTTP_PORT = 8080  # Change as needed
WS_PORT = 8000    # Change as needed
DEBUG = True      # Set to True for debug messages

# Import vgamepad if installed
vgamepadInstalled = True
vgamepadError = False
class VgamepadDisabled(Exception): pass

# Removed options management
# No longer checking for 'disableVgamepad'
try:
    from vgamepad import VX360Gamepad, XUSB_BUTTON
    gamepads = [VX360Gamepad() for _ in range(4)]
except ModuleNotFoundError:
    gamepads = None
    vgamepadInstalled = False
except VgamepadDisabled:
    gamepads = None
except Exception as err:
    gamepads = None
    vgamepadError = True
    if DEBUG: print(f"Error: {err}")

keyboard = Controller()

# Set the current directory
os.chdir(os.path.join(os.path.dirname(__file__), ''))

# Get keyboard key by name
def getKey(keyName):
    if len(keyName) > 1:
        if keyName.isdigit(): return KeyCode(int(keyName))
        else: return Key[keyName]
    return keyName

# Press or release keyboard keys or gamepad buttons
def keyCommand(wsClient, cmd, key, player, vpad=False):
    if DEBUG: print(f'[PLAYER {player + 1} COMMAND] {key}')
    try:
        # Gamepad commands
        if vpad:
            if not gamepads:
                wsClient.sendMessage('INFO Virtual control is not installed')
                return

            # Press a button on the gamepad
            def button(action, key):
                t = 255 if action == 'press' else 0
                if key == 'xusb_gamepad_left_trigger': 
                    gamepads[player].left_trigger(value=t)
                elif key == 'xusb_gamepad_right_trigger': 
                    gamepads[player].right_trigger(value=t)
                else: 
                    getattr(gamepads[player], f'{action}_button')(button=XUSB_BUTTON[key.upper()])
                if DEBUG: print(f'Gamepad {action} on {key}')

            # Control a gamepad joystick
            def joystick(side, key):
                x, y = list(map(int, key.split('|')))
                getattr(gamepads[player], f'{side}_joystick')(x_value=x, y_value=y)
                if DEBUG: print(f'Moved {side} joystick to x:{x}, y:{y}')

            if cmd == 'vjl': joystick('left', key)
            elif cmd == 'vjr': joystick('right', key)
            elif cmd == 'r': button('release', key)
            elif cmd == 'p': button('press', key)
            elif cmd == 't':
                button('press', key)
                gamepads[player].update()
                sleep(0.05)
                button('release', key)
            gamepads[player].update()

        # Keyboard commands
        elif cmd == 'r': 
            keyboard.release(key)
            if DEBUG: print(f'Released keyboard key: {key}')
        elif cmd == 'p': 
            keyboard.press(key)
            if DEBUG: print(f'Pressed keyboard key: {key}')
        elif cmd == 't':
            keyboard.press(key)
            sleep(0.05)
            keyboard.release(key)
            if DEBUG: print(f'Tapped keyboard key: {key}')

    except Exception as err:
        if DEBUG: print(f'Error: {err}')


# Handle WebSocket messages
def message(msg, client):
    msg = msg.lower().split(' ')
    cmd = msg[0]
    
    if DEBUG: print(f'[MESSAGE RECEIVED] Command: {cmd}, Message: {msg}')

    if cmd == 'ping':
        pingID = msg[1]
        client.sendMessage(f'pong {pingID}')
        return

    keys = msg[1].split(',')
    player = int(msg[2]) if len(msg) >= 3 else 0
    for key in keys:
        if cmd.startswith('v') or key.startswith('xusb_gamepad'):
            keyCommand(client, cmd, key, player, True)
        else:
            keyCommand(client, cmd, getKey(key), player)


# HTTP Server
class NoCacheRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.myHeaders()
        SimpleHTTPRequestHandler.end_headers(self)

    def myHeaders(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')

    def log_message(self, format, *args):
        return

class CustomThreadingHTTPServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        return

# Start HTTP server
def httpServer():
    httpd = CustomThreadingHTTPServer(('', HTTP_PORT), NoCacheRequestHandler)
    if DEBUG: print(f'HTTP server starting on port {HTTP_PORT}')
    httpd.serve_forever()

# WebSocket Server
wsClients = []
class WebSocketServer(WebSocket):
    def handleMessage(self):
        try: 
            message(self.data, self)
        except Exception as err:
            if DEBUG: print(f'WebSocket error: {err}')

    def handleConnected(self):
        wsClients.append(self)
        if DEBUG: print(f'User connected ({self.address})')

    def handleClose(self):
        wsClients.remove(self)
        if DEBUG: print(f'User disconnected ({self.address})')

# Send a message to all WebSocket clients
def sendWebSocketMsg(msg):
    for client in wsClients:
        client.sendMessage(msg)

# Start WebSocket server
def wsServer():
    wss = SimpleWebSocketServer('0.0.0.0', WS_PORT, WebSocketServer)
    if DEBUG: print(f'WebSocket server starting on port {WS_PORT}')
    wss.serveforever()

# Entry point for the script
if __name__ == "__main__":
    # Start threads for HTTP and WebSocket servers
    httpThread = threading.Thread(target=httpServer)
    httpThread.daemon = True
    httpThread.start()
    wsThread = threading.Thread(target=wsServer)
    wsThread.daemon = True
    wsThread.start()

    if DEBUG: print(f'Server started on ports HTTP: {HTTP_PORT}, WebSocket: {WS_PORT}')

    # Keep the main thread alive
    while True:
        sleep(1)
