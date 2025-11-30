# Week 6: Gazebo Basics

## Installation and Setup

Gazebo integrates tightly with ROS2. We'll use **Gazebo Fortress** (formerly Ignition Gazebo), the modern replacement for Gazebo Classic.

```bash
# Install Gazebo Fortress on Ubuntu 22.04
sudo apt-get update
sudo apt-get install -y gazebo-fortress

# Verify installation
ign gazebo --version
# Expected output: Gazebo Fortress 6.x.x

# Install ROS2 Gazebo bridge for Humble
sudo apt-get install ros-humble-ros-gz-bridge ros-humble-ros-gz-sim
```

**Key Difference**: Gazebo Classic used `gazebo` commands; Ignition/Fortress uses `ign gazebo`.

## SDF Models: The Robot Description Language

**SDF (Simulation Description Format)** is XML-based and more expressive than URDF. Unlike URDF (designed for kinematics), SDF natively supports:

- Closed kinematic loops
- Multiple models in one file
- Plugin configurations for sensors and controllers

**Example**: Simple humanoid torso with two arms (simplified for clarity).

```xml
<!-- humanoid_torso.sdf -->
<?xml version="1.0"?>
<sdf version="1.8">
  <model name="humanoid_torso">
    <!-- Base link (torso) -->
    <link name="torso">
      <pose>0 0 1.0 0 0 0</pose> <!-- x y z roll pitch yaw -->
      <inertial>
        <mass>15.0</mass> <!-- 15 kg torso -->
        <inertia>
          <ixx>0.5</ixx> <ixy>0</ixy> <ixz>0</ixz>
          <iyy>0.6</iyy> <iyz>0</iyz> <izz>0.3</izz>
        </inertia>
      </inertial>
      <collision name="torso_collision">
        <geometry>
          <box><size>0.3 0.4 0.6</size></box> <!-- Width Depth Height -->
        </geometry>
      </collision>
      <visual name="torso_visual">
        <geometry>
          <box><size>0.3 0.4 0.6</size></box>
        </geometry>
        <material>
          <ambient>0.2 0.2 0.8 1</ambient> <!-- Blue torso -->
        </material>
      </visual>
    </link>

    <!-- Right shoulder joint -->
    <joint name="right_shoulder" type="revolute">
      <parent>torso</parent>
      <child>right_upper_arm</child>
      <axis>
        <xyz>1 0 0</xyz> <!-- Rotate around X-axis (pitch) -->
        <limit>
          <lower>-1.57</lower> <!-- -90 degrees -->
          <upper>1.57</upper>  <!-- +90 degrees -->
          <effort>50</effort>   <!-- Max torque: 50 Nm -->
          <velocity>2.0</velocity> <!-- Max speed: 2 rad/s -->
        </limit>
      </axis>
    </joint>

    <!-- Right upper arm link -->
    <link name="right_upper_arm">
      <pose relative_to="right_shoulder">0 -0.25 0 0 0 0</pose>
      <inertial>
        <mass>2.0</mass>
        <inertia>
          <ixx>0.01</ixx> <ixy>0</ixy> <ixz>0</ixz>
          <iyy>0.01</iyy> <iyz>0</iyz> <izz>0.005</izz>
        </inertia>
      </inertial>
      <collision name="arm_collision">
        <geometry>
          <cylinder><radius>0.05</radius><length>0.3</length></cylinder>
        </geometry>
      </collision>
      <visual name="arm_visual">
        <geometry>
          <cylinder><radius>0.05</radius><length>0.3</length></cylinder>
        </geometry>
      </visual>
    </link>
  </model>
</sdf>
```

**Key Concepts**:
- `<pose>`: Position (x, y, z) and orientation (roll, pitch, yaw in radians)
- `<inertial>`: Mass and moment of inertia tensor (critical for stable simulation)
- `relative_to`: Child link positions relative to parent joint frame

## Physics Engines: ODE vs Bullet

Gazebo supports multiple physics engines. The two most common for humanoid robotics are:

### ODE (Open Dynamics Engine)
- **Pros**: Fast, handles large contact counts well
- **Cons**: Less accurate contact resolution, can be "bouncy"
- **Best For**: Multi-legged robots, rough terrain navigation

### Bullet
- **Pros**: Accurate collision detection, stable stacking
- **Cons**: Slower for many contacts
- **Best For**: Manipulation tasks, precise contact modeling

**World File Configuration**:

```xml
<!-- world_file.sdf -->
<?xml version="1.0"?>
<sdf version="1.8">
  <world name="humanoid_world">
    <!-- Choose physics engine: ode, bullet, dart -->
    <physics name="default_physics" type="bullet">
      <max_step_size>0.001</max_step_size> <!-- 1ms timestep -->
      <real_time_factor>1.0</real_time_factor> <!-- Run at real-time speed -->
      <real_time_update_rate>1000</real_time_update_rate> <!-- 1000 Hz -->
    </physics>

    <!-- Lighting for visualization -->
    <light name="sun" type="directional">
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
    </light>

    <!-- Ground plane -->
    <model name="ground">
      <static>true</static>
      <link name="ground_link">
        <collision name="ground_collision">
          <geometry>
            <plane><normal>0 0 1</normal></plane>
          </geometry>
          <surface>
            <friction>
              <ode><mu>1.0</mu></ode> <!-- Friction coefficient -->
            </friction>
          </surface>
        </collision>
      </link>
    </model>

    <!-- Include our humanoid model -->
    <include>
      <uri>file://humanoid_torso.sdf</uri>
      <pose>0 0 1.5 0 0 0</pose> <!-- Spawn 1.5m above ground -->
    </include>
  </world>
</sdf>
```

## Spawning Robots and Running Simulation

```bash
# Launch Gazebo with the world file
ign gazebo world_file.sdf

# Alternative: Spawn model dynamically via command
ign service -s /world/humanoid_world/create \
  --reqtype ignition.msgs.EntityFactory \
  --reptype ignition.msgs.Boolean \
  --timeout 1000 \
  --req 'sdf_filename: "humanoid_torso.sdf", pose: {position: {z: 2.0}}'
```

**Exercise**: Modify `humanoid_torso.sdf` to add a left arm (mirror the right arm). Adjust inertia values and verify the robot doesn't tip over when spawned.

---

**Next**: [Week 6 - Physics Configuration](./week-6-physics.md) - Tuning collision, friction, and contact forces for realistic humanoid behavior.
