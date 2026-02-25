# Copyright (c) 2024 PAL Robotics S.L. All rights reserved.
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

import os
from pathlib import Path

from launch import LaunchDescription

from launch_ros.actions import Node
from dataclasses import dataclass
from launch_pal.arg_utils import LaunchArgumentsBase

from ament_index_python.packages import get_package_share_directory


@dataclass(frozen=True)
class LaunchArguments(LaunchArgumentsBase):
    pass


def generate_launch_description():

    # Create the launch description
    ld = LaunchDescription()
    launch_arguments = LaunchArguments()

    launch_arguments.add_to_launch_description(ld)

    declare_actions(ld, launch_arguments)

    return ld


def declare_actions(launch_description: LaunchDescription, launch_args: LaunchArguments):
    
    # sim_dir = get_package_share_directory('tiago_pro_bringup')
    
    gazebo_spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-model", "tiago-pro",
        ],
    )
    
    launch_description.add_action(gazebo_spawn_robot)
    
    # bridge = Node(
    #     package='ros_gz_bridge',
    #     executable='parameter_bridge',
    #     name='bridge_ros_gz',
    #     parameters=[
    #         {
    #             'config_file': os.path.join(
    #                 sim_dir, 'config/bridge', 'tiago_pro_bridge.yaml'
    #             ),
    #             'use_sim_time': True,
    #         }
    #     ],
    #     output='screen',
    # )
    # launch_description.add_action(bridge)

    return
