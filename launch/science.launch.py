from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([
        Node(
            package='science',
            executable='ble_recv.py',
            name='ble_recv',
            output='screen'
        ),
        Node(
            package='science',
            executable='science_gui.py',
            name='science_gui',
            output='screen'
        ),
        Node(
            package='science',
            executable='science_controller.py',
            name='science_controller',
            output='screen'
        ),
        Node(
            package='science',
            executable='scienceCAN_send.py',
            name='scienceCAN_send',
            output='screen'
        ),
        Node(
            package='science',
            executable='scienceCAN_recv.py',
            name='scienceCAN_recv',
            output='screen'
        ),
        Node(
            package='science',
            executable='geniecam_publisher.py',
            name='geniecam_publisher',
            output='screen'
        ),
        Node(
            package='science',
            executable='pub_image.py',
            name='pub_image',
            output='screen'
        )
    ])