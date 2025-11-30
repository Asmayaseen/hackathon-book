# Week 10: Bipedal Locomotion Control

## The Bipedal Stability Challenge

Walking on two legs is fundamentally unstable. Unlike wheeled robots with static stability (they remain upright when stopped), humanoids must **dynamically balance** - constantly adjusting to prevent falling.

### Key Challenges

1. **Small Support Polygon**: Feet provide minimal contact area compared to wheeled bases
2. **High Center of Mass**: Humanoid torso is tall, creating large toppling moments
3. **Underactuation**: Fewer actuators than degrees of freedom (cannot directly control all motion)
4. **Phase Transitions**: Switching between single-leg and double-leg support is discontinuous

## Zero Moment Point (ZMP) Criterion

The **Zero Moment Point** is the point on the ground where the sum of gravitational and inertial forces produces zero moment (torque). For stable walking, the ZMP must remain inside the **support polygon** (the convex hull of foot contact points).

### Mathematical Definition

```python
import numpy as np

def compute_zmp(robot_state):
    """
    Compute Zero Moment Point from robot's state.

    Args:
        robot_state: Dictionary with keys:
            - 'com_pos': Center of mass position [x, y, z]
            - 'com_vel': Center of mass velocity [vx, vy, vz]
            - 'com_acc': Center of mass acceleration [ax, ay, az]
            - 'mass': Total robot mass (kg)

    Returns:
        zmp: [x, y] coordinates of ZMP on ground plane
    """
    g = 9.81  # Gravity acceleration (m/s²)

    # Extract state
    x, y, z = robot_state['com_pos']
    vx, vy, vz = robot_state['com_vel']
    ax, ay, az = robot_state['com_acc']
    m = robot_state['mass']

    # ZMP equations (assuming ground at z=0)
    # ZMP_x = x - z * (ax + g*θ_y) / (az + g)
    # ZMP_y = y - z * (ay - g*θ_x) / (az + g)
    # Simplified for small angles:
    zmp_x = x - z * ax / (az + g)
    zmp_y = y - z * ay / (az + g)

    return np.array([zmp_x, zmp_y])

def is_stable(zmp, support_polygon):
    """
    Check if ZMP is inside support polygon.

    Args:
        zmp: [x, y] ZMP coordinates
        support_polygon: List of [x, y] points defining foot contacts

    Returns:
        stable: True if ZMP inside polygon (stable)
    """
    from shapely.geometry import Point, Polygon

    zmp_point = Point(zmp)
    support = Polygon(support_polygon)

    return support.contains(zmp_point)

# Example usage
robot_state = {
    'com_pos': [0.0, 0.0, 0.8],      # CoM at 80cm height
    'com_vel': [0.3, 0.0, 0.0],      # Walking forward at 0.3 m/s
    'com_acc': [0.1, 0.0, -0.5],     # Accelerating forward
    'mass': 45.0                      # 45kg humanoid
}

zmp = compute_zmp(robot_state)
print(f"ZMP position: ({zmp[0]:.3f}, {zmp[1]:.3f})")

# Support polygon during single-leg stance (right foot)
right_foot_polygon = [
    [0.05, 0.05],   # Front-right corner
    [0.05, -0.05],  # Front-left corner
    [-0.05, -0.05], # Back-left corner
    [-0.05, 0.05]   # Back-right corner
]

stable = is_stable(zmp, right_foot_polygon)
print(f"Robot is {'STABLE' if stable else 'UNSTABLE'}")
```

## Gait Generation

A **gait** is a coordinated pattern of leg movements. Humanoid walking typically uses a periodic gait with four phases:

1. **Double Support**: Both feet on ground (stable but slow)
2. **Left Swing**: Right foot supports, left foot moves forward
3. **Double Support**: Both feet on ground (transition)
4. **Right Swing**: Left foot supports, right foot moves forward

### Simple Gait Trajectory Generator

```python
import numpy as np

class BipedGaitGenerator:
    def __init__(self, step_length=0.15, step_height=0.05, step_duration=0.8):
        """
        Initialize bipedal gait generator.

        Args:
            step_length: Forward distance per step (meters)
            step_height: Maximum foot lift height (meters)
            step_duration: Time for one step (seconds)
        """
        self.step_length = step_length
        self.step_height = step_height
        self.step_duration = step_duration
        self.double_support_ratio = 0.2  # 20% of step in double support

    def generate_foot_trajectory(self, t, foot='left'):
        """
        Generate foot trajectory for swing phase.

        Args:
            t: Time within current step (0 to step_duration)
            foot: 'left' or 'right'

        Returns:
            foot_pos: [x, y, z] position of foot
        """
        # Normalize time to [0, 1]
        phase = t / self.step_duration

        # Double support at beginning and end of step
        ds_time = self.double_support_ratio

        if phase < ds_time or phase > (1 - ds_time):
            # Double support - foot on ground
            return self._stance_position(foot)
        else:
            # Swing phase - foot in air
            swing_phase = (phase - ds_time) / (1 - 2*ds_time)  # Normalize to [0, 1]

            # Forward motion (linear)
            x = self.step_length * swing_phase

            # Lateral offset (feet separated by hip width)
            y = 0.1 if foot == 'left' else -0.1

            # Vertical motion (parabolic arc for smooth lift/landing)
            z = 4 * self.step_height * swing_phase * (1 - swing_phase)

            return np.array([x, y, z])

    def _stance_position(self, foot):
        """Return foot position during stance phase."""
        y = 0.1 if foot == 'left' else -0.1
        return np.array([0.0, y, 0.0])

    def generate_com_trajectory(self, t, num_steps):
        """
        Generate center of mass trajectory.
        CoM shifts laterally over support foot during single support.

        Args:
            t: Current time
            num_steps: Number of steps planned

        Returns:
            com_pos: [x, y, z] CoM position
        """
        # Forward velocity
        vx = self.step_length / self.step_duration
        com_x = vx * t

        # Lateral shift (oscillate between left and right)
        step_index = int(t / self.step_duration)
        phase = (t % self.step_duration) / self.step_duration

        # Shift CoM over support foot
        if step_index % 2 == 0:
            # Right foot support - shift CoM right
            com_y = -0.05 * np.sin(np.pi * phase)
        else:
            # Left foot support - shift CoM left
            com_y = 0.05 * np.sin(np.pi * phase)

        # Constant height (simplified)
        com_z = 0.8

        return np.array([com_x, com_y, com_z])

# Usage example
gait = BipedGaitGenerator(step_length=0.15, step_height=0.05, step_duration=0.8)

# Simulate one step
dt = 0.01  # 100 Hz control
for t in np.arange(0, 0.8, dt):
    left_foot = gait.generate_foot_trajectory(t, foot='left')
    right_foot = gait.generate_foot_trajectory(t, foot='right')
    com = gait.generate_com_trajectory(t, num_steps=5)

    # In real implementation, these would be sent to inverse kinematics
    # to compute joint angles
    if int(t / dt) % 10 == 0:  # Print every 0.1s
        print(f"t={t:.2f}s  CoM: {com}  L_foot: {left_foot}  R_foot: {right_foot}")
```

## Balance Control

Maintaining balance requires **real-time feedback control** to correct for disturbances.

### PID Balance Controller

```python
class ZMPBalanceController:
    def __init__(self, kp=0.5, ki=0.01, kd=0.1):
        """
        PID controller to keep ZMP inside support polygon.

        Args:
            kp, ki, kd: PID gains for position, integral, derivative control
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd

        # Controller state
        self.zmp_error_integral = np.zeros(2)
        self.prev_zmp_error = np.zeros(2)

    def compute_correction(self, desired_zmp, actual_zmp, dt):
        """
        Compute CoM acceleration correction to achieve desired ZMP.

        Args:
            desired_zmp: Target ZMP position [x, y]
            actual_zmp: Current ZMP position [x, y]
            dt: Time step (seconds)

        Returns:
            com_acc_correction: [ax, ay] to add to CoM acceleration
        """
        # ZMP error
        zmp_error = desired_zmp - actual_zmp

        # Update integral
        self.zmp_error_integral += zmp_error * dt

        # Compute derivative
        zmp_error_derivative = (zmp_error - self.prev_zmp_error) / dt
        self.prev_zmp_error = zmp_error

        # PID control law
        correction = (
            self.kp * zmp_error +
            self.ki * self.zmp_error_integral +
            self.kd * zmp_error_derivative
        )

        return correction

# Usage in control loop
controller = ZMPBalanceController(kp=0.5, ki=0.01, kd=0.1)

# Simulated control loop
dt = 0.01
desired_zmp = np.array([0.0, 0.0])  # Keep ZMP at center of foot

for i in range(100):
    # Measure current state
    actual_zmp = compute_zmp(robot_state)

    # Compute correction
    com_acc_correction = controller.compute_correction(desired_zmp, actual_zmp, dt)

    # Apply correction to CoM acceleration
    robot_state['com_acc'][:2] += com_acc_correction

    # Update robot state (simplified dynamics)
    robot_state['com_vel'] += robot_state['com_acc'] * dt
    robot_state['com_pos'] += robot_state['com_vel'] * dt

    if i % 10 == 0:
        print(f"ZMP error: {np.linalg.norm(desired_zmp - actual_zmp):.4f}m")
```

## Integration with Nav2

Connecting bipedal locomotion to Nav2 navigation requires a **velocity command interpreter** that converts Nav2's commanded velocities into gait parameters:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray

class BipedalLocomotionNode(Node):
    def __init__(self):
        super().__init__('bipedal_locomotion')

        # Subscribe to Nav2 velocity commands
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.velocity_callback,
            10
        )

        # Publish joint commands to robot
        self.joint_pub = self.create_publisher(
            Float64MultiArray,
            '/joint_commands',
            10
        )

        # Gait generator
        self.gait = BipedGaitGenerator()
        self.controller = ZMPBalanceController()

        # Control loop at 100 Hz
        self.timer = self.create_timer(0.01, self.control_loop)

        self.target_vx = 0.0
        self.target_vy = 0.0
        self.target_omega = 0.0
        self.time = 0.0

    def velocity_callback(self, msg):
        """Receive velocity commands from Nav2."""
        self.target_vx = msg.linear.x
        self.target_vy = msg.linear.y
        self.target_omega = msg.angular.z

        # Adjust gait parameters based on commanded velocity
        self.gait.step_length = self.target_vx * self.gait.step_duration
        self.gait.step_length = np.clip(self.gait.step_length, 0.0, 0.3)  # Max 30cm steps

    def control_loop(self):
        """Generate gait and balance control at 100 Hz."""
        # Generate desired foot and CoM positions
        left_foot = self.gait.generate_foot_trajectory(self.time, 'left')
        right_foot = self.gait.generate_foot_trajectory(self.time, 'right')
        com_ref = self.gait.generate_com_trajectory(self.time, num_steps=5)

        # Balance control (simplified - real implementation needs full state)
        desired_zmp = np.array([0.0, 0.0])  # Center of support foot
        actual_zmp = np.array([0.0, 0.0])   # Would come from sensors
        com_correction = self.controller.compute_correction(desired_zmp, actual_zmp, 0.01)

        # TODO: Inverse kinematics to convert foot/CoM positions to joint angles
        # joint_angles = inverse_kinematics(left_foot, right_foot, com_ref)

        # Publish joint commands
        # joint_msg = Float64MultiArray(data=joint_angles)
        # self.joint_pub.publish(joint_msg)

        self.time += 0.01

def main():
    rclpy.init()
    node = BipedalLocomotionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

## Exercises

1. **ZMP Analysis**: Compute ZMP for a stationary humanoid with CoM at various lateral positions. Identify the stability boundary.

2. **Gait Visualization**: Use matplotlib to plot foot and CoM trajectories over 5 steps. Verify that CoM shifts appropriately over support foot.

3. **PID Tuning**: Implement the ZMP balance controller and tune PID gains to minimize settling time while avoiding oscillations.

4. **Nav2 Integration**: Connect your gait generator to Nav2 velocity commands. Test navigation to waypoints in simulation.

---

**Congratulations!** You've completed Module 3: NVIDIA Isaac Platform. You now understand GPU-accelerated simulation, synthetic data generation, hardware-accelerated perception, and bipedal locomotion control - the core technologies enabling next-generation humanoid robots.

**Next Module**: [Module 4 - Vision-Language-Action Models](../module-04-vla/intro.md)
