# MAIN PYTHON FILE FOR RSX SCIENCE

# Contains all the main science peripherals and modules for CAN communication
# 2026/26 edition

# MAIN PYTHON FILE FOR RSX SCIENCE

# Contains all the main science peripherals and modules for CAN communication
# 2026/26 edition

import can
# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import String

from comms.CAN_utilities import *

# Types of modules
SCI_MODULE_NONE             = 0 # No type
SCI_MODULE_RPI              = 1 # Raspberry Pi 5
SCI_MODULE_GENERAL          = 2 # Arduino Nano
SCI_MODULE_OPTICS           = 3 # Arduino Nano
SCI_MODULE_DRILL            = 4 # Arduino Nano
SCI_MODULE_MOTOR            = 5 # Arduino Nano
SCI_MODULE_MULTISPECTRAL    = 6 # Arduino Nano
SCI_MODULE_SORTER           = 7 # Arduino Nano

# Types of Peripherals
SCI_PERIPHERAL_NONE = 0
SCI_PERIPHERAL_ALL = 1
SCI_PERIPHERAL_UVLED = 2
SCI_PERIPHERAL_SERVO = 3
SCI_PERIPHERAL_LINEAR_ACTUATOR = 4
SCI_PERIPHERAL_ULTRASONIC = 5
SCI_PERIPHERAL_ELECTROMAGNET = 6
SCI_PERIPHERAL_SPARK_MOTOR = 7

# Types of errors
SCI_ERROR_SUCCESS = 0 # No Error
SCI_ERROR_GENERIC = 1 # General Error Msg
SCI_ERROR_PP = 2

# Available slots for large multi-packet datasets
AVAILABLE_MULT_PKT_SLOTS = list(range(1, 16))
ACTIVE_MULT_PKT_SLOTS = []

# Spectrometer Packet Size 
SPEC_PACKET_SIZE = 144

class ScienceCanPacket:
    priority: int = 0
    # multipacket_id: Identifies whether CAN msg is part of a larger multi-packet piece of data,
    # or if its a standalone. 0 if normal CAN msg, ID of the big data packet if otherwise
    multipacket_id: int = 0
    sender: int = 0
    receiver: int = 0
    peripheral: int = 0
    extra: int = 0
    dlc: int = 0
    data = [None, None, None, None, None, None, None, None]

    # Prints the raw values of everything in the Science Can Packet (SCP)
    def print_pkt(self, immediate=True):
        print("============================")
        print("RSX Science CAN Packet Data!")
        print("----------------------------")
        print (f"Priority: {self.priority}")
        print (f"Is_Part_of_Multipacket: {bool(self.multipacket_id)}")
        print (f"Sender_Module: {self.sender}")
        print (f"Receiver_Module: {self.receiver}")
        print (f"Peripheral: {self.peripheral}")
        print (f"Extra_Bits: {self.extra}")
        print (f"Data_Lenth: {self.dlc}")
        print("----------------------------")
        print (f"Data_Content: {self.data}")
        print("============================")

    # Returns receiver of the SCP
    def fetch_receiver(self):
        return self.receiver

    # Returns sender of the SCP
    def fetch_sender(self):
        return self.sender

    # Returns peripheral of the SCP
    def fetch_peripheral(self):
        return self.peripheral

    def fetch_multipacket_id(self):
        return self.multipacket_id
    
    def celebrate(self):
        print("YAYYYY! WE DID IT! THIS IS AWESOME!!!")

# Buffer lists for incoming and outgoing CAN messages 
RX_BUFFER = []
TX_BUFFER = []
MULTIPACKET_BUFFER = [] # Appends to RX_BUFFER once ENTIRE large dataset has been received

def assign_available_slot():
    # Find next available multipacket slot
    res = AVAILABLE_MULT_PKT_SLOTS[0]

    # Remove from available list and add to active list
    AVAILABLE_MULT_PKT_SLOTS.remove(res)
    ACTIVE_MULT_PKT_SLOTS.append(res)

    # Return the slot for use
    return res

def free_available_slot(free_slot):

    # Remove from available list and add to active list
    AVAILABLE_MULT_PKT_SLOTS.append(free_slot)
    ACTIVE_MULT_PKT_SLOTS.remove(free_slot)

def multi_packet_manager(scp_msg):
    mid = scp_msg.multipacket_id
    index = scp_msg.extra

    MULTIPACKET_BUFFER[mid][index] = scp_msg

    if len(MULTIPACKET_BUFFER[mid]) == SPEC_PACKET_SIZE:
        RX_BUFFER.append(MULTIPACKET_BUFFER[mid])
        MULTIPACKET_BUFFER.remove(MULTIPACKET_BUFFER[mid])
        free_available_slot(mid)

def assemble_SCP_from_frame(can_frame: can.Message):
    rsx_sci_pkt = ScienceCanPacket()
    # Fill the RSX_Sci packet with information from the CAN frame address
    can_id  = can_frame.arbitration_id
    rsx_sci_pkt.extra  = can_id & 0xFFF
    can_id = can_id >> 12
    rsx_sci_pkt.peripheral     = can_id & 0xF
    can_id = can_id >> 4
    rsx_sci_pkt.receiver     = can_id & 0xF
    can_id = can_id >> 4
    rsx_sci_pkt.sender     = can_id & 0xF
    can_id = can_id >> 4
    rsx_sci_pkt.multipacket_id     = can_id & 0xF
    can_id = can_id >> 4
    rsx_sci_pkt.priority     = can_id & 0x1

    # Assign the length
    rsx_sci_pkt.dlc = can_frame.dlc

    # Fill the RSX_Sci packet with data received
    for i in range (can_frame.dlc):
        rsx_sci_pkt.data[i] = can_frame.data[i]

    return rsx_sci_pkt

def assemble_frame_from_SCP(rsx_sci_pkt: ScienceCanPacket):

    can_frame = can.Message()
    # Initialize can_id for new frame to send
    can_id = 0

    # Populate can_id with info from RSX_Sci packet
    can_id |= rsx_sci_pkt.priority & 0x1
    can_id = can_id << 4
    can_id |= rsx_sci_pkt.multipacket_id & 0xF
    can_id = can_id << 4
    can_id |= rsx_sci_pkt.sender & 0xF
    can_id = can_id << 4
    can_id |= rsx_sci_pkt.receiver & 0xF
    can_id = can_id << 4
    can_id |= rsx_sci_pkt.peripheral & 0xF
    can_id = can_id << 12
    can_id |= rsx_sci_pkt.extra & 0xFFF

    can_frame.arbitration_id = can_id

    can_frame.dlc = rsx_sci_pkt.dlc

    can_frame.is_extended_id = True

    can_frame.data = rsx_sci_pkt.data

    return can_frame

def process_rx(can_bus):
    for i in range (32):
        can_msg = can_bus.recv(0.01)
        if can_msg != None:
            new_scp = assemble_SCP_from_frame(can_msg)
            if new_scp.receiver == SCI_MODULE_RPI:
                if new_scp.multipacket_id == 0:
                    RX_BUFFER.append(new_scp)
                else:
                    multi_packet_manager(new_scp)
        else:
            break   
    return i  

def process_tx(can_bus):
    for msg in TX_BUFFER:
        assemble_frame_from_SCP(msg)
        try:
            can_bus.send(msg=msg, timeout=0.1)
        except TimeoutError:
            print("ERROR: MESSAGE DID NOT SEND PROPERLY")
        TX_BUFFER.remove(msg)

# Reads from ROS topic data, fills and returns an SCP with information to be sent
def process_ROS_topic(ros_topic):

    # Initialize an instance of an empty SCP
    rsx_scp = ScienceCanPacket()

    '''
    Current expected layout of ros_msg (subject to change):
    priority: 0
    receiver: final receiving module in CAN
    peripheral: final associated peripheral message is being sent to
    extra: any extra info sent from ground station
    data_legth: length of data, equivalent to dlc in CAN
    data_content: actual contents of message being sent, equivalent to CAN data
    '''

    # Fill with info from ros_topic
    # rsx_scp.priority = ros_topic.priority

    if ros_topic.peripheral == SCI_PERIPHERAL_SERVO:
        rsx_scp.multipacket_id = assign_available_slot() # Assign next available multipacket ID to request
    else:
        rsx_scp.multipacket_id = 0

    rsx_scp.sender = SCI_MODULE_RPI  # Sender will always be RPi, it sends every ros_msg to CAN network
    rsx_scp.receiver = ros_topic.receiver
    rsx_scp.peripheral = ros_topic.peripheral
    rsx_scp.extra = ros_topic.extra
    rsx_scp.dlc = ros_topic.data_length
    rsx_scp.data = ros_topic.data_content

    return rsx_scp

# Sanity function that returns a sample SCP from a string format ROS topic
def ROS_STR_to_CAN_sanity(ros_str):
    # Initialize an instance of an empty SCP
    rsx_scp = ScienceCanPacket()

    # Fill SCP with sample info from ros_topic
    rsx_scp.priority = 0
    rsx_scp.multipacket_id = 0 # Single packet by default
    rsx_scp.sender = SCI_MODULE_RPI  # Sender will always be RPi, it sends every ros_msg to CAN network
    rsx_scp.receiver = SCI_MODULE_DRILL
    rsx_scp.peripheral = SCI_PERIPHERAL_SERVO
    rsx_scp.extra = 0b000100010001
    rsx_scp.dlc = len(ros_str)
    rsx_scp.data = ros_str

    return rsx_scp