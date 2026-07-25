# Science Communication Code

This directory contains all the science communication code that is required to transfer data from our sensors to the ROS2 network so that the base station can access it.

## Directories

- `calibration_photos2`: Contains photos for the calibration of our Teledyne DALSA Genie camera used in multispectral module. **NOTE** these photos are not that well done and need to be properly retaken.
- `comms`: Contains all our communication files which includes our CAN connection files to send and receive messages over the CANBUS, BLE connection files to send receive messages over bluetooth, controller files to receive messages from an external joystick that is shared with Arm and other files than set up ROS2 nodes for communication with the base station.
- `genie_cam`: Contains all python code that is needed to take images from our Teledyne DALSA Genie camera. **NOTE** that the library used for this camera `pygigev` works only for Python 3.8 or below, while ROS2 works for Python 3.9 or above. This compatibility issue requires image capturing code to run in a separate virtual python environment (at the time of writing this description).

## Files

The remaining files are for either texting or further documentation.
- `hello_science.py`: Quick test to see if ROS2 package was built correctly.
- `image.jpg`: Test image from our multispectral camera.
- `requirements.txt`: A text file containing all the python libraries that our code needs that is not automatically installed. **NOTE** update it whenever a new library is used for easier documentation as well as installation.
- `sub.py`: A simple test ROS2 subscriber file.
