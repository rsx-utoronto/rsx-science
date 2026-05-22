# Contents of this script listens for ROS messages 
# Upon receiving a ROS message, the Pi Node will extract the information and push it into the CAN bus

import rclpy
from rclpy.node import Node
from science_can import *
from CAN_utilities import initialize_bus
import numpy as np
import time

from science.msg import SCP

# Link from ROS to Pi, where Pi listens for ROS messages
class CAN_send(Node):

    def __init__(self):
        super().__init__('ros_receiver')
        self.create_subscription(
            SCP,
            'scp_send', #TODO confirm the topic name
            self.ros_receiver_callback,
            10)
        
    def ros_receiver_callback(self, msg : SCP):
        
        # Fill up SCP with info from ROS Message 
        sci_pkt = process_ROS_topic(msg)

        # Add the message into the TX Buffer (Pi system will send it into CAN BUS)
        TX_BUFFER.append(sci_pkt)

def main(args=None):

    rclpy.init(args=args)

    # Create instance of ROS listener 
    send_can = CAN_send()

    # Instantiate CAN bus
    BUS = initialize_bus()

    #

    while (True):
        process_tx(BUS)
        time.sleep(1)
        
if __name__ == "__main__": 
    main()