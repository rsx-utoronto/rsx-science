#!/usr/bin/env python3

# MAIN PYTHON FILE FOR RSX SCIENCE 

# Contains all the main science sensors and modules for CAN communication
# 2026/26 edition  

import can
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from science.CAN_utilities import *

# Types of modules
SCI_MODULE_NONE = 0 # No type
SCI_MODULE_RPI = 1 # Raspberry Pi 5 
SCI_MODULE_GENERAL = 2 # Arduino Nano
SCI_MODULE_OPTICS = 3 # Arduino Nano
SCI_MODULE_DRILL = 4 # Arduino Nano
SCI_MODULE_MOTOR = 5 # Arduino Nano

# Types of sensors 
SCI_SENSOR_NONE = 0 
SCI_SENSOR_ALL = 1
SCI_SENSOR_UVLED = 2
SCI_SENSOR_SERVO = 3
SCI_SENSOR_LINEAR_ACTUATOR = 4 
SCI_SENSOR_ULTRASONIC = 5
SCI_SENSOR_ELECTROMAGNET = 6
SCI_SENSOR_SPARK_MOTOR = 7 

# Types of errors 
SCI_ERROR_SUCCESS = 0 # No Error 
SCI_ERROR_GENERIC = 1 # General Error Msg 
SCI_ERROR_PP = 2

# The science CAN tag denoting our specific CAN network 
SCIENCE_CAN_TAG = 314 

class ScienceCanPacket:
    priority: int = 0
    science: int = 0
    sender: int = 0
    receiver: int = 0
    sensor: int = 0
    extra: int = 0
    dlc: int = 0 
    data = [None, None, None, None, None, None, None, None]

    # Prints the raw values of everything in the Science Can Packet (SCP) 
    def print_pkt(self, immediate=True):
        print("============================")
        print("RSX Science CAN Packet Data!")
        print("----------------------------")
        print (f"Priority: {self.priority}")
        print (f"RSX_Science_Tag: {self.science}")
        print (f"Sender_Module: {self.sender}")
        print (f"Receiver_Module: {self.receiver}")
        print (f"Sensor: {self.sensor}")
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
    
    # Returns sensor of the SCP 
    def fetch_sensor(self):
        return self.sensor

def assemble_SCP_from_frame(can_frame: can.Message, rsx_sci_pkt: ScienceCanPacket):
    # Fill the RSX_Sci packet with information from the CAN frame address
    can_id  = can_frame.arbitration_id
    rsx_sci_pkt.extra  = can_id & 0xFFF
    can_id = can_id >> 12
    rsx_sci_pkt.sensor     = can_id & 0xF
    can_id = can_id >> 4
    rsx_sci_pkt.receiver     = can_id & 0xF
    can_id = can_id >> 4
    rsx_sci_pkt.sender     = can_id & 0xF
    can_id = can_id >> 4
    rsx_sci_pkt.science     = can_id & 0xF
    can_id = can_id >> 4
    rsx_sci_pkt.priority     = can_id & 0x1

    # Assign the length 
    rsx_sci_pkt.dlc = can_frame.dlc

    # Fill the RSX_Sci packet with data received 
    for i in range (can_frame.dlc):
        rsx_sci_pkt.data[i] = can_frame.data[i]
    
    return can_frame

def assemble_frame_from_SCP(rsx_sci_pkt: ScienceCanPacket):

    can_frame = can.Message()
    # Initialize can_id for new frame to send
    can_id = 0

    print(rsx_sci_pkt.priority)

    # Populate can_id with info from RSX_Sci packet
    can_id |= rsx_sci_pkt.priority & 0x1
    can_id = can_id >> 4
    can_id |= rsx_sci_pkt.science & 0xF
    can_id = can_id >> 4
    can_id |= rsx_sci_pkt.sender & 0xF
    can_id = can_id >> 4
    can_id |= rsx_sci_pkt.receiver & 0xF
    can_id = can_id >> 4
    can_id |= rsx_sci_pkt.sensor & 0xF
    can_id = can_id >> 12
    can_id |= rsx_sci_pkt.extra & 0xFFF

    can_frame.arbitration_id = can_id

    can_frame.dlc = rsx_sci_pkt.dlc 

    can_frame.is_extended_id = True

    return can_frame

# Reads from ROS topic data, fills and returns an SCP with information to be sent 
def process_ROS_topic(ros_topic):
    
    # Initialize an instance of an empty SCP 
    rsx_scp = ScienceCanPacket()

    '''
    Current expected layout of ros_msg (subject to change): 
    priority: 0
    receiver: final receiving module in CAN
    sensor: final associated sensor message is being sent to
    extra: any extra info sent from ground station
    data_legth: length of data, equivalent to dlc in CAN
    data_content: actual contents of message being sent, equivalent to CAN data
    '''

    # Fill with info from ros_topic
    rsx_scp.priority = ros_topic.priority
    rsx_scp.science = SCIENCE_CAN_TAG
    rsx_scp.sender = SCI_MODULE_RPI  # Sender will always be RPi, it sends every ros_msg to CAN network 
    rsx_scp.receiver = ros_topic.receiver 
    rsx_scp.sensor = ros_topic.sensor
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
    rsx_scp.science = SCIENCE_CAN_TAG
    rsx_scp.sender = SCI_MODULE_RPI  # Sender will always be RPi, it sends every ros_msg to CAN network 
    rsx_scp.receiver = SCI_MODULE_DRILL
    rsx_scp.sensor = SCI_SENSOR_SERVO
    rsx_scp.extra = 0b000100010001
    rsx_scp.dlc = len(ros_str)
    rsx_scp.data = ros_str

    return rsx_scp
    
    
def process_can_rx():
    return "bruh"
