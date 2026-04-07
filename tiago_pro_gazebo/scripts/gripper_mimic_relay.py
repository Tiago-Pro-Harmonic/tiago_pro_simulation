#!/usr/bin/env python3

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

"""Relay node that enforces gripper mimic joints in Gazebo Harmonic simulation.

Background
----------
sdformat_urdf drops URDF <mimic> tags when converting to SDF, so Gazebo physics
does not enforce the mechanical coupling between the pal-pro-gripper finger joints.
gz_ros2_control also has no built-in mimic support, and hardware_interface forbids
command_interface on mimic joints.

This node reads the actuated finger joint position from /joint_states and publishes
the corresponding target position for each mimic joint as a std_msgs/Float64 on
/gz_gripper_mimic/{joint_name}. ros_gz_bridge forwards these to Gazebo transport
topics consumed by gz::sim::systems::JointPositionController plugins in the URDF.

Multipliers match gripper.urdf.xacro <mimic> tags:
  inner/outer finger  : -8.28 * finger_joint
  fingertip           :  8.28 * finger_joint
  finger_right        :  0.22 * finger_joint
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64

# (mimic_joint_suffix, multiplier)
_MIMIC_JOINTS = [
    ('outer_finger_right_joint', -8.28),
    ('inner_finger_right_joint', -8.28),
    ('fingertip_right_joint',     8.28),
    ('finger_right_joint',        0.22),
    ('outer_finger_left_joint',  -8.28),
    ('inner_finger_left_joint',  -8.28),
    ('fingertip_left_joint',      8.28),
]

_GRIPPER_SIDES = ('left', 'right')


class GripperMimicRelay(Node):

    def __init__(self):
        super().__init__('gripper_mimic_relay')

        # Build per-joint publishers keyed by actuated finger joint name
        # { finger_joint_name : [(publisher, multiplier), ...] }
        self._gripper_pubs = {}
        for side in _GRIPPER_SIDES:
            prefix = f'gripper_{side}'
            finger_joint = f'{prefix}_finger_joint'
            pubs = []
            for suffix, multiplier in _MIMIC_JOINTS:
                joint_name = f'{prefix}_{suffix}'
                topic = f'/gz_gripper_mimic/{joint_name}'
                pub = self.create_publisher(Float64, topic, 10)
                pubs.append((pub, multiplier))
            self._gripper_pubs[finger_joint] = pubs

        self._sub = self.create_subscription(
            JointState, '/joint_states', self._joint_states_cb, 10)

        self.get_logger().info('Gripper mimic relay started.')

    def _joint_states_cb(self, msg: JointState):
        joint_pos = dict(zip(msg.name, msg.position))

        for finger_joint, pubs in self._gripper_pubs.items():
            if finger_joint not in joint_pos:
                continue
            p = joint_pos[finger_joint]
            for pub, multiplier in pubs:
                cmd = Float64()
                cmd.data = multiplier * p
                pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = GripperMimicRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
