cmake_minimum_required(VERSION 3.14.4)  # ROS 2 requires CMake 3.8+
project(science)

# Compiler Settings ====================================================
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()


# ROS 2 Core ===========================================================
find_package(ament_cmake REQUIRED)
# find_package(rclcpp REQUIRED)   # Not needed if there are no cpp nodes
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
# find_package(geometry_msgs REQUIRED)
# find_package(visualization_msgs REQUIRED)
# find_package(tf2_ros REQUIRED)
# find_package(tf2 REQUIRED)
# find_package(message_filters REQUIRED)
find_package(rosidl_default_generators REQUIRED)  # Replaces message_generation




# Science does not need point cloud data manipulation as of yet
# PCL Configuration ====================================================
# find_package(PCL 1.10 REQUIRED)  # Use updated version for ROS 2
# include_directories(${PCL_INCLUDE_DIRS})
# link_directories(${PCL_LIBRARY_DIRS})
# add_definitions(${PCL_DEFINITIONS})


# Declare Custom Messages ==============================================
set(msg_files
  "msg/Science.msg"
)

rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  DEPENDENCIES
  std_msgs
#   sensor_msgs
#   geometry_msgs
#   visualization_msgs
)

# target_include_directories(drive_sender_node PUBLIC
#   "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
#   "$<INSTALL_INTERFACE:include/${rover}>"
# )


# Install Targets =====================================================
# install(
#   DIRECTORY include/
#   DESTINATION include
# )

# Install launch files =================================================
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# Setup for Python Script ==============================================
install(PROGRAMS
    science/hello_science.py
    science/pub_image.py
    science/sub.py
    science/science_test.py
    DESTINATION lib/${PROJECT_NAME}
)

# Export dependencies ==================================================
ament_export_dependencies(
  std_msgs
  rosidl_default_runtime # Allows python to import custom messages
  sensor_msgs
#   geometry_msgs
#   visualization_msgs
)

ament_package()