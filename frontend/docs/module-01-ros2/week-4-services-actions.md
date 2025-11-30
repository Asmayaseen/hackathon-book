# Week 4: Services and Actions

![Services and Actions](/img/ai-6.png)

## Service Client-Server Pattern

While topics enable continuous data streaming, many robot operations require request-response interactions. Services provide synchronous RPC (Remote Procedure Call) semantics: a client sends a request and blocks until receiving a response from the server.

### When to Use Services

Services are ideal for:
- **Infrequent queries**: Computing inverse kinematics for a target pose
- **Configuration changes**: Setting controller gains or switching operational modes
- **State queries**: Requesting current battery level or system diagnostics
- **Atomic operations**: Triggering calibration sequences that must complete before returning

**Critical distinction**: Services block the calling node until complete. Never use services for operations that take more than ~1 second—use actions instead (covered below).

### Service Type Anatomy

Services consist of a request message and a response message. Example: `AddTwoInts.srv`

```
# Request
int64 a
int64 b
---
# Response
int64 sum
```

The `---` separator divides request from response. For humanoid robotics, common service types include:
- `SetBool`: Enable/disable a controller
- `Trigger`: Initiate calibration or homing
- `GetPose`: Query end-effector position

## Service Server Example: Inverse Kinematics Calculator

This server computes joint angles needed to position a humanoid's hand at a target location—a fundamental operation for manipulation tasks.

```python
#!/usr/bin/env python3
"""
Inverse kinematics service for humanoid arm.
Computes joint angles to reach target end-effector pose.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.srv import GetPlan
from geometry_msgs.msg import Pose, Point, Quaternion
from sensor_msgs.msg import JointState
import math

class IKService(Node):
    """
    Provides inverse kinematics solving as a service.
    Simplified 2-DOF arm for demonstration.
    """

    def __init__(self):
        super().__init__('ik_service')

        # Create service server on /compute_ik topic
        # Service type: custom message defined in package
        self.srv = self.create_service(
            GetPlan,  # Reusing existing type for demonstration
            'compute_ik',
            self.compute_ik_callback
        )

        # Arm parameters (meters)
        self.upper_arm_length = 0.3  # Shoulder to elbow
        self.forearm_length = 0.25   # Elbow to wrist

        self.get_logger().info('IK service ready')

    def compute_ik_callback(self, request, response):
        """
        Solve inverse kinematics for 2-DOF planar arm.

        Args:
            request: Contains target pose (position and orientation)
            response: Populated with joint angles

        Returns:
            response: Modified response object (ROS 2 convention)
        """
        # Extract target position from request
        target_x = request.goal.pose.position.x
        target_y = request.goal.pose.position.y

        self.get_logger().info(f'IK request: target=({target_x:.3f}, {target_y:.3f})')

        # Calculate distance to target
        distance = math.sqrt(target_x**2 + target_y**2)

        # Check if target is reachable
        max_reach = self.upper_arm_length + self.forearm_length
        min_reach = abs(self.upper_arm_length - self.forearm_length)

        if distance > max_reach or distance < min_reach:
            self.get_logger().error(
                f'Target unreachable: distance={distance:.3f}m, '
                f'valid range=[{min_reach:.3f}, {max_reach:.3f}]'
            )
            # Return empty response to indicate failure
            return response

        # Compute elbow angle using law of cosines
        # c² = a² + b² - 2ab*cos(C)
        cos_elbow = (
            (target_x**2 + target_y**2 -
             self.upper_arm_length**2 - self.forearm_length**2) /
            (2 * self.upper_arm_length * self.forearm_length)
        )

        # Clamp to [-1, 1] to avoid numerical errors
        cos_elbow = max(-1.0, min(1.0, cos_elbow))
        elbow_angle = math.acos(cos_elbow)

        # Compute shoulder angle
        alpha = math.atan2(target_y, target_x)
        beta = math.atan2(
            self.forearm_length * math.sin(elbow_angle),
            self.upper_arm_length + self.forearm_length * math.cos(elbow_angle)
        )
        shoulder_angle = alpha - beta

        # Populate response (in production, return JointState message)
        self.get_logger().info(
            f'IK solution: shoulder={math.degrees(shoulder_angle):.1f}°, '
            f'elbow={math.degrees(elbow_angle):.1f}°'
        )

        # For demonstration, encode angles in response
        # In real implementation, define custom service type with JointState response
        response.plan.poses = []  # Placeholder

        return response

def main(args=None):
    rclpy.init(args=args)
    node = IKService()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down IK service')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Service Client Example

```python
#!/usr/bin/env python3
"""
Client that requests inverse kinematics solutions.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.srv import GetPlan
from geometry_msgs.msg import PoseStamped, Point

class IKClient(Node):
    def __init__(self):
        super().__init__('ik_client')

        # Create service client
        self.client = self.create_client(GetPlan, 'compute_ik')

        # Wait for service to become available (with 5 second timeout)
        self.get_logger().info('Waiting for IK service...')
        if not self.client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('IK service not available')
            return

        self.get_logger().info('IK service connected')

    def send_request(self, x, y):
        """
        Send IK request for target position.

        Args:
            x (float): Target x coordinate (meters)
            y (float): Target y coordinate (meters)
        """
        # Create request message
        request = GetPlan.Request()
        request.goal = PoseStamped()
        request.goal.pose.position = Point(x=x, y=y, z=0.0)

        # Send request asynchronously (non-blocking)
        future = self.client.call_async(request)

        # Register callback for when response arrives
        future.add_done_callback(self.handle_response)

    def handle_response(self, future):
        """
        Called when service response is received.

        Args:
            future: Future object containing response
        """
        try:
            response = future.result()
            self.get_logger().info('IK solution received')
            # Process response.plan data here
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')

def main(args=None):
    rclpy.init(args=args)
    client = IKClient()

    # Request IK for position (0.4, 0.3)
    client.send_request(0.4, 0.3)

    # Spin to process callbacks
    rclpy.spin(client)

if __name__ == '__main__':
    main()
```

## Action Servers: Long-Running Tasks

Actions extend services for operations that take significant time (seconds to minutes) and require progress feedback. Examples include:
- Walking to a destination (report distance remaining)
- Grasping an object (report contact forces during approach)
- Standup sequence (report completion of each phase)

### Action Structure

Actions have three components:
1. **Goal**: Request message (e.g., target position for walking)
2. **Result**: Final outcome (e.g., success/failure, final pose)
3. **Feedback**: Periodic progress updates (e.g., current distance to goal)

Actions also support **cancellation**—critical for safety when a humanoid must abort a motion.

## Action Server Example: Walk to Position

```python
#!/usr/bin/env python3
"""
Action server for humanoid walking.
Executes walk commands with progress feedback.
"""

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from action_msgs.msg import GoalStatus
# In production, define custom action: WalkToPosition.action
# For demo, using example action type
from example_interfaces.action import Fibonacci
import time

class WalkActionServer(Node):
    """
    Executes walking motions as long-running actions.
    """

    def __init__(self):
        super().__init__('walk_action_server')

        # Create action server
        self._action_server = ActionServer(
            self,
            Fibonacci,  # Replace with custom WalkToPosition action
            'walk_to_position',
            self.execute_callback
        )

        # Walking parameters
        self.walking_speed = 0.5  # m/s

        self.get_logger().info('Walk action server started')

    def execute_callback(self, goal_handle):
        """
        Execute walking action.

        Args:
            goal_handle: Handle for managing action execution

        Returns:
            Result message
        """
        self.get_logger().info('Executing walk action')

        # Extract goal (in real action, this would be target pose)
        target_distance = 2.0  # meters
        steps_required = int(target_distance / self.walking_speed)

        # Create feedback message
        feedback_msg = Fibonacci.Feedback()

        # Simulate walking with periodic feedback
        for step in range(steps_required):
            # Check if cancellation requested
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Walk action canceled')
                return Fibonacci.Result()

            # Compute progress
            distance_covered = step * self.walking_speed
            distance_remaining = target_distance - distance_covered

            # Publish feedback (in real implementation, include current pose)
            feedback_msg.sequence = [int(distance_covered * 100), int(distance_remaining * 100)]
            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f'Walking: {distance_covered:.2f}m covered, '
                f'{distance_remaining:.2f}m remaining'
            )

            # Simulate one second of walking
            time.sleep(1.0)

        # Mark action as succeeded
        goal_handle.succeed()

        # Return result
        result = Fibonacci.Result()
        result.sequence = [int(target_distance * 100)]
        self.get_logger().info(f'Walk completed: {target_distance}m')

        return result

def main(args=None):
    rclpy.init(args=args)
    node = WalkActionServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down walk action server')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Parameters and Dynamic Reconfigure

Parameters allow runtime configuration without restarting nodes—essential for tuning controller gains during testing.

```python
#!/usr/bin/env python3
"""
Demonstrates ROS 2 parameter usage for controller tuning.
"""

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult

class BalanceController(Node):
    def __init__(self):
        super().__init__('balance_controller')

        # Declare parameters with default values
        self.declare_parameter('kp_pitch', 50.0)   # Proportional gain for pitch
        self.declare_parameter('kd_pitch', 10.0)   # Derivative gain
        self.declare_parameter('kp_roll', 50.0)
        self.declare_parameter('kd_roll', 10.0)
        self.declare_parameter('max_torque', 100.0)  # Nm

        # Register callback for parameter changes
        self.add_on_set_parameters_callback(self.parameter_callback)

        # Read initial parameter values
        self.update_gains()

        self.get_logger().info(
            f'Balance controller initialized: '
            f'kp_pitch={self.kp_pitch}, kd_pitch={self.kd_pitch}'
        )

    def update_gains(self):
        """Read current parameter values."""
        self.kp_pitch = self.get_parameter('kp_pitch').value
        self.kd_pitch = self.get_parameter('kd_pitch').value
        self.kp_roll = self.get_parameter('kp_roll').value
        self.kd_roll = self.get_parameter('kd_roll').value
        self.max_torque = self.get_parameter('max_torque').value

    def parameter_callback(self, params):
        """
        Called when parameters are changed via CLI or service.

        Args:
            params: List of parameters being modified

        Returns:
            SetParametersResult: Success/failure indicator
        """
        for param in params:
            self.get_logger().info(f'Parameter changed: {param.name} = {param.value}')

        # Update internal gains
        self.update_gains()

        # Validate parameters (example: ensure gains are positive)
        if self.kp_pitch < 0 or self.kd_pitch < 0:
            self.get_logger().error('Gains must be positive')
            return SetParametersResult(successful=False)

        return SetParametersResult(successful=True)

def main(args=None):
    rclpy.init(args=args)
    node = BalanceController()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
```

### Using Parameters from CLI

```bash
# Get current parameter values
ros2 param get /balance_controller kp_pitch

# Set new value (triggers callback)
ros2 param set /balance_controller kp_pitch 75.0

# List all parameters for a node
ros2 param list /balance_controller

# Save parameters to YAML file
ros2 param dump /balance_controller > controller_params.yaml

# Load parameters from file on startup
ros2 run humanoid_control balance_controller --ros-args --params-file controller_params.yaml
```

## Next Steps

You now understand services for request-response operations, actions for long-running tasks with feedback, and parameters for runtime configuration. The next chapter, **Week 5: URDF**, introduces robot modeling—defining the kinematic structure of a humanoid robot for simulation and control.

### Practice Exercise

Create an action client that:
1. Sends a walk goal to the action server
2. Displays progress feedback in the terminal
3. Cancels the action if user presses 'q'

Hint: Use `rclpy.action.ActionClient` and register callbacks for feedback, result, and goal_response.
