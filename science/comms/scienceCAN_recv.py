#!/usr/bin/env python3

# In this code, we would like to receive SCI Packet
# Using Publisher Node
# Infinitely Read can_msg = BUS.recv()
# Publish pulse_pkg = assemble_SCP_from_frame(can_frame=can_msg)

#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from science_can import *
from CAN_utilities import *

from science.msg import SCP


class CAN_recv(Node):

    def __init__(self):
        super().__init__('scienceCAN_recv')

        self.publisher = self.create_publisher(
            SCP,
            'scp_recv',
            10
        )

        # Instantiate CAN bus
        self.BUS = initialize_bus(channel='can1')

        # Call process_tx periodically without blocking ROS callbacks
        self.tx_timer = self.create_timer(0.01, self.can_receiver_callback)
        self.get_logger().info("Science CAN Receive Node Initialized and Listening.")

    def can_recv_loop(self):

        while rclpy.ok():
            msg_received = ScienceCanPacket()
            try: 
                process_rx(self.BUS)
                if RX_BUFFER == []:
                    continue
                else:
                    # print(RX_BUFFER)
                    for msg in RX_BUFFER:
                        msg_received = msg
                        if type(msg_received) == list:
                            msg_received[0].print_pkg()
                            print(combine_multipacket_data(msg_received))
                        else:
                            print(f"Length of RX_BUFFER: {len(RX_BUFFER)}")
                            msg_received.print_processed_pkt()

                    RX_BUFFER.clear()

            except Exception as e:
                self.get_logger().error(f"Failed to assemble or read CAN bus: {e}")   

def main(args=None):
    # print("Starting CAN Receive Node", flush=True)

    rclpy.init(args=args)

    recv_can = CAN_recv()

    rclpy.spin(recv_can)

    recv_can.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()