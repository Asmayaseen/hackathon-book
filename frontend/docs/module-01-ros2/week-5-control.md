# Week 5: ros2_control Framework

## Introduction to ros2_control

The ros2_control framework provides a standardized architecture for robot control systems in ROS 2. It decouples controller algorithms from hardware-specific code through well-defined interfaces, enabling you to develop control strategies that work seamlessly across simulation and real robots.

### Why ros2_control?

**Hardware Abstraction**: Write controller code once, deploy to different actuator types (servo motors, hydraulic actuators, electric motors) by swapping hardware interface plugins.

**Real-time Safety**: ros2_control runs controllers in dedicated threads with real-time priorities, ensuring deterministic execution—critical for humanoid balance control where delays can cause falls.

**Ecosystem Integration**: Compatible with MoveIt (motion planning), Gazebo (simulation), and industrial robot drivers. Humanoid projects benefit from reusing proven controller implementations.

**State Management**: Provides lifecycle management for controllers (inactive, active, emergency_stop), enabling safe mode transitions during operation.

## Architecture Overview

ros2_control consists of three main components:

### 1. Hardware Interface

Bridges between controller commands and physical/simulated hardware. Defines how to read sensor data (joint encoders, force sensors) and write actuator commands (motor voltages, position setpoints).

**Interface Types**:
- `CommandInterface`: Write commands to hardware (e.g., `position`, `velocity`, `effort`)
- `StateInterface`: Read sensor data (e.g., `position`, `velocity`, `effort`)

### 2. Controller Manager

Manages controller lifecycle: loading, configuring, activating, deactivating. Ensures only one controller writes to each command interface (prevents conflicts).

### 3. Controllers

Implement control algorithms (PID, model predictive control, impedance control). ROS 2 provides standard controllers:
- **JointTrajectoryController**: Executes smooth multi-joint trajectories
- **JointGroupPositionController**: Simple position commands for joint groups
- **DiffDriveController**: For mobile bases (wheeled humanoids)

## Controller Types for Humanoid Robots

### Position Controllers

Command desired joint angles. The hardware interface (or lower-level controller in the actuator) closes the control loop to achieve the target position.

**Use cases**:
- Reaching to a target pose (arm stretched forward)
- Holding a static posture (standing still)
- Playing back pre-recorded motions

**Limitations**: Cannot directly control contact forces—problematic for tasks like grasping or balancing on compliant surfaces.

### Velocity Controllers

Command desired joint velocities. Useful for continuous motions where exact position is less critical than smooth speed profiles.

**Use cases**:
- Walking with prescribed joint velocity profiles
- Compliant motions that adapt to external forces
- Teleoperation (joystick input maps to joint speeds)

**Limitations**: Position drift over time without feedback correction.

### Effort Controllers

Command desired joint torques/forces. Provides direct control over interaction forces—essential for advanced humanoid behaviors.

**Use cases**:
- Impedance control for safe human-robot interaction
- Force-based grasping (close gripper until target force detected)
- Balance control using ankle/hip torques to regulate center of mass

**Challenges**: Requires accurate dynamic models and force/torque sensing. Most humanoid research operates in effort control mode.

## ros2_control Configuration in URDF

To use ros2_control, add special tags to your URDF that define hardware interfaces and controllers.

### Hardware Interface Definition

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid">

  <!-- Include ros2_control Xacro macros -->
  <xacro:include filename="$(find ros2_control)/urdf/ros2_control.xacro"/>

  <!-- Define ros2_control hardware interface -->
  <ros2_control name="HumanoidRobotSystem" type="system">

    <!-- Hardware plugin (use Gazebo for simulation) -->
    <hardware>
      <plugin>gazebo_ros2_control/GazeboSystem</plugin>
    </hardware>

    <!-- Joint 1: Left shoulder pitch -->
    <joint name="left_shoulder_pitch">
      <!-- State interfaces: what sensors can read -->
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>

      <!-- Command interfaces: what controllers can write -->
      <command_interface name="position">
        <!-- Optional: set initial command value -->
        <param name="initial_value">0.0</param>
      </command_interface>
      <command_interface name="effort"/>

      <!-- Joint limits (optional, can also read from URDF) -->
      <param name="min_position">-1.57</param>
      <param name="max_position">1.57</param>
      <param name="max_velocity">2.0</param>
      <param name="max_effort">100.0</param>
    </joint>

    <!-- Joint 2: Left shoulder roll -->
    <joint name="left_shoulder_roll">
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
      <command_interface name="position"/>
      <command_interface name="effort"/>
      <param name="min_position">-0.785</param>
      <param name="max_position">0.785</param>
    </joint>

    <!-- Joint 3: Left elbow -->
    <joint name="left_elbow">
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
      <command_interface name="position"/>
      <command_interface name="effort"/>
      <param name="min_position">0.0</param>
      <param name="max_position">2.356</param>
    </joint>

    <!-- Repeat for right arm and leg joints... -->

    <!-- Optional: IMU sensor for balance control -->
    <sensor name="imu_sensor">
      <state_interface name="orientation.x"/>
      <state_interface name="orientation.y"/>
      <state_interface name="orientation.z"/>
      <state_interface name="orientation.w"/>
      <state_interface name="angular_velocity.x"/>
      <state_interface name="angular_velocity.y"/>
      <state_interface name="angular_velocity.z"/>
      <state_interface name="linear_acceleration.x"/>
      <state_interface name="linear_acceleration.y"/>
      <state_interface name="linear_acceleration.z"/>
    </sensor>

  </ros2_control>

  <!-- Gazebo plugin to load ros2_control -->
  <gazebo>
    <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
      <robot_param>robot_description</robot_param>
      <robot_param_node>robot_state_publisher</robot_param_node>
      <parameters>$(find humanoid_control)/config/controllers.yaml</parameters>
    </plugin>
  </gazebo>

</robot>
```

### Controller Configuration YAML

Define controller parameters in `config/controllers.yaml`:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz - control loop frequency

    # List of controllers to load on startup
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    arm_position_controller:
      type: position_controllers/JointGroupPositionController

    arm_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController

# Joint state broadcaster: publishes /joint_states topic
joint_state_broadcaster:
  ros__parameters:
    # No additional config needed - broadcasts all joints automatically

# Arm position controller: simple position commands
arm_position_controller:
  ros__parameters:
    joints:
      - left_shoulder_pitch
      - left_shoulder_roll
      - left_elbow
      - right_shoulder_pitch
      - right_shoulder_roll
      - right_elbow

    # Interface to command (position, velocity, or effort)
    interface_name: position

# Arm trajectory controller: smooth trajectory execution
arm_trajectory_controller:
  ros__parameters:
    joints:
      - left_shoulder_pitch
      - left_shoulder_roll
      - left_elbow
      - right_shoulder_pitch
      - right_shoulder_roll
      - right_elbow

    # Command interface
    command_interfaces:
      - position

    # State interfaces for feedback
    state_interfaces:
      - position
      - velocity

    # Constraints for trajectory execution
    constraints:
      stopped_velocity_tolerance: 0.01  # rad/s
      goal_time: 0.5  # seconds - time tolerance for reaching goal

    # PID gains for trajectory tracking (per joint)
    gains:
      left_shoulder_pitch: {p: 100.0, d: 10.0, i: 0.0, i_clamp: 1.0}
      left_shoulder_roll: {p: 80.0, d: 8.0, i: 0.0, i_clamp: 1.0}
      left_elbow: {p: 60.0, d: 6.0, i: 0.0, i_clamp: 1.0}
      right_shoulder_pitch: {p: 100.0, d: 10.0, i: 0.0, i_clamp: 1.0}
      right_shoulder_roll: {p: 80.0, d: 8.0, i: 0.0, i_clamp: 1.0}
      right_elbow: {p: 60.0, d: 6.0, i: 0.0, i_clamp: 1.0}
```

## Control Loop Basics

The ros2_control control loop follows this sequence (executed at `update_rate`, e.g., 100 Hz):

### 1. Read State

Hardware interface reads current joint positions, velocities, and efforts from encoders/sensors.

```cpp
// Pseudocode - actual implementation in hardware plugin
for (auto& joint : joints_) {
  joint.position = read_encoder(joint.name);
  joint.velocity = compute_velocity(joint.position, previous_position, dt);
  joint.effort = read_current_sensor(joint.name);
}
```

### 2. Update Controllers

Each active controller runs its control algorithm, reading state and computing commands.

```cpp
// JointTrajectoryController update (simplified)
for (size_t i = 0; i < joints_.size(); ++i) {
  // Get target position from trajectory at current time
  double target_position = trajectory_.sample(current_time, i);

  // PID control law
  double error = target_position - joint_state_[i].position;
  double error_derivative = -joint_state_[i].velocity;  // Assumes target velocity = 0

  // Compute command (effort in this case)
  joint_commands_[i].effort = gains_[i].p * error + gains_[i].d * error_derivative;

  // Clamp to joint limits
  joint_commands_[i].effort = std::clamp(
    joint_commands_[i].effort,
    -max_effort_[i],
    max_effort_[i]
  );
}
```

### 3. Write Commands

Hardware interface sends commands to actuators.

```cpp
// Pseudocode
for (auto& joint : joints_) {
  write_motor_command(joint.name, joint.command_effort);
}
```

### 4. Repeat

Loop repeats at fixed rate. Real-time scheduling ensures deterministic timing.

## Launching ros2_control System

```python
#!/usr/bin/env python3
"""
Launch file for humanoid robot with ros2_control.
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Get URDF file path
    urdf_path = os.path.join(
        get_package_share_directory('humanoid_description'),
        'urdf',
        'humanoid.urdf.xacro'
    )

    # Get controller config path
    controller_config = os.path.join(
        get_package_share_directory('humanoid_control'),
        'config',
        'controllers.yaml'
    )

    return LaunchDescription([
        # Start Gazebo simulation
        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
            output='screen'
        ),

        # Spawn robot in Gazebo
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-entity', 'humanoid', '-topic', 'robot_description'],
            output='screen'
        ),

        # Publish robot description
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_path).read()}],
            output='screen'
        ),

        # Load and start controller manager
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[controller_config],
            output='screen'
        ),

        # Spawn controllers
        ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                 'joint_state_broadcaster'],
            output='screen'
        ),

        ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                 'arm_trajectory_controller'],
            output='screen'
        ),

        # Launch RViz for visualization
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.join(
                get_package_share_directory('humanoid_description'),
                'rviz',
                'humanoid.rviz'
            )],
            output='screen'
        ),
    ])
```

## Testing Controllers

```bash
# List available controllers
ros2 control list_controllers

# Check controller status
ros2 control list_hardware_interfaces

# Send position command to arm controller
ros2 topic pub /arm_position_controller/commands std_msgs/msg/Float64MultiArray \
  "{data: [0.5, 0.3, 1.2, -0.5, -0.3, -1.2]}"

# Send trajectory to trajectory controller
ros2 action send_goal /arm_trajectory_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  -f trajectory_goal.yaml
```

## Hardware Interfaces for Real Robots

For physical humanoid hardware, implement a custom hardware interface plugin:

```cpp
#include "hardware_interface/system_interface.hpp"

class HumanoidHardwareInterface : public hardware_interface::SystemInterface
{
public:
  // Initialize hardware (open serial ports, connect to motor controllers)
  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override;

  // Read joint states from encoders
  hardware_interface::return_type read(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

  // Write commands to motors
  hardware_interface::return_type write(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  // Hardware communication (e.g., CAN bus, EtherCAT)
  std::unique_ptr<MotorController> motor_controller_;

  // Cached state/command values
  std::vector<double> joint_positions_;
  std::vector<double> joint_velocities_;
  std::vector<double> joint_efforts_;
  std::vector<double> joint_commands_;
};
```

## Next Steps

You now understand how ros2_control bridges simulation and hardware through standardized interfaces. The final chapter provides a **Complete URDF Example** with integrated ros2_control configuration—a working humanoid robot ready for simulation in Gazebo.

### Practice Exercise

1. Modify `controllers.yaml` to create a `leg_position_controller` for hip and knee joints
2. Launch the system in Gazebo
3. Send commands to move the legs using `ros2 topic pub`
4. Monitor joint states with `ros2 topic echo /joint_states`
5. Tune PID gains to achieve smooth motion without oscillation
