# Code to read BME280 humidity and temperature data for Raspberry Pi
# Ensure bleak library is installed
# Adapted from https://randomnerdtutorials.com/ble-raspberry-pi-and-pi-pico-w/#more-177129

import asyncio
from bleak import BleakScanner, BleakClient, uuids

connected = False

SERVICE_UUID = uuids.normalize_uuid_16(0x181A)
TEMPCHAR_UUID = uuids.normalize_uuid_16(0x2A6E)
HUMCHAR_UUID = uuids.normalize_uuid_16(0x2A6F)
PRESCHAR_UUID = uuids.normalize_uuid_16(0x2A6D)
ALTCHAR_UUID = uuids.normalize_uuid_16(0x2AB3)

async def receive_data_task(client):
    """Receive data from the peripheral device."""
    while True:
        try:
            temperature = await client.read_gatt_char(TEMPCHAR_UUID)
            humidity = await client.read_gatt_char(HUMCHAR_UUID)
            pressure = await client.read_gatt_char(PRESCHAR_UUID)
            altitude = await client.read_gatt_char(ALTCHAR_UUID)

            print(f"Temperature: {temperature.decode('utf-8')}")
            print(f"Humidity: {humidity.decode('utf-8')}")
            print(f"Pressure: {pressure.decode('utf-8')}")
            print(f"Altitude: {altitude.decode('utf-8')}")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

# Original code from link (should work on the Pi):
# async def connect_and_communicate(address):
#     global connected
#     print(f"Connecting to {address}...")
#
#     async with BleakClient(address) as client:
#         connected = client.is_connected
#         print(f"Connected: {connected}")
#         await receive_data_task(client)
#     connected = False

# Adapted code for windows:
async def connect_and_communicate(address):
    global connected
    print(f"Searching for {address}...")
    device = await BleakScanner.find_device_by_address(address, timeout=20.0)
    if device is None:
        print(f"Could not find device with address {address}. Reset your Arduino!")
        return

    print(f"Found {device.name}! Connecting...")

    async with BleakClient(device) as client:
        connected = client.is_connected
        print(f"Connected: {connected}")
        await receive_data_task(client)

    connected = False
    print("Disconnected.")

async def main():
    devices = await BleakScanner.discover()

    for d in devices:
        if d.name == "Nano-Environemtal-Sensor":
            print(d.address)
            break

if __name__ == "__main__":
    bme_address = "b0:b2:1c:49:ed:16"
    try:
        asyncio.run(connect_and_communicate(bme_address))
        # asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript stopped by user.")



