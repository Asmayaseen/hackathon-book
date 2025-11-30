# Week 5: URDF for Humanoid Robots

## Introduction to URDF

The Unified Robot Description Format (URDF) is an XML-based specification for describing robot kinematics, dynamics, and visual appearance. URDF files define the robot's structure as a tree of links (rigid bodies) connected by joints (movable or fixed connections).

For humanoid robots, URDF enables:
- **Simulation**: Visualize robot motion in Gazebo or RViz before hardware testing
- **Kinematics**: Compute forward/inverse kinematics for pose planning
- **Collision detection**: Prevent self-collisions during complex motions
- **Control**: Generate controller configurations from joint definitions

### URDF Philosophy

URDF represents robots as kinematic trees with a single root link (typically `base_link`). Each joint connects a parent link to a child link, defining the relative motion between them. This tree structure matches the physical reality of most robots: a humanoid has a torso (root) with limbs branching outward.

## Joint Types

URDF supports six joint types, each defining different motion constraints:

### Revolute Joints

Rotate around a single axis with angle limits (most common for robot joints).

```xml
<!-- Shoulder pitch joint: rotates around Y-axis -->
<joint name="left_shoulder_pitch" type="revolute">
  <parent link="torso"/>
  <child link="left_upper_arm"/>

  <!-- Joint origin relative to parent link -->
  <origin xyz="0.0 0.15 0.4" rpy="0 0 0"/>

  <!-- Axis of rotation in joint frame -->
  <axis xyz="0 1 0"/>

  <!-- Joint limits (radians) -->
  <limit lower="-1.57" upper="1.57" effort="100.0" velocity="2.0"/>

  <!-- Joint dynamics (optional) -->
  <dynamics damping="0.7" friction="0.5"/>
</joint>
```

**Parameters**:
- `lower/upper`: Angle limits in radians (±90° in this example)
- `effort`: Maximum torque (Nm) the actuator can apply
- `velocity`: Maximum angular velocity (rad/s)
- `damping`: Simulates energy dissipation in bearings
- `friction`: Models static/kinetic friction

### Prismatic Joints

Translate along a single axis (used for telescoping limbs or linear actuators).

```xml
<!-- Telescoping torso joint -->
<joint name="torso_lift" type="prismatic">
  <parent link="base_link"/>
  <child link="torso"/>

  <origin xyz="0 0 0.5" rpy="0 0 0"/>

  <!-- Axis of translation -->
  <axis xyz="0 0 1"/>

  <!-- Linear limits (meters) -->
  <limit lower="0.0" upper="0.3" effort="500.0" velocity="0.1"/>
</joint>
```

### Continuous Joints

Revolute joints without angle limits (for wheels or unrestricted rotation).

```xml
<!-- Waist rotation (360° rotation) -->
<joint name="waist_yaw" type="continuous">
  <parent link="pelvis"/>
  <child link="torso"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit effort="80.0" velocity="1.5"/>
</joint>
```

### Fixed Joints

Rigidly attach links (no motion). Used for sensors, end-effectors, or structural components.

```xml
<!-- Camera mounted on head -->
<joint name="head_camera_joint" type="fixed">
  <parent link="head"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0.05" rpy="0 0 0"/>
</joint>
```

## Link Structure: Visual and Collision Geometry

Each link defines both visual appearance (for rendering) and collision geometry (for physics simulation).

```xml
<link name="left_upper_arm">
  <!-- Visual appearance (what you see in RViz/Gazebo) -->
  <visual>
    <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    <geometry>
      <!-- Cylinder: radius=0.05m, length=0.3m -->
      <cylinder radius="0.05" length="0.3"/>
    </geometry>
    <material name="blue">
      <color rgba="0.0 0.0 0.8 1.0"/>
    </material>
  </visual>

  <!-- Collision geometry (for physics/contact detection) -->
  <!-- Often simplified for performance -->
  <collision>
    <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    <geometry>
      <!-- Same as visual for simple shapes -->
      <cylinder radius="0.05" length="0.3"/>
    </geometry>
  </collision>

  <!-- Inertial properties (for dynamics simulation) -->
  <inertial>
    <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    <mass value="2.5"/>  <!-- kg -->

    <!-- Inertia tensor for cylinder about center of mass -->
    <!-- Computed using: I = m*r²/2 (z-axis), I = m*(3r²+h²)/12 (x,y-axes) -->
    <inertia
      ixx="0.0208" ixy="0.0" ixz="0.0"
      iyy="0.0208" iyz="0.0"
      izz="0.003125"/>
  </inertial>
</link>
```

### Geometry Options

```xml
<!-- Box (width, depth, height in meters) -->
<geometry>
  <box size="0.1 0.2 0.05"/>
</geometry>

<!-- Sphere (radius in meters) -->
<geometry>
  <sphere radius="0.08"/>
</geometry>

<!-- Mesh (load from STL/DAE file) -->
<geometry>
  <mesh filename="package://humanoid_description/meshes/hand.stl" scale="1.0 1.0 1.0"/>
</geometry>
```

## Xacro: Modular URDF

Writing raw URDF for complex robots leads to repetitive code. Xacro (XML Macros) extends URDF with:
- **Variables**: Define constants (link lengths, masses)
- **Macros**: Reusable templates for repeated structures (left/right limbs)
- **Math**: Compute values (inertia tensors, compound transforms)
- **File inclusion**: Split robot into modular files

### Xacro Example: Parameterized Arm

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid_arm">

  <!-- Define constants -->
  <xacro:property name="upper_arm_length" value="0.3"/>
  <xacro:property name="forearm_length" value="0.25"/>
  <xacro:property name="arm_radius" value="0.05"/>
  <xacro:property name="arm_mass" value="2.5"/>

  <!-- Macro for arm links (reusable for left/right) -->
  <xacro:macro name="arm_links" params="side reflect">

    <!-- Upper arm link -->
    <link name="${side}_upper_arm">
      <visual>
        <origin xyz="0 0 ${-upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${arm_radius}" length="${upper_arm_length}"/>
        </geometry>
        <material name="blue">
          <color rgba="0.2 0.2 0.8 1.0"/>
        </material>
      </visual>

      <collision>
        <origin xyz="0 0 ${-upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${arm_radius}" length="${upper_arm_length}"/>
        </geometry>
      </collision>

      <xacro:cylinder_inertia
        mass="${arm_mass}"
        radius="${arm_radius}"
        length="${upper_arm_length}"/>
    </link>

    <!-- Shoulder joint -->
    <joint name="${side}_shoulder_pitch" type="revolute">
      <parent link="torso"/>
      <child link="${side}_upper_arm"/>

      <!-- Reflect parameter: 1 for left, -1 for right -->
      <origin xyz="0.0 ${reflect * 0.15} 0.4" rpy="0 0 0"/>

      <axis xyz="0 1 0"/>
      <limit lower="-1.57" upper="1.57" effort="100.0" velocity="2.0"/>
      <dynamics damping="0.7"/>
    </joint>

    <!-- Forearm link -->
    <link name="${side}_forearm">
      <visual>
        <origin xyz="0 0 ${-forearm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${arm_radius * 0.8}" length="${forearm_length}"/>
        </geometry>
        <material name="blue"/>
      </visual>

      <collision>
        <origin xyz="0 0 ${-forearm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${arm_radius * 0.8}" length="${forearm_length}"/>
        </geometry>
      </collision>

      <xacro:cylinder_inertia
        mass="${arm_mass * 0.8}"
        radius="${arm_radius * 0.8}"
        length="${forearm_length}"/>
    </link>

    <!-- Elbow joint -->
    <joint name="${side}_elbow" type="revolute">
      <parent link="${side}_upper_arm"/>
      <child link="${side}_forearm"/>

      <origin xyz="0 0 ${-upper_arm_length}" rpy="0 0 0"/>

      <axis xyz="0 1 0"/>
      <!-- Elbow only bends one direction -->
      <limit lower="0.0" upper="2.356" effort="80.0" velocity="2.0"/>
      <dynamics damping="0.5"/>
    </joint>

  </xacro:macro>

  <!-- Macro for computing cylinder inertia -->
  <xacro:macro name="cylinder_inertia" params="mass radius length">
    <inertial>
      <origin xyz="0 0 ${-length/2}" rpy="0 0 0"/>
      <mass value="${mass}"/>
      <inertia
        ixx="${mass * (3*radius*radius + length*length) / 12}"
        ixy="0.0" ixz="0.0"
        iyy="${mass * (3*radius*radius + length*length) / 12}"
        iyz="0.0"
        izz="${mass * radius * radius / 2}"/>
    </inertial>
  </xacro:macro>

  <!-- Torso link (root) -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
      <material name="grey">
        <color rgba="0.5 0.5 0.5 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="15.0"/>
      <inertia ixx="0.4" ixy="0.0" ixz="0.0"
               iyy="0.5" iyz="0.0" izz="0.2"/>
    </inertial>
  </link>

  <!-- Instantiate left and right arms -->
  <xacro:arm_links side="left" reflect="1"/>
  <xacro:arm_links side="right" reflect="-1"/>

</robot>
```

### Processing Xacro Files

```bash
# Convert Xacro to URDF
xacro humanoid_arm.urdf.xacro > humanoid_arm.urdf

# View in RViz
ros2 launch urdf_tutorial display.launch.py model:=humanoid_arm.urdf.xacro

# Check for errors
check_urdf humanoid_arm.urdf
```

## Complete Humanoid URDF Example

See the next chapter (**Week 5: Complete URDF Example**) for a full working humanoid robot with torso, arms, legs, and hands—ready for simulation in Gazebo and control with ros2_control.

## Best Practices

1. **Use Xacro for all but trivial robots**: Avoid copy-paste errors and enable easy parameter tuning
2. **Define inertial properties**: Physics simulation requires accurate mass/inertia
3. **Simplify collision geometry**: Use primitive shapes (boxes, cylinders) instead of complex meshes for performance
4. **Follow naming conventions**: Use `<side>_<body_part>_<motion>` (e.g., `left_shoulder_pitch`)
5. **Set realistic limits**: Joint limits should match hardware specifications
6. **Test incrementally**: Build robot link-by-link, testing visualization after each addition

## Next Steps

The next chapter covers **ros2_control**, the framework for connecting URDF models to actual controllers (position, velocity, effort) and hardware interfaces. You'll learn how to make your URDF robot move in simulation and transition to real hardware.

### Practice Exercise

Extend the arm Xacro macro to include:
1. A wrist rotation joint (continuous type)
2. A simple gripper with two fingers (prismatic joints)
3. Force/torque sensor link at the wrist (fixed joint)

Visualize in RViz and verify joint limits work as expected.
