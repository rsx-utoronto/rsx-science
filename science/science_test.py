#!/usr/bin/env python3

# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node
import science_can as sc
import numpy as np

from science.msg import Science


class GUITest(Node):

    def __init__(self):
        super().__init__('science_gui')
        self.subscription = self.create_subscription(
            Science,
            'science_state',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        self.publisher = self.create_publisher(
            Science,
            "science_state", 
            10
        )
        self.test = True
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback, autostart= True)

    def listener_callback(self, msg : Science):

        self.get_logger().info('I heard you >:)')
        # can_message = sc.ROS_STR_to_CAN_sanity(msg.data)
        # can_message.print_pkt()
        
        # Check which module is the message for
        if "rsx" == msg.receiver:
            return

        # self.get_logger().info('I heard you >:)')

        sci_pkt = sc.ScienceCanPacket()

        # Sender in this case will always be the RPi5
        sci_pkt.sender = sc.SCI_MODULE_RPI

        # Handling optical module specific commands 
        if "optical" == msg.receiver:
            sci_pkt.receiver = sc.SCI_MODULE_OPTICS

            if "uv_led" == msg.peripheral:
                sci_pkt.peripheral = sc.SCI_PERIPHERAL_UVLED
            
            elif "blue_led" == msg.peripheral:
                sci_pkt.peripheral = sc.SCI_PERIPHERAL_UVLED #TODO
            
            if "on" == msg.command:
                sci_pkt.data = None #TODO
            
            elif "off" == msg.command:
                sci_pkt.data = None #TODO

            if "spectrometer" == msg.peripheral:
                sci_pkt.receiver = "spectrometer" #TODO

                if "start" == msg.command:
                    # self.test = True
                    # self.timer.reset()
                    sci_pkt.data = None #TODO
                
                elif "stop" == msg.command:
                    # self.test = False
                    # self.timer.destroy()
                    sci_pkt.data = None #TODO

        # Handling drill module specific commands
        elif "drill" == msg.receiver:
            sci_pkt.receiver = sc.SCI_MODULE_DRILL

            # Maybe not needed???
            if "ultrasonic" == msg.peripheral:
                sci_pkt.peripheral = sc.SCI_PERIPHERAL_ULTRASONIC

                #TODO
            
            if "electromagnet" == msg.peripheral:
                sci_pkt.peripheral = sc.SCI_PERIPHERAL_ELECTROMAGNET

                if "on" == msg.command:
                    sci_pkt.data = None #TODO
                
                elif "off" == msg.command:
                    sci_pkt.data = None #TODO


        # Handling multispectral module specific commands
        elif "multispectral" == msg.receiver:
            sci_pkt.receiver = sc.SCI_MODULE_MULTISPECTRAL

            if "collect_13" == msg.command:
                sci_pkt.data = None #TODO
            
            elif "collect_single" == msg.command:
                sci_pkt.data = None #TODO


        # Handling sorter module specific commands
        elif "sorter" == msg.receiver:
            sci_pkt.receiver = sc.SCI_MODULE_SORTER

        else:
            self.get_logger().info('ERROR: Invalid receiver')
            return
        
        # Handling the servo peripheral commands (common to all modules) 
        if "servo" == msg.peripheral:
            sci_pkt.peripheral = sc.SCI_PERIPHERAL_SERVO

            # Prepare CAN data packet for "servo" peripheral
            if "forward" == msg.command:
                sci_pkt.priority = 0 # 0 For high priority, 1 for low. Can be default and placed outside of if statements. 
                sci_pkt.multipacket_id = 0 # 0 for single packet commands. Should only be another number for spectrometer data. Can also be default
                sci_pkt.extra = 0 # No extra data to be sent with servo
                sci_pkt.dlc = 8 # Full length of data 
                sci_pkt.data = bytes([0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]) # First byte set to 1 for forward, -1 for backward. 
            
            elif "backward" == msg.command:
                sci_pkt.data = None #TODO
            
            else:
                self.get_logger().info('ERROR: Invalid command')
                return

        print(msg.receiver)
        print(msg.peripheral)
        print(msg.command)
        print(msg.data)
        print(msg.response)

    def timer_callback(self):
        msg = Science()
        msg.receiver = "rsx"
        msg.command = "temphum_data"
        # msg.command = None
        test_array = np.random.rand(2)
        msg.data = test_array
        msg.response = "site_2"
        
        if self.test:
            self.publisher.publish(msg)

        # print("Printing on topic")
    

def main(args=None):
    rclpy.init(args=args)

    gui_test = GUITest()

    rclpy.spin(gui_test)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    gui_test.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
