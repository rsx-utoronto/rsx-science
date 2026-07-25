# rsx-science
Repository for all Robotics for Space Exploration - Science subteam code. This includes all the code for microcontrollers, ROS2 connection to software and camera connection + image processing. 

## Science Communication Structure
In the 2025-26 competition year, Science communication was developed into a system combining ROS2 and our custom CAN protocol for Arduinos. The custom CAN for Arduino uses TJA1050 and MCP2515 integrated chips and builds upon the Arduino library for MCP2515: [https://github.com/autowp/arduino-mcp2515](URL). The most recent version of the Science CAN can be found in `ares-can` repository made by Kevin and Vhea: [https://github.com/rsx-utoronto/ares-can](URL).

<img width="960" height="720" alt="Science Communication Architecture" src="https://github.com/user-attachments/assets/5ef884cd-2fc8-4ac3-8c97-b2f73d567400" />

Currently, Science has the following modules:
- `Drill`: Responsible for controlling the linear actuator on the science end-effector and also turning the electromagnet on the end-effector on/off.
- `Chemical`: Responsibe for holding the chemicals for soil analysis and changing their position if necessary using a servo motor.
- `SparkMAX NEOv1`: The actual motor that will perform the drilling together with the linear actuator in the drill module. SparkMAX is the motor controller used for the motors NEOv1, both from Rev Robotics.
- `Optical`: Responsible for performing the fluorescence detection on collected soil sample by controlling the servo for changing samples, turning the UV/Blue-LED sources on/off for illumination and collecting as well as transferring spectrometer data.
- `Multispectral`: Responsible for rotating the wheel on our multispectral camera to change the filter. **NOTE** that the collected images are stored by a different system on the linux computer and not the Arduino Nano.
- `Temp/Humidity`: Responsible for collecting temperating and humidity data using BME280 sensor and Arduino Nano IOT 33. The data is sent to the linux computer directly via BLE.

## Directories

- `arduino_scripts`
Contains arduino `.ino` files for all the modules we use.

- `launch`
Contains launch files for Science ROS2 code.

- `msg`
Contains custom ROS2 message types specifically for Science.

- `resource`
Automatically generated file with ROS2. **DO NOT DELETE**.

- `science`
Contains most of Science code for ROS2 and CAN connections. For more information on files here, check the `README.md` within the directory or contact Abhay (Request from Abhay: please do not contact Abhay).

- `test`
Automatically generated directory when creating a ROS2 package, can be edited/deleted.

## Files
All the files present here are for ROS2 setup and their location should not be changed. Extra care should be taken for `CMakeLists.txt` and `package.xml` since they setup the package completely. Adding new python files for ROS2 may require changes in them. For more details regarding these files, ask Software team or check ROS2 documentation :).
