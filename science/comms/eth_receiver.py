#!/usr/bin/env python3
"""
Receiver — runs on the laptop (192.168.0.123).
Listens for data sent by the Raspberry Pi over TCP.

Usage:
    python3 receiver.py [--port 5005]
"""

import argparse
import socket
import time


HOST = "192.168.0.123"
ALLOWED_CLIENT = "192.168.0.34"
DEFAULT_PORT = 5005


def main():
    parser = argparse.ArgumentParser(description="Receive data from Raspberry Pi over ethernet.")
    parser.add_argument("--host", default=HOST, help="Local IP to bind (default: 192.168.0.123)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((args.host, args.port))
        srv.listen(1)
        print(f"Listening on {args.host}:{args.port} — waiting for Pi to connect...")

        while True:
            conn, addr = srv.accept()
            if addr[0] != ALLOWED_CLIENT:
                print(f"Rejected connection from {addr[0]}")
                conn.close()
                continue
            print(f"Connected: {addr[0]}:{addr[1]}\n")
            with conn:
                buffer = ""
                try:
                    while True:
                        chunk = conn.recv(1024).decode("utf-8", errors="replace")
                        if not chunk:
                            break
                        buffer += chunk
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            timestamp = time.strftime("%H:%M:%S")
                            print(f"[{timestamp}] {line}")
                except (ConnectionResetError, BrokenPipeError):
                    pass
            print(f"\nDisconnected: {addr[0]} — waiting for next connection...")


if __name__ == "__main__":
    main()
