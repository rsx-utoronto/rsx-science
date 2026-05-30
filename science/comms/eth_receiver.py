#!/usr/bin/env python3
"""
Receiver — runs on the laptop (192.168.0.123).
Listens for BLE sensor data forwarded by the Pi over TCP and publishes to ROS.
"""

import argparse
import socket
import threading

import rclpy
from rclpy.node import Node
from science.msg import Science


HOST = "192.168.0.123"
ALLOWED_CLIENT = "192.168.0.34"
DEFAULT_PORT = 5005


class EthReceiver(Node):

    def __init__(self, host: str, port: int):
        super().__init__("eth_receiver")
        self.publisher = self.create_publisher(Science, "science_output", 10)

        thread = threading.Thread(target=self._serve, args=(host, port), daemon=True)
        thread.start()

    def _serve(self, host: str, port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((host, port))
            srv.listen(1)
            self.get_logger().info(f"Listening on {host}:{port} — waiting for Pi...")

            while True:
                conn, addr = srv.accept()
                if addr[0] != ALLOWED_CLIENT:
                    self.get_logger().warn(f"Rejected connection from {addr[0]}")
                    conn.close()
                    continue
                self.get_logger().info(f"Connected: {addr[0]}:{addr[1]}")
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
                                self._handle(line.strip())
                    except (ConnectionResetError, BrokenPipeError):
                        pass
                self.get_logger().info(f"Disconnected: {addr[0]} — waiting for next connection...")

    def _handle(self, line: str):
        # Expected format: device_name,temperature,humidity
        parts = line.split(",")
        if len(parts) != 3:
            self.get_logger().warn(f"Unexpected message format: {line!r}")
            return
        try:
            device_name = parts[0]
            temperature = float(parts[1])
            humidity = float(parts[2])
        except ValueError:
            self.get_logger().warn(f"Failed to parse values in: {line!r}")
            return

        msg = Science()
        msg.receiver = "rsx"
        msg.peripheral = device_name
        msg.data.append(temperature)
        msg.data.append(humidity)
        self.publisher.publish(msg)
        self.get_logger().info(f"Published: {device_name} temp={temperature} hum={humidity}")


def main():
    parser = argparse.ArgumentParser(description="Receive BLE sensor data from Pi and publish to ROS.")
    parser.add_argument("--host", default=HOST, help="Local IP to bind (default: 192.168.0.123)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    rclpy.init()
    node = EthReceiver(args.host, args.port)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
