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

from science.msg import SCP
from sensor_msgs.msg import Joy
from std_msgs.msg import String

class Controller(Node):

    def __init__(self):
        super().__init__('science_controller')
        self.create_subscription(
            Joy,
            'joy', #TODO confirm the topic name
            self.controller_callback,
            10
        )

        self.create_subscription(
            String,
            'arm_state',
            self.arm_callback, 
            10
        )

        self.publisher = self.create_publisher(
            SCP,
            "scp_send", 
            10
        )

        # self.test = True
        # timer_period = 0.5
        # self.timer = self.create_timer(timer_period, self.timer_callback, autostart= True)

        # # Instantiate CAN bus
        # self.BUS = sc.initialize_bus()

        # 
        # self.index = 0
        self.start = True
        self.state = None
        self.drill_speed = 0
        self.scp = SCP()
        # prev_joy_input = Joy()
        self.prev_buttons = None
        # print(self.prev_buttons)
        # for i in range(8):
        #     print(i)
        #     self.prev_buttons[i] = 0

    def arm_callback(self, msg : String):
        self.state = msg.data
    
    def controller_callback(self, msg : Joy):

        # self.get_logger().info('I heard you >:)')

        if self.state != "science":
            self.get_logger().debug('Not in Science state')
            # self.get_logger().debug("Not in Science state")
            return

        if self.start:
            self.prev_buttons = msg.buttons[:8]
            self.start = False
            return

        if self.prev_buttons == msg.buttons[:8]:
                # print(self.prev_buttons)
                # self.prev_buttons = msg.buttons[:8]
                # self.get_logger().debug('No science buttons were pressed')
                return

        button_x        = msg.buttons[0]
        button_o        = msg.buttons[1]
        prev_x          = self.prev_buttons[0]
        prev_o          = self.prev_buttons[1]

        button_triangle = msg.buttons[2]
        button_square   = msg.buttons[3]
        prev_triangle   = self.prev_buttons[2]
        prev_square     = self.prev_buttons[3]

        button_L2       = msg.buttons[6]
        button_R2       = msg.buttons[7]
        prev_L2         = self.prev_buttons[6]
        prev_R2         = self.prev_buttons[7]

        # axis_L2       = msg.axes[2]
        # axis_R2       = msg.axes[5]

        button_L1       = msg.buttons[4]
        button_R1       = msg.buttons[5]
        prev_L1         = self.prev_buttons[4]
        prev_R1         = self.prev_buttons[5]

        # sci_pkt                 = sc.ScienceCanPacket()
        self.scp.sender         = sc.SCI_MODULE_RPI
        self.scp.receiver       = sc.SCI_MODULE_DRILL
        self.scp.priority       = 0
        self.scp.multipacket_id = 0
        self.scp.extra          = sc.SCI_ERROR_SUCCESS
        self.scp.dlc            = 8

        data = None
        if button_o or button_x:
            data = int(max(button_x - button_o, 0))
            self.scp.peripheral = sc.SCI_PERIPHERAL_ELECTROMAGNET 
            # task = self.BUS.send(pulse)

        # elif button_x:
        #     sci_pkt.peripheral  = sc.SCI_PERIPHERAL_ELECTROMAGNET 
        #     sci_pkt.data = bytes([0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]) # First byte set to 1 for on
        #     pulse = sc.assemble_frame_from_SCP(rsx_sci_pkt= sci_pkt)
        #     # task = self.BUS.send(pulse)

        if button_triangle or button_square:
            data = int(max(button_square - button_triangle, 0))
            self.scp.peripheral = sc.SCI_PERIPHERAL_SERVO 

        # elif button_square:
        #     sci_pkt.peripheral  = sc.SCI_PERIPHERAL_SERVO 
        #     sci_pkt.data = bytes([0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]) # First byte set to 1 for servo forward (open)
        #     pulse = sc.assemble_frame_from_SCP(rsx_sci_pkt= sci_pkt)
        #     # task = self.BUS.send(pulse)

        if button_L1 or button_R1:
            data = int(button_R1 - button_L1)
            self.drill_speed += data

            if abs(self.drill_speed) >  3:
                self.get_logger().warn("Max Drill Speed")
                self.drill_speed -= data
                data = None
                return
            
            self.scp.peripheral = sc.SCI_PERIPHERAL_SPARK_MOTOR

        # elif button_R1:
        #     sci_pkt.peripheral  = sc.SCI_PERIPHERAL_SERVO 
        #     sci_pkt.data = bytes([0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]) # First byte set to 1 for servo forward (open)
        #     pulse = sc.assemble_frame_from_SCP(rsx_sci_pkt= sci_pkt)
        #     # task = self.BUS.send(pulse)

        if button_L2 != prev_L2 or button_R2 != prev_R2:
            if button_R2 - button_L2 != 0:
                data = 1 * (button_R2 - button_L2)
            else:
                data = 0
            self.scp.peripheral = sc.SCI_PERIPHERAL_LINEAR_ACTUATOR

        # elif button_R2:
        #     sci_pkt.peripheral  = sc.SCI_PERIPHERAL_SERVO 
        #     sci_pkt.data = bytes([0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]) # First byte set to 1 for servo forward (open)
        #     pulse = sc.assemble_frame_from_SCP(rsx_sci_pkt= sci_pkt)
        #     # task = self.BUS.send(pulse)

        # print(data)
        self.prev_buttons = msg.buttons[:8]

        if data not in range(-3, 4):
            self.get_logger().debug("Invalid data for controller")
            return
        
        self.scp.data = [(data & 0xFF), 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF] # First byte set to 0 for off
        self.publisher.publish(self.scp)
        # pulse = sc.assemble_frame_from_SCP(rsx_sci_pkt= sci_pkt)
        # task = self.BUS.send(pulse)

def main(args=None):
    rclpy.init(args=args)

    Controller_Node = Controller()

    rclpy.spin(Controller_Node)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    Controller_Node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

