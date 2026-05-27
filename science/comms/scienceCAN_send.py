#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from science_can import *
from CAN_utilities import *

from science.msg import SCP


class CAN_send(Node):

    def __init__(self):
        super().__init__('scienceCAN_send')

        self.subscription = self.create_subscription(
            SCP,
            'scp_send',
            self.ros_receiver_callback,
            10
        )

        # Instantiate CAN bus
        self.BUS = initialize_bus(channel='can1')

        # Call process_tx periodically without blocking ROS callbacks
        self.tx_timer = self.create_timer(0.01, self.process_tx_callback)

    def ros_receiver_callback(self, msg: SCP):
        print("in ros receiver can callback", flush=True)

        sci_pkt = ScienceCanPacket()

        sci_pkt.priority       = msg.priority
        sci_pkt.receiver       = msg.receiver
        sci_pkt.multipacket_id = msg.multipacket_id
        sci_pkt.peripheral     = msg.peripheral   # FIXED: you had msg.multipacket_id here
        sci_pkt.extra          = msg.extra
        sci_pkt.data           = msg.data
        sci_pkt.dlc            = msg.dlc

        # If your ScienceCanPacket has sender, include this too:
        # sci_pkt.sender = msg.sender

        TX_BUFFER.append(sci_pkt)
        sci_pkt.print_pkt()

    def process_tx_callback(self):
        process_tx(self.BUS)


def main(args=None):
    print("Starting CAN Send Node", flush=True)

    rclpy.init(args=args)

    send_can = CAN_send()

    rclpy.spin(send_can)

    send_can.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()