#!/usr/bin/env python3

# Code to read BME280 humidity and temperature data for Raspberry Pi
# Ensure bleak library is installed
# Adapted from https://randomnerdtutorials.com/ble-raspberry-pi-and-pi-pico-w/#more-177129

import rclpy
from rclpy.node import Node

from science.msg import Science
import asyncio
from bleak import BleakScanner, BleakClient, uuids, BLEDevice

# NOTE: MUST MATCH WITH THE ONES ON THE ARDUINO CODE!!
SERVICE_UUID = uuids.normalize_uuid_16(0x181A)
TEMPCHAR_UUID = uuids.normalize_uuid_16(0x2A6E)
HUMCHAR_UUID = uuids.normalize_uuid_16(0x2A6F)
PRESCHAR_UUID = uuids.normalize_uuid_16(0x2A6D)
ALTCHAR_UUID = uuids.normalize_uuid_16(0x2AB3)

# NOTE: ALSO MUST MATCH WITH ARDUINO CODE!!
DEVICE_NAME = ["Nano-Environmental-Sensor1", "Nano-Environmental-Sensor2"]

class BLEOut(Node):

    def __init__(self):
        super().__init__("BLEOut")

        self.ble_publisher = self.create_publisher(
            Science,
            "science_output",
            10
        )

        # Variable to hold the temp/hum probes as BLE devices
        self.probes = []


    async def run_ble(self):
        """
        (None) -> (None)

        Starts the connection process to find the temp/hum probes
        """

        # Making sure we find all the devices
        while len(self.probes) < len(DEVICE_NAME):
            self.get_logger().info(f"Searching for probes")

            # Attempt to find the probes
            await self.find_probes()

        self.get_logger().info(f"PROBES FOUND!!")

        # Retrieve data from the found probes
        await self.connect_probes()


    async def find_probes(self):
        """
        (None) -> (None)

        Searches for the probes in the surrounding through the 
        set device names on the arduino. NOTE: The names MUST match
        the names in DEVICE_NAME variable
        """
        self.get_logger().debug(f"Searching for {DEVICE_NAME[0]} and {DEVICE_NAME[1]}")
        
        # Look for devices for 5s
        devices = await BleakScanner.discover(timeout= 5)

        for device in devices:
            # print(
            # f"Name: {device.name}\n",
            # f"Address: {device.address}\n",
            # )
            if device.name in DEVICE_NAME:

                # Check if the device was already found
                if self.probes == [] or device.name != self.probes[0].name:
                    self.probes.append(device)
                    self.get_logger().info(f"Found {device.name}")

                

    async def receive_data(self, client : BleakClient, device : BLEDevice):
        """
        (BleakClient, BLEDevice) -> (None)

        Receive data from the connected BLE device.

        parameters:
            - client (BleakClient): Client made from the found BLE device
            - device (BLEDevice): Found BLE device that we are retrieving data from
        """
        
        # While ROS2 is fine, keep on attempting to receive data
        while rclpy.ok():
            try:
                temperature = await client.read_gatt_char(TEMPCHAR_UUID)
                temperature = temperature.decode('utf-8').replace("C", "")
                humidity = await client.read_gatt_char(HUMCHAR_UUID)
                humidity = humidity.decode('utf-8').replace("%", "")
                # pressure = await client.read_gatt_char(PRESCHAR_UUID)
                # altitude = await client.read_gatt_char(ALTCHAR_UUID)

                msg = Science()
                msg.receiver = "rsx"
                msg.peripheral = device.name
                msg.data.append(float(temperature))
                msg.data.append(float(humidity))

                self.ble_publisher.publish(msg)

                # print(f"Temperature: {msg.data[0]} C")
                # print(f"Humidity: {msg.data[1]} %")
                # print(f"Pressure: {pressure.decode('utf-8')}")
                # print(f"Altitude: {altitude.decode('utf-8')}")
                await asyncio.sleep(1)

            except Exception as e:
                print(f"Error receiving data: {e}")
                break


    async def connect_probes(self):
        """
        (None) -> (None)

        Make simultaneous connections to both the probes that were found
        """
        if len(self.probes) != 2:
            self.get_logger().error(f"Could not find the temp/hum probes")
            return
        
        # Make two separate clients at the same time to receive data simultaneously
        await asyncio.gather(
            self.connect_and_communicate(self.probes[0]),
            self.connect_and_communicate(self.probes[1])
        )


    async def connect_and_communicate(self, device : BLEDevice):
        """
        (BLEDevice) -> (None)

        Make a client connection via BLE to the found device

        parameters:
            - device (BLEDevice): Probe device to connect to 
                                  and receive data from
        """

        async with BleakClient(device) as client:
            self.get_logger().info(f"Connected to {device.name}")
            await self.receive_data(client, device)

        # receive_data will stop only when the device is disconnected
        print("Disconnected.")


if __name__ == "__main__":

    # MAC Addresses of Arduinos being currently used (just in case)
    bme_address1 = "B0:B2:1C:49:ED:16"
    bme_address2 = "B0:B2:1C:4A:01:4E"
    # asyncio.run(connect_and_communicate(bme_address))
    
    rclpy.init()

    BLE_Node = BLEOut()

    try:
        asyncio.run(BLE_Node.run_ble())

    except KeyboardInterrupt:
        # rclpy.spin(BLE_Node)
        print("\nScript stopped by user.")
    
    finally:
        BLE_Node.destroy_node()



