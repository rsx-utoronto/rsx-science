# Contents of this script listens for ROS messages 
# Upon receiving a ROS message, the Pi Node will extract the information and push it into the CAN bus

import rclpy
from rclpy.node import Node

from science_can import *
from CAN_utilities import *

from science.msg import SCP

# Link from ROS to Pi, where Pi listens for ROS messages
class CAN_send(Node):

    def __init__(self):
        super().__init__('scienceCAN_send')
        self.create_subscription(
            SCP,
            'scp_send', #TODO confirm the topic name
            self.ros_receiver_callback,
            10)
        
        self.sci_pkt = ScienceCanPacket()

        # Instantiate CAN bus
        self.BUS = initialize_bus()

        
    def ros_receiver_callback(self, msg : SCP):
        
        # Fill up SCP with info from ROS Message 
        self.sci_pkt.priority       = msg.priority
        self.sci_pkt.receiver       = msg.receiver
        self.sci_pkt.multipacket_id = msg.multipacket_id
        self.sci_pkt.peripheral     = msg.multipacket_id
        self.sci_pkt.extra          = msg.extra
        self.sci_pkt.data           = msg.data
        self.sci_pkt.dlc            = msg.dlc

        # Add the message into the TX Buffer (Pi system will send it into CAN BUS)
        TX_BUFFER.append(self.sci_pkt)

def main(args=None):

    rclpy.init(args=args)

    # Create instance of ROS listener 
    send_can = CAN_send()

    # Send CAN messages
    while rclpy.ok():
        process_tx(send_can.BUS)

    # Keep the node running
    # rclpy.spin(send_can)

    # while (True):
    #     process_tx(BUS)
    #     time.sleep(1)
        
if __name__ == "__main__": 
    main()