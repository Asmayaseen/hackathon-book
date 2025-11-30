# Week 3: Nodes and Topics

## Understanding the Publish-Subscribe Pattern

The publish-subscribe pattern is the backbone of ROS 2 communication. Unlike direct function calls between modules, pub-sub decouples data producers from consumers. A publisher broadcasts messages on a named topic without knowing which nodes (if any) are listening. Subscribers receive all messages on topics they're interested in, without knowing the source.

For humanoid robots, this pattern is essential. Consider a balance controller that needs foot pressure data. Multiple sensors (left foot, right foot, toe pressure, heel pressure) can publish to separate topics. The balance controller subscribes to all relevant topics, processing data as it arrives—without tight coupling to specific sensor implementations.

### Topic Characteristics

**Topics are typed**: Each topic has a specific message type (e.g., `sensor_msgs/msg/JointState`). Publishers and subscribers must agree on the type, ensuring type safety at compile time.

**Topics are many-to-many**: Multiple publishers can write to one topic (e.g., multiple cameras publishing images). Multiple subscribers can read from one topic (e.g., both a logger and a vision algorithm consuming camera data).

**Topics are asynchronous**: Publishers don't wait for subscribers. If no subscribers exist, messages are discarded. This prevents blocking in time-critical control loops.

## Creating Python Nodes with rclpy

The `rclpy` library provides Python bindings for ROS 2. Let's create a complete example: a node that publishes joint angle commands for a humanoid robot.

### Publisher Node: Joint Command Publisher

```python
#!/usr/bin/env python3
"""
Joint command publisher for humanoid robot.
Publishes target angles for shoulder, elbow, hip, and knee joints.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import math

class JointCommandPublisher(Node):
    """
    Publishes periodic joint commands to simulate arm movement.
    """

    def __init__(self):
        # Initialize node with name 'joint_command_publisher'
        super().__init__('joint_command_publisher')

        # Create publisher on /joint_commands topic
        # Queue size of 10 stores up to 10 messages if subscriber can't keep up
        self.publisher_ = self.create_publisher(
            JointState,
            '/joint_commands',
            10
        )

        # Create timer to publish at 10 Hz (100ms period)
        # Humanoid control typically runs at 100-1000 Hz; 10 Hz is for demonstration
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Track time for sinusoidal motion
        self.time_step = 0

        # Define joint names for humanoid arm (matches URDF convention)
        self.joint_names = [
            'left_shoulder_pitch',
            'left_shoulder_roll',
            'left_elbow',
            'right_shoulder_pitch',
            'right_shoulder_roll',
            'right_elbow'
        ]

        self.get_logger().info('Joint command publisher started')

    def timer_callback(self):
        """
        Called every 100ms to publish new joint commands.
        Generates sinusoidal trajectories for smooth arm motion.
        """
        msg = JointState()

        # Populate header with timestamp (required for sensor data)
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        # Set joint names
        msg.name = self.joint_names

        # Generate sinusoidal joint angles (in radians)
        # Amplitude of 0.5 rad ≈ 28 degrees provides safe range of motion
        msg.position = [
            0.5 * math.sin(self.time_step),      # Left shoulder pitch: forward/back
            0.3 * math.cos(self.time_step),      # Left shoulder roll: side to side
            0.8 * math.sin(self.time_step * 2),  # Left elbow: faster bend/extend
            -0.5 * math.sin(self.time_step),     # Right shoulder: opposite of left
            -0.3 * math.cos(self.time_step),
            -0.8 * math.sin(self.time_step * 2)
        ]

        # Velocity (rad/s) - typically computed from position derivatives
        # For demonstration, set to zero (position control mode)
        msg.velocity = [0.0] * len(self.joint_names)

        # Effort (torque in Nm) - not used in position control
        msg.effort = []

        # Publish message
        self.publisher_.publish(msg)

        # Log every 1 second (10 messages)
        if self.time_step % 10 < 0.1:
            self.get_logger().info(f'Published joint commands at t={self.time_step:.1f}s')

        # Increment time for next iteration
        self.time_step += 0.1

def main(args=None):
    # Initialize rclpy library
    rclpy.init(args=args)

    # Create node instance
    node = JointCommandPublisher()

    try:
        # Spin node to process callbacks (runs until Ctrl+C)
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        node.get_logger().info('Shutting down joint command publisher')
    finally:
        # Clean up resources
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Subscriber Node: Joint State Monitor

```python
#!/usr/bin/env python3
"""
Joint state monitor for humanoid robot.
Subscribes to joint commands and logs current positions.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class JointStateMonitor(Node):
    """
    Monitors joint commands and detects potential safety violations.
    """

    def __init__(self):
        super().__init__('joint_state_monitor')

        # Create subscription to /joint_commands topic
        # QoS depth of 10 matches publisher
        self.subscription = self.create_subscription(
            JointState,
            '/joint_commands',
            self.listener_callback,
            10
        )

        # Define joint limits (radians) for safety checking
        # In production, these would come from URDF or config file
        self.joint_limits = {
            'left_shoulder_pitch': (-1.57, 1.57),   # ±90 degrees
            'left_shoulder_roll': (-0.785, 0.785),  # ±45 degrees
            'left_elbow': (0.0, 2.356),             # 0 to 135 degrees
            'right_shoulder_pitch': (-1.57, 1.57),
            'right_shoulder_roll': (-0.785, 0.785),
            'right_elbow': (0.0, 2.356)
        }

        self.get_logger().info('Joint state monitor started')

    def listener_callback(self, msg):
        """
        Called automatically whenever a message is published on /joint_commands.

        Args:
            msg (JointState): Received joint state message
        """
        # Check for safety violations
        for i, joint_name in enumerate(msg.name):
            if joint_name in self.joint_limits:
                position = msg.position[i]
                min_limit, max_limit = self.joint_limits[joint_name]

                if position < min_limit or position > max_limit:
                    self.get_logger().warning(
                        f'SAFETY: {joint_name} at {position:.3f} rad '
                        f'exceeds limits [{min_limit:.3f}, {max_limit:.3f}]'
                    )

        # Log received data (throttled to avoid spam)
        # In production, would send to data recorder or dashboard
        if len(msg.position) > 0:
            self.get_logger().info(
                f'Received: {len(msg.position)} joints, '
                f'first position: {msg.position[0]:.3f} rad'
            )

def main(args=None):
    rclpy.init(args=args)
    node = JointStateMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down joint state monitor')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Running the Example

### Step 1: Add Nodes to Package

Save the publisher as `humanoid_ws/src/humanoid_control/humanoid_control/joint_publisher.py` and the subscriber as `joint_monitor.py`. Update `setup.py`:

```python
entry_points={
    'console_scripts': [
        'joint_publisher = humanoid_control.joint_publisher:main',
        'joint_monitor = humanoid_control.joint_monitor:main',
    ],
},
```

### Step 2: Build and Run

```bash
# Build workspace
cd ~/humanoid_ws
colcon build --symlink-install
source install/setup.bash

# Terminal 1: Start publisher
ros2 run humanoid_control joint_publisher

# Terminal 2: Start monitor (in new terminal, after sourcing)
ros2 run humanoid_control joint_monitor

# Terminal 3: Inspect communication
ros2 topic hz /joint_commands  # Should show ~10 Hz
ros2 topic echo /joint_commands  # View raw messages
```

## TurtleSim Example: Visualizing Topics

TurtleSim provides a visual demonstration of pub-sub communication. The turtle's position is controlled via the `/turtle1/cmd_vel` topic.

```bash
# Start turtlesim node
ros2 run turtlesim turtlesim_node

# In new terminal: Publish velocity commands
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.0}}"

# Watch turtle move in circle (2 m/s forward, 1 rad/s rotation)
```

Create a custom controller:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math

class TurtleCircleController(Node):
    def __init__(self):
        super().__init__('turtle_circle')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.publish_velocity)
        self.angle = 0.0

    def publish_velocity(self):
        msg = Twist()
        # Vary linear velocity to create spiral pattern
        msg.linear.x = 2.0 + math.sin(self.angle)
        msg.angular.z = 1.0
        self.publisher_.publish(msg)
        self.angle += 0.1

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(TurtleCircleController())

if __name__ == '__main__':
    main()
```

## Message Types Deep Dive

**sensor_msgs/msg/JointState**: Standard message for robot joint data
- `header`: Timestamp and coordinate frame
- `name[]`: Joint identifiers (must match URDF)
- `position[]`: Angles (rad) or displacements (m)
- `velocity[]`: Angular or linear velocities
- `effort[]`: Torques (Nm) or forces (N)

**geometry_msgs/msg/Twist**: Velocity command for mobile robots
- `linear`: Velocity in x, y, z (m/s)
- `angular`: Rotation around x, y, z (rad/s)

Always check message definitions with `ros2 interface show <msg_type>` before using.

## Next Steps

You now understand topic-based communication and can create publishers and subscribers. Next chapter covers **Services and Actions** for request-response patterns and long-running tasks—essential for high-level robot behaviors like "stand up" or "grasp object."

### Practice Exercise

Extend the joint monitor to compute and publish joint velocities:
1. Subscribe to `/joint_commands`
2. Calculate velocity as (current_position - previous_position) / dt
3. Publish to new topic `/joint_velocities`
4. Visualize with `rqt_plot /joint_velocities`
