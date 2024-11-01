import websocket
import json
import time

WS_SERVER_URL = "ws://localhost:8000"  # WS_PORT

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    print("Connected to server")

    # Example commands to send
    commands = [
        "ping 1234",                # Simple ping command
        "p xusb_gamepad_a 0",      # Press button A on player 1's gamepad
        "r xusb_gamepad_a 0",      # Release button A on player 1's gamepad
        "vjl 128|255 0"             # Move left joystick for player 1
    ]
    
    for cmd in commands:
        ws.send(cmd)
        time.sleep(1)  # Wait for a second between commands to observe responses

if __name__ == "__main__":
    # Create a WebSocket app and run it
    ws = websocket.WebSocketApp(WS_SERVER_URL,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()