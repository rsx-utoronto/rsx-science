#!/usr/bin/env python3
"""
Sender — runs on the Raspberry Pi (192.168.0.34).
Sends data to the laptop receiver over TCP.

Usage:
    python3 sender.py [--host 192.168.0.123] [--port 5005] [--interval 1.0]
"""

import argparse
import socket
import time


DEFAULT_HOST = "192.168.0.123"
DEFAULT_PORT = 5005


SENSORS = {
    "cpu_temp": lambda: round(float(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000, 2),
    "uptime_s": lambda: round(float(open("/proc/uptime").read().split()[0]), 1),
}


# def read_sensors() -> dict:
#     data = {}
#     for key, fn in SENSORS.items():
#         try:
#             data[key] = fn()
#         except Exception:
#             data[key] = None
#     return data


# def build_message(seq: int) -> str:
#     sensors = read_sensors()
#     parts = [f"seq={seq}"] + [f"{k}={v}" for k, v in sensors.items()]
#     return " | ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Send data to laptop over ethernet.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Receiver IP (default: 192.168.0.123)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between messages.")
    parser.add_argument("--message", default=None, help="Fixed message instead of sensor data.")
    args = parser.parse_args()

    seq = 0
    while True:
        try:
            print(f"Connecting to {args.host}:{args.port}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((args.host, args.port))
                print("Connected.\n")
                while True:
                    line = args.message if args.message else "test"
                    s.sendall((line + "\n").encode("utf-8"))
                    print(f"TX: {line}")
                    seq += 1
                    time.sleep(args.interval)
        except (ConnectionRefusedError, OSError) as e:
            print(f"Connection failed: {e} — retrying in 5s...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nStopped.")
            break


if __name__ == "__main__":
    main()
