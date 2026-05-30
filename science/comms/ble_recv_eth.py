#!/usr/bin/env python3

# Code to read BME280 humidity and temperature data for Raspberry Pi
# Ensure bleak library is installed
# Adapted from https://randomnerdtutorials.com/ble-raspberry-pi-and-pi-pico-w/#more-177129

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

RECEIVER_HOST = "192.168.0.123"
RECEIVER_PORT = 5005


class BLEOut:

    def __init__(self):
        # Variable to hold the temp/hum probes as BLE devices
        self.probes = []


    async def run_ble(self):
        """
        (None) -> (None)

        Starts the connection process to find the temp/hum probes
        """

        # Making sure we find all the devices
        while len(self.probes) < len(DEVICE_NAME):
            print(f"Searching for probes")

            # Attempt to find the probes
            await self.find_probes()

        print(f"PROBES FOUND!!")

        # Connect to the ethernet receiver before starting BLE data loop
        while True:
            try:
                print(f"Connecting to receiver {RECEIVER_HOST}:{RECEIVER_PORT}...")
                reader, writer = await asyncio.open_connection(RECEIVER_HOST, RECEIVER_PORT)
                print("TCP connection established.\n")
                break
            except (ConnectionRefusedError, OSError) as e:
                print(f"Connection failed: {e} — retrying in 5s...")
                await asyncio.sleep(5)

        try:
            # Retrieve data from the found probes
            await self.connect_probes(writer)
        finally:
            writer.close()
            await writer.wait_closed()


    async def find_probes(self):
        """
        (None) -> (None)

        Searches for the probes in the surrounding through the
        set device names on the arduino. NOTE: The names MUST match
        the names in DEVICE_NAME variable
        """
        print(f"Searching for {DEVICE_NAME[0]} and {DEVICE_NAME[1]}")

        # Look for devices for 5s
        devices = await BleakScanner.discover(timeout= 5)

        for device in devices:
            if device.name in DEVICE_NAME:

                # Check if the device was already found
                if self.probes == [] or device.name != self.probes[0].name:
                    self.probes.append(device)
                    print(f"Found {device.name}")



    async def receive_data(self, client : BleakClient, device : BLEDevice, writer : asyncio.StreamWriter):
        """
        (BleakClient, BLEDevice, asyncio.StreamWriter) -> (None)

        Receive data from the connected BLE device and forward over TCP.

        parameters:
            - client (BleakClient): Client made from the found BLE device
            - device (BLEDevice): Found BLE device that we are retrieving data from
            - writer (asyncio.StreamWriter): TCP stream to the ethernet receiver
        """

        while True:
            try:
                temperature = await client.read_gatt_char(TEMPCHAR_UUID)
                temperature = temperature.decode('utf-8').replace("C", "")
                humidity = await client.read_gatt_char(HUMCHAR_UUID)
                humidity = humidity.decode('utf-8').replace("%", "")

                line = f"{device.name},{float(temperature):.2f},{float(humidity):.2f}"
                print(f"TX: {line}")
                writer.write((line + "\n").encode("utf-8"))
                await writer.drain()

                await asyncio.sleep(1)

            except Exception as e:
                print(f"Error receiving data: {e}")
                break


    async def connect_probes(self, writer : asyncio.StreamWriter):
        """
        (asyncio.StreamWriter) -> (None)

        Make simultaneous connections to both the probes that were found
        """
        if len(self.probes) != 2:
            print(f"Could not find the temp/hum probes")
            return

        # Make two separate clients at the same time to receive data simultaneously
        await asyncio.gather(
            self.connect_and_communicate(self.probes[0], writer),
            self.connect_and_communicate(self.probes[1], writer)
        )


    async def connect_and_communicate(self, device : BLEDevice, writer : asyncio.StreamWriter):
        """
        (BLEDevice, asyncio.StreamWriter) -> (None)

        Make a client connection via BLE to the found device

        parameters:
            - device (BLEDevice): Probe device to connect to
                                  and receive data from
            - writer (asyncio.StreamWriter): TCP stream to the ethernet receiver
        """

        async with BleakClient(device) as client:
            print(f"Connected to {device.name}")
            await self.receive_data(client, device, writer)

        # receive_data will stop only when the device is disconnected
        print("Disconnected.")


if __name__ == "__main__":

    # MAC Addresses of Arduinos being currently used (just in case)
    bme_address1 = "B0:B2:1C:49:ED:16"
    bme_address2 = "B0:B2:1C:4A:01:4E"

    BLE_Node = BLEOut()

    try:
        asyncio.run(BLE_Node.run_ble())

    except KeyboardInterrupt:
        print("\nScript stopped by user.")
