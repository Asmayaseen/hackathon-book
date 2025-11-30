# Week 5: Complete Humanoid URDF Example

## Overview

This chapter presents a complete, working URDF model for a simplified humanoid robot with torso, arms, and legs. The model includes:
- Full kinematic chain (18 degrees of freedom)
- Accurate collision geometry for self-collision avoidance
- Inertial properties for realistic dynamics simulation
- ros2_control integration for position and effort control
- Xacro macros for modularity and maintainability

This robot can be simulated in Gazebo, visualized in RViz, and controlled via ros2_control—providing a foundation for humanoid research and development.

## Robot Specifications

**Degrees of Freedom**:
- Torso: 1 (waist rotation)
- Arms: 8 (4 per arm: shoulder pitch/roll, elbow, wrist rotation)
- Legs: 8 (4 per leg: hip pitch/roll, knee, ankle pitch)
- Hands: Simplified (no individual finger joints in this version)

**Physical Dimensions** (meters):
- Height: 1.65m (comparable to average human)
- Torso: 0.5m tall, 0.3m wide
- Upper arm: 0.3m length
- Forearm: 0.25m length
- Thigh: 0.4m length
- Shin: 0.4m length

## Complete Xacro Model

### Main Robot File: `humanoid.urdf.xacro`

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="simple_humanoid">

  <!-- Include macros for repeated structures -->
  <xacro:include filename="$(find humanoid_description)/urdf/macros.xacro"/>
  <xacro:include filename="$(find humanoid_description)/urdf/materials.xacro"/>

  <!-- Robot parameters -->
  <xacro:property name="pi" value="3.14159265359"/>

  <!-- Link dimensions (meters) -->
  <xacro:property name="torso_width" value="0.3"/>
  <xacro:property name="torso_depth" value="0.2"/>
  <xacro:property name="torso_height" value="0.5"/>

  <xacro:property name="upper_arm_length" value="0.3"/>
  <xacro:property name="upper_arm_radius" value="0.05"/>
  <xacro:property name="forearm_length" value="0.25"/>
  <xacro:property name="forearm_radius" value="0.04"/>

  <xacro:property name="thigh_length" value="0.4"/>
  <xacro:property name="thigh_radius" value="0.06"/>
  <xacro:property name="shin_length" value="0.4"/>
  <xacro:property name="shin_radius" value="0.05"/>

  <xacro:property name="foot_length" value="0.2"/>
  <xacro:property name="foot_width" value="0.1"/>
  <xacro:property name="foot_height" value="0.05"/>

  <!-- Link masses (kg) -->
  <xacro:property name="torso_mass" value="25.0"/>
  <xacro:property name="upper_arm_mass" value="2.5"/>
  <xacro:property name="forearm_mass" value="1.5"/>
  <xacro:property name="hand_mass" value="0.5"/>
  <xacro:property name="thigh_mass" value="5.0"/>
  <xacro:property name="shin_mass" value="3.0"/>
  <xacro:property name="foot_mass" value="1.0"/>

  <!-- ======================== -->
  <!-- Base and Torso           -->
  <!-- ======================== -->

  <!-- Base link (fixed to world in simulation) -->
  <link name="base_link">
    <visual>
      <origin xyz="0 0 0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.4 0.3 0.05"/>
      </geometry>
      <material name="dark_grey"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.4 0.3 0.05"/>
      </geometry>
    </collision>
    <xacro:box_inertia mass="10.0" x="0.4" y="0.3" z="0.05"/>
  </link>

  <!-- Torso link -->
  <link name="torso">
    <visual>
      <origin xyz="0 0 ${torso_height/2}" rpy="0 0 0"/>
      <geometry>
        <box size="${torso_width} ${torso_depth} ${torso_height}"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 ${torso_height/2}" rpy="0 0 0"/>
      <geometry>
        <box size="${torso_width} ${torso_depth} ${torso_height}"/>
      </geometry>
    </collision>
    <xacro:box_inertia mass="${torso_mass}" x="${torso_width}" y="${torso_depth}" z="${torso_height}"/>
  </link>

  <!-- Waist joint: rotation around Z-axis -->
  <joint name="waist_rotation" type="continuous">
    <parent link="base_link"/>
    <child link="torso"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit effort="150.0" velocity="1.5"/>
    <dynamics damping="1.0" friction="0.5"/>
  </joint>

  <!-- ======================== -->
  <!-- Arms (using macro)       -->
  <!-- ======================== -->

  <!-- Left arm -->
  <xacro:arm_assembly
    side="left"
    reflect="1"
    parent="torso"
    origin_xyz="0.0 ${torso_depth/2 + 0.05} ${torso_height - 0.1}"
    origin_rpy="0 0 0"/>

  <!-- Right arm -->
  <xacro:arm_assembly
    side="right"
    reflect="-1"
    parent="torso"
    origin_xyz="0.0 ${-(torso_depth/2 + 0.05)} ${torso_height - 0.1}"
    origin_rpy="0 0 0"/>

  <!-- ======================== -->
  <!-- Legs (using macro)       -->
  <!-- ======================== -->

  <!-- Left leg -->
  <xacro:leg_assembly
    side="left"
    reflect="1"
    parent="base_link"
    origin_xyz="0.0 ${torso_depth/4} 0.05"
    origin_rpy="0 0 0"/>

  <!-- Right leg -->
  <xacro:leg_assembly
    side="right"
    reflect="-1"
    parent="base_link"
    origin_xyz="0.0 ${-torso_depth/4} 0.05"
    origin_rpy="0 0 0"/>

  <!-- ======================== -->
  <!-- ros2_control integration -->
  <!-- ======================== -->

  <xacro:include filename="$(find humanoid_description)/urdf/ros2_control.xacro"/>
  <xacro:humanoid_ros2_control/>

  <!-- ======================== -->
  <!-- Gazebo plugins           -->
  <!-- ======================== -->

  <xacro:include filename="$(find humanoid_description)/urdf/gazebo.xacro"/>

</robot>
```

### Macros File: `macros.xacro`

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- ======================== -->
  <!-- Inertia Macros           -->
  <!-- ======================== -->

  <!-- Box inertia -->
  <xacro:macro name="box_inertia" params="mass x y z">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="${mass}"/>
      <inertia
        ixx="${mass * (y*y + z*z) / 12.0}"
        ixy="0.0" ixz="0.0"
        iyy="${mass * (x*x + z*z) / 12.0}"
        iyz="0.0"
        izz="${mass * (x*x + y*y) / 12.0}"/>
    </inertial>
  </xacro:macro>

  <!-- Cylinder inertia (axis along Z) -->
  <xacro:macro name="cylinder_inertia" params="mass radius length">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="${mass}"/>
      <inertia
        ixx="${mass * (3*radius*radius + length*length) / 12.0}"
        ixy="0.0" ixz="0.0"
        iyy="${mass * (3*radius*radius + length*length) / 12.0}"
        iyz="0.0"
        izz="${mass * radius * radius / 2.0}"/>
    </inertial>
  </xacro:macro>

  <!-- ======================== -->
  <!-- Arm Assembly Macro       -->
  <!-- ======================== -->

  <xacro:macro name="arm_assembly" params="side reflect parent origin_xyz origin_rpy">

    <!-- Upper arm link -->
    <link name="${side}_upper_arm">
      <visual>
        <origin xyz="0 0 ${-upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${upper_arm_radius}" length="${upper_arm_length}"/>
        </geometry>
        <material name="blue"/>
      </visual>
      <collision>
        <origin xyz="0 0 ${-upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${upper_arm_radius}" length="${upper_arm_length}"/>
        </geometry>
      </collision>
      <xacro:cylinder_inertia mass="${upper_arm_mass}" radius="${upper_arm_radius}" length="${upper_arm_length}"/>
    </link>

    <!-- Shoulder pitch joint (forward/backward) -->
    <joint name="${side}_shoulder_pitch" type="revolute">
      <parent link="${parent}"/>
      <child link="${side}_upper_arm"/>
      <origin xyz="${origin_xyz}" rpy="${origin_rpy}"/>
      <axis xyz="0 ${reflect} 0"/>
      <limit lower="${-pi/2}" upper="${pi/2}" effort="100.0" velocity="2.0"/>
      <dynamics damping="0.7" friction="0.5"/>
    </joint>

    <!-- Forearm link -->
    <link name="${side}_forearm">
      <visual>
        <origin xyz="0 0 ${-forearm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${forearm_radius}" length="${forearm_length}"/>
        </geometry>
        <material name="light_blue"/>
      </visual>
      <collision>
        <origin xyz="0 0 ${-forearm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${forearm_radius}" length="${forearm_length}"/>
        </geometry>
      </collision>
      <xacro:cylinder_inertia mass="${forearm_mass}" radius="${forearm_radius}" length="${forearm_length}"/>
    </link>

    <!-- Elbow joint -->
    <joint name="${side}_elbow" type="revolute">
      <parent link="${side}_upper_arm"/>
      <child link="${side}_forearm"/>
      <origin xyz="0 0 ${-upper_arm_length}" rpy="0 0 0"/>
      <axis xyz="0 ${reflect} 0"/>
      <limit lower="0.0" upper="${pi * 0.75}" effort="80.0" velocity="2.0"/>
      <dynamics damping="0.5" friction="0.3"/>
    </joint>

    <!-- Hand link -->
    <link name="${side}_hand">
      <visual>
        <origin xyz="0 0 -0.05" rpy="0 0 0"/>
        <geometry>
          <box size="0.08 0.05 0.1"/>
        </geometry>
        <material name="grey"/>
      </visual>
      <collision>
        <origin xyz="0 0 -0.05" rpy="0 0 0"/>
        <geometry>
          <box size="0.08 0.05 0.1"/>
        </geometry>
      </collision>
      <xacro:box_inertia mass="${hand_mass}" x="0.08" y="0.05" z="0.1"/>
    </link>

    <!-- Wrist joint -->
    <joint name="${side}_wrist_rotation" type="continuous">
      <parent link="${side}_forearm"/>
      <child link="${side}_hand"/>
      <origin xyz="0 0 ${-forearm_length}" rpy="0 0 0"/>
      <axis xyz="0 0 ${reflect}"/>
      <limit effort="30.0" velocity="3.0"/>
      <dynamics damping="0.2" friction="0.1"/>
    </joint>

  </xacro:macro>

  <!-- ======================== -->
  <!-- Leg Assembly Macro       -->
  <!-- ======================== -->

  <xacro:macro name="leg_assembly" params="side reflect parent origin_xyz origin_rpy">

    <!-- Thigh link -->
    <link name="${side}_thigh">
      <visual>
        <origin xyz="0 0 ${-thigh_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${thigh_radius}" length="${thigh_length}"/>
        </geometry>
        <material name="dark_blue"/>
      </visual>
      <collision>
        <origin xyz="0 0 ${-thigh_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${thigh_radius}" length="${thigh_length}"/>
        </geometry>
      </collision>
      <xacro:cylinder_inertia mass="${thigh_mass}" radius="${thigh_radius}" length="${thigh_length}"/>
    </link>

    <!-- Hip pitch joint (forward/backward) -->
    <joint name="${side}_hip_pitch" type="revolute">
      <parent link="${parent}"/>
      <child link="${side}_thigh"/>
      <origin xyz="${origin_xyz}" rpy="${origin_rpy}"/>
      <axis xyz="0 ${reflect} 0"/>
      <limit lower="${-pi/3}" upper="${pi/2}" effort="200.0" velocity="1.5"/>
      <dynamics damping="1.0" friction="0.8"/>
    </joint>

    <!-- Shin link -->
    <link name="${side}_shin">
      <visual>
        <origin xyz="0 0 ${-shin_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${shin_radius}" length="${shin_length}"/>
        </geometry>
        <material name="blue"/>
      </visual>
      <collision>
        <origin xyz="0 0 ${-shin_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${shin_radius}" length="${shin_length}"/>
        </geometry>
      </collision>
      <xacro:cylinder_inertia mass="${shin_mass}" radius="${shin_radius}" length="${shin_length}"/>
    </link>

    <!-- Knee joint -->
    <joint name="${side}_knee" type="revolute">
      <parent link="${side}_thigh"/>
      <child link="${side}_shin"/>
      <origin xyz="0 0 ${-thigh_length}" rpy="0 0 0"/>
      <axis xyz="0 ${reflect} 0"/>
      <limit lower="0.0" upper="${pi * 0.7}" effort="150.0" velocity="1.5"/>
      <dynamics damping="0.8" friction="0.6"/>
    </joint>

    <!-- Foot link -->
    <link name="${side}_foot">
      <visual>
        <origin xyz="${foot_length/4} 0 ${-foot_height/2}" rpy="0 0 0"/>
        <geometry>
          <box size="${foot_length} ${foot_width} ${foot_height}"/>
        </geometry>
        <material name="black"/>
      </visual>
      <collision>
        <origin xyz="${foot_length/4} 0 ${-foot_height/2}" rpy="0 0 0"/>
        <geometry>
          <box size="${foot_length} ${foot_width} ${foot_height}"/>
        </geometry>
      </collision>
      <xacro:box_inertia mass="${foot_mass}" x="${foot_length}" y="${foot_width}" z="${foot_height}"/>
    </link>

    <!-- Ankle pitch joint -->
    <joint name="${side}_ankle_pitch" type="revolute">
      <parent link="${side}_shin"/>
      <child link="${side}_foot"/>
      <origin xyz="0 0 ${-shin_length}" rpy="0 0 0"/>
      <axis xyz="0 ${reflect} 0"/>
      <limit lower="${-pi/4}" upper="${pi/4}" effort="100.0" velocity="1.0"/>
      <dynamics damping="0.5" friction="0.4"/>
    </joint>

  </xacro:macro>

</robot>
```

### Materials File: `materials.xacro`

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Color definitions for visualization -->

  <material name="blue">
    <color rgba="0.2 0.2 0.8 1.0"/>
  </material>

  <material name="light_blue">
    <color rgba="0.4 0.6 1.0 1.0"/>
  </material>

  <material name="dark_blue">
    <color rgba="0.1 0.1 0.4 1.0"/>
  </material>

  <material name="grey">
    <color rgba="0.5 0.5 0.5 1.0"/>
  </material>

  <material name="dark_grey">
    <color rgba="0.3 0.3 0.3 1.0"/>
  </material>

  <material name="black">
    <color rgba="0.1 0.1 0.1 1.0"/>
  </material>

  <material name="white">
    <color rgba="0.9 0.9 0.9 1.0"/>
  </material>

  <material name="red">
    <color rgba="0.8 0.1 0.1 1.0"/>
  </material>

  <material name="green">
    <color rgba="0.1 0.8 0.1 1.0"/>
  </material>

</robot>
```

### ros2_control Configuration: `ros2_control.xacro`

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <xacro:macro name="humanoid_ros2_control">

    <ros2_control name="HumanoidSystem" type="system">

      <hardware>
        <plugin>gazebo_ros2_control/GazeboSystem</plugin>
      </hardware>

      <!-- Waist joint -->
      <joint name="waist_rotation">
        <command_interface name="effort"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <!-- Left arm joints -->
      <joint name="left_shoulder_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="left_elbow">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="left_wrist_rotation">
        <command_interface name="effort"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <!-- Right arm joints (mirror of left) -->
      <joint name="right_shoulder_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="right_elbow">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="right_wrist_rotation">
        <command_interface name="effort"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <!-- Left leg joints -->
      <joint name="left_hip_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="left_knee">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="left_ankle_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <!-- Right leg joints (mirror of left) -->
      <joint name="right_hip_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="right_knee">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="right_ankle_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

    </ros2_control>

    <!-- Load Gazebo ros2_control plugin -->
    <gazebo>
      <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
        <parameters>$(find humanoid_control)/config/controllers.yaml</parameters>
      </plugin>
    </gazebo>

  </xacro:macro>

</robot>
```

## Testing the Model

### Visualize in RViz

```bash
# Convert Xacro to URDF
xacro humanoid.urdf.xacro > humanoid.urdf

# Check for errors
check_urdf humanoid.urdf

# Launch RViz
ros2 launch urdf_tutorial display.launch.py model:=humanoid.urdf.xacro
```

### Simulate in Gazebo

```bash
# Launch Gazebo with robot
ros2 launch humanoid_description gazebo.launch.py

# List controllers
ros2 control list_controllers

# Send test command to left arm
ros2 topic pub /left_arm_position_controller/commands std_msgs/msg/Float64MultiArray \
  "{data: [0.5, 1.0]}"
```

## Module Summary

Congratulations! You have completed Module 1: ROS 2 Fundamentals. You can now:

- Install and configure ROS 2 development environments
- Create publishers, subscribers, services, and action servers
- Model humanoid robots with URDF and Xacro
- Integrate ros2_control for simulation and hardware
- Visualize and test robots in RViz and Gazebo

This foundation prepares you for Module 2: Simulation Environments, where you'll learn advanced Gazebo techniques, sensor simulation, and physics-based contact modeling for humanoid locomotion.

### Next Steps

1. Experiment with the complete humanoid model: modify joint limits, add sensors (cameras, IMU), tune controller gains
2. Implement a balance controller that uses IMU feedback to prevent falling
3. Create trajectory files for coordinated whole-body motions (waving, squatting)
4. Explore MoveIt integration for motion planning with collision avoidance

Continue building your expertise in physical AI and humanoid robotics!
