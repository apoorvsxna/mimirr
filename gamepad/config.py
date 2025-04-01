from dataclasses import dataclass

@dataclass
class ServerConfig:
    http_port: int = 8080
    ws_port: int = 8000
    debug: bool = True
    max_gamepads: int = 4
    host: str = '0.0.0.0'
    # Time in milliseconds for button press simulation
    button_press_time: float = 0.05
    # Maximum reconnection attempts for WebSocket
    max_reconnect_attempts: int = 5
    # Base delay between reconnection attempts (will be multiplied by 2^attempt)
    reconnect_delay: int = 1000
    # Interval for WebSocket ping messages (ms)
    ping_interval: int = 5000