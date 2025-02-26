#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
import socket
import qrcode
from http.server import ThreadingHTTPServer
from SimpleWebSocketServer import SimpleWebSocketServer
from time import sleep
from gamepad.config import ServerConfig
from gamepad.gamepad_manager import GamepadManager
from gamepad.websocket_handler import GamepadWebSocketHandler
from gamepad.http_handler import NoCacheHTTPHandler

class ConfiguredHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass, config):
        super().__init__(server_address, RequestHandlerClass)
        self.config = config

class GamepadServer:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.gamepad_manager = GamepadManager(config)
        GamepadWebSocketHandler.gamepad_manager = self.gamepad_manager

    def get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '127.0.0.1'

    def display_qr_code(self) -> None:
        ip = self.get_local_ip()
        url = f"http://{ip}:{self.config.http_port}"
        
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)

        print("\n" + "="*50)
        print("Mimirr: Remote Control")
        print("="*50)
        qr.print_ascii()
        print(f"\nScan the QR code or visit: {url}")
        print("\nPress Ctrl+C to stop the server")
        print("="*50 + "\n")

    def start(self) -> None:
        try:
            http_thread = threading.Thread(target=self._run_http_server)
            ws_thread = threading.Thread(target=self._run_websocket_server)

            http_thread.daemon = True
            ws_thread.daemon = True

            http_thread.start()
            ws_thread.start()
            
            self.display_qr_code()

            while True:
                sleep(1)

        except KeyboardInterrupt:
            print("\nShutting down servers...")
        except Exception as e:
            print(f"\nError: {str(e)}")
            raise

    def _run_http_server(self) -> None:
        server = ConfiguredHTTPServer(
            ('', self.config.http_port),
            NoCacheHTTPHandler,
            self.config
        )
        server.serve_forever()

    def _run_websocket_server(self) -> None:
        server = SimpleWebSocketServer(
            self.config.host,
            self.config.ws_port,
            GamepadWebSocketHandler
        )
        server.serveforever()

def main():
    config = ServerConfig()
    server = GamepadServer(config)
    server.start()

if __name__ == "__main__":
    main()