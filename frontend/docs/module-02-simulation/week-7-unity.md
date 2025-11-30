# Week 7: Unity for Robotics

![Unity for Robotics](/img/ai-17.png)

## Why Unity for Robotics?

While Gazebo excels at ROS2 integration, **Unity** offers:

1. **Photorealistic Rendering**: Essential for vision-based policies and sim-to-real transfer
2. **NVIDIA PhysX**: High-performance physics with GPU acceleration
3. **ML-Agents Integration**: Built-in reinforcement learning framework
4. **VR/AR Support**: Human-robot interaction studies and teleoperation

**Unity Robotics Hub** bridges Unity with ROS2 via TCP, enabling seamless integration.

## Installation and Setup

```bash
# Prerequisites: Unity 2021.3 LTS or later
# Download Unity Hub from https://unity.com/download

# Install Unity Robotics Hub packages in Unity:
# 1. Open Unity Editor
# 2. Window → Package Manager → Add package from git URL:
#    - com.unity.robotics.urdf-importer
#    - com.unity.robotics.ros-tcp-connector

# Install ROS2 side (ROS-TCP-Endpoint)
cd ~/ros2_ws/src
git clone https://github.com/Unity-Technologies/ROS-TCP-Endpoint.git
cd ~/ros2_ws
colcon build --packages-select ros_tcp_endpoint
source install/setup.bash

# Launch ROS2 endpoint (bridge)
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1
```

## URDF Importer: From ROS to Unity

Unity uses **articulation bodies** (PhysX feature) for multi-body dynamics. The URDF importer converts ROS robot descriptions to Unity GameObjects.

**Workflow**:

1. Export URDF from ROS2 workspace (example: TurtleBot3)

```bash
# Locate URDF file
find ~/ros2_ws/src -name "*.urdf"
# Example: ~/ros2_ws/src/turtlebot3/turtlebot3_description/urdf/turtlebot3_waffle.urdf
```

2. Import in Unity:
   - `Assets → Import Robot from URDF`
   - Select `.urdf` file
   - Choose **Import Settings**:
     - **Mesh Decomposition**: Convex hull (faster collision)
     - **Axis Type**: Y-Up (Unity convention)
     - **Articulation Body**: Enabled

3. Result: GameObject hierarchy with:
   - **ArticulationBody** components (joints)
   - **MeshRenderer** (visual)
   - **MeshCollider** (collision)

**Example: Simple 2-DOF Arm in URDF**:

```xml
<!-- two_dof_arm.urdf -->
<robot name="simple_arm">
  <link name="base_link">
    <visual>
      <geometry><box size="0.1 0.1 0.2"/></geometry>
      <material name="blue"><color rgba="0 0 1 1"/></material>
    </visual>
    <collision>
      <geometry><box size="0.1 0.1 0.2"/></geometry>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.005"/>
    </inertial>
  </link>

  <joint name="shoulder_joint" type="revolute">
    <parent link="base_link"/>
    <child link="upper_arm"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 0 1"/> <!-- Rotate around Z -->
    <limit lower="-1.57" upper="1.57" effort="10" velocity="2.0"/>
  </joint>

  <link name="upper_arm">
    <visual>
      <geometry><cylinder radius="0.05" length="0.3"/></geometry>
      <material name="red"><color rgba="1 0 0 1"/></material>
    </visual>
    <collision>
      <geometry><cylinder radius="0.05" length="0.3"/></geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.008" ixy="0" ixz="0" iyy="0.008" iyz="0" izz="0.001"/>
    </inertial>
  </link>
</robot>
```

After import, Unity creates:
- `base_link` (GameObject with ArticulationBody, immovable anchor)
- `upper_arm` (child GameObject, ArticulationBody with revolute joint)

## Articulation Bodies: Unity's Multi-Body Physics

**ArticulationBody** is Unity's solution for robotic chains (replaces legacy ConfigurableJoint). Key properties:

```csharp
// C# script to control joint (attach to upper_arm GameObject)
using UnityEngine;

public class JointController : MonoBehaviour
{
    private ArticulationBody articulationBody;

    void Start()
    {
        articulationBody = GetComponent<ArticulationBody>();

        // Configure joint drive (PD controller)
        var drive = articulationBody.xDrive;
        drive.stiffness = 1000f;  // P gain (position control)
        drive.damping = 100f;     // D gain (velocity damping)
        drive.forceLimit = 10f;   // Max torque (10 Nm)
        articulationBody.xDrive = drive;
    }

    void Update()
    {
        // Set target position (in degrees)
        float targetAngle = Mathf.Sin(Time.time) * 90f; // Oscillate ±90°

        var drive = articulationBody.xDrive;
        drive.target = targetAngle;
        articulationBody.xDrive = drive;

        // Read current joint state
        float currentAngle = articulationBody.jointPosition[0] * Mathf.Rad2Deg;
        float currentVelocity = articulationBody.jointVelocity[0];

        Debug.Log($"Joint Angle: {currentAngle:F2}°, Velocity: {currentVelocity:F2} rad/s");
    }
}
```

**Key Difference from Gazebo**: Unity uses **implicit spring-damper drives** (built-in PD control), while Gazebo requires external controllers via plugins.

## PhysX Engine Configuration

Unity's **PhysX** requires tuning for stable humanoid simulation.

**Project Settings → Physics**:

```csharp
// Script to configure physics at runtime (attach to empty GameObject)
using UnityEngine;

public class PhysicsConfig : MonoBehaviour
{
    void Start()
    {
        // Global physics settings
        Physics.gravity = new Vector3(0, -9.81f, 0); // Earth gravity
        Physics.defaultSolverIterations = 12;        // Higher = more stable joints
        Physics.defaultSolverVelocityIterations = 8; // Velocity constraint iterations

        // Time settings (fixed timestep for physics)
        Time.fixedDeltaTime = 0.01f; // 100 Hz physics update (0.01s)

        // Articulation-specific settings
        Physics.ArticulationSolverIterations = 16; // Critical for humanoid stability
        Physics.ArticulationSolverVelocityIterations = 4;
    }
}
```

**Stability Tips**:
- **Solver Iterations**: Increase to 16-24 for humanoids (default 6 is too low)
- **Fixed Timestep**: Keep at 0.01s (100Hz) or lower for multi-body stability
- **Continuous Collision Detection**: Enable on fast-moving links (feet during swing phase)

## ROS2 Integration: Publishing Joint States

**Unity → ROS2 Communication**:

```csharp
// Publish joint states to ROS2 (requires ROS-TCP-Connector)
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class JointStatePublisher : MonoBehaviour
{
    private ROSConnection ros;
    private ArticulationBody[] joints;
    private float publishInterval = 0.1f; // 10 Hz
    private float timer = 0f;

    void Start()
    {
        // Connect to ROS
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<JointStateMsg>("/joint_states");

        // Find all articulation bodies in robot
        joints = GetComponentsInChildren<ArticulationBody>();
    }

    void FixedUpdate()
    {
        timer += Time.fixedDeltaTime;

        if (timer >= publishInterval)
        {
            timer = 0f;
            PublishJointStates();
        }
    }

    void PublishJointStates()
    {
        var msg = new JointStateMsg
        {
            header = new RosMessageTypes.Std.HeaderMsg
            {
                stamp = new RosMessageTypes.Std.TimeMsg
                {
                    sec = (int)Time.time,
                    nanosec = (uint)((Time.time % 1) * 1e9)
                }
            },
            name = new string[joints.Length],
            position = new double[joints.Length],
            velocity = new double[joints.Length],
            effort = new double[joints.Length]
        };

        for (int i = 0; i < joints.Length; i++)
        {
            msg.name[i] = joints[i].name;
            msg.position[i] = joints[i].jointPosition[0]; // Radians
            msg.velocity[i] = joints[i].jointVelocity[0]; // Rad/s
            msg.effort[i] = joints[i].jointForce[0];      // Torque (Nm)
        }

        ros.Publish("/joint_states", msg);
    }
}
```

**ROS2 Subscriber (verify data)**:

```bash
ros2 topic echo /joint_states
```

## Unity ML-Agents for Reinforcement Learning

Unity's **ML-Agents** framework enables training policies directly in Unity (alternative to Isaac Gym).

**Quick Start**:

```csharp
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;

public class HumanoidAgent : Agent
{
    private ArticulationBody[] joints;

    public override void Initialize()
    {
        joints = GetComponentsInChildren<ArticulationBody>();
    }

    // Observations: joint positions + velocities
    public override void CollectObservations(VectorSensor sensor)
    {
        foreach (var joint in joints)
        {
            sensor.AddObservation(joint.jointPosition[0]); // Position
            sensor.AddObservation(joint.jointVelocity[0]); // Velocity
        }
    }

    // Actions: target joint angles
    public override void OnActionReceived(ActionBuffers actions)
    {
        for (int i = 0; i < joints.Length; i++)
        {
            var drive = joints[i].xDrive;
            drive.target = actions.ContinuousActions[i] * 90f; // ±90° range
            joints[i].xDrive = drive;
        }
    }

    // Reward: standing upright
    public void FixedUpdate()
    {
        float uprightBonus = transform.up.y; // 1.0 if perfectly vertical
        AddReward(uprightBonus * 0.01f); // Small reward per step

        if (transform.position.y < 0.5f) // Fell down
        {
            SetReward(-1f);
            EndEpisode();
        }
    }
}
```

**Training**: Use `mlagents-learn` (Python package) with PPO algorithm.

**Exercise**: Import a humanoid URDF into Unity. Create a C# script that applies sinusoidal joint commands to make the robot wave one arm. Publish joint states to ROS2 and visualize in RViz.

---

**Next**: [Week 7 - Building Custom Worlds](./week-7-worlds.md) - Terrains, obstacles, and realistic environments.
