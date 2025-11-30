# Week 7: Sensor Simulation

![Sensor Simulation](/img/ai-8.png)

## Why Sensor Simulation Matters

Physical AI systems rely on noisy, imperfect sensor data. Simulating sensors with realistic characteristics is critical for sim-to-real transfer. Key challenges:

1. **Noise and Drift**: Real sensors have Gaussian noise, bias drift, and quantization
2. **Update Rates**: Sensors run at different frequencies (IMU: 200Hz, LiDAR: 10-20Hz, camera: 30Hz)
3. **Latency**: Data arrives with delays (10-50ms typical)
4. **Environmental Effects**: Lighting changes affect cameras, reflective surfaces confuse LiDAR

## LiDAR Simulation

**LiDAR (Light Detection and Ranging)** measures distances by timing laser pulses. Common in outdoor navigation.

```xml
<!-- Add LiDAR sensor to humanoid head -->
<link name="head">
  <pose>0 0 1.7 0 0 0</pose> <!-- 1.7m height -->

  <sensor name="lidar_sensor" type="gpu_lidar">
    <pose>0 0 0.1 0 0 0</pose> <!-- Offset from head center -->
    <update_rate>10</update_rate> <!-- 10 Hz (common for robotics) -->
    <topic>/humanoid/lidar</topic>

    <lidar>
      <scan>
        <horizontal>
          <samples>720</samples> <!-- 720 points per scan -->
          <resolution>1.0</resolution>
          <min_angle>-3.14159</min_angle> <!-- -180 degrees -->
          <max_angle>3.14159</max_angle>  <!-- +180 degrees -->
        </horizontal>
        <vertical>
          <samples>16</samples> <!-- 16 vertical layers -->
          <resolution>1.0</resolution>
          <min_angle>-0.2618</min_angle> <!-- -15 degrees -->
          <max_angle>0.2618</max_angle>  <!-- +15 degrees -->
        </vertical>
      </scan>

      <range>
        <min>0.1</min> <!-- Minimum range: 10cm -->
        <max>30.0</max> <!-- Maximum range: 30m -->
        <resolution>0.01</resolution> <!-- 1cm precision -->
      </range>

      <!-- Realistic noise model -->
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.02</stddev> <!-- 2cm standard deviation -->
      </noise>
    </lidar>

    <visualize>true</visualize> <!-- Show rays in GUI -->
  </sensor>
</link>
```

**ROS2 Subscriber (Python)**:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class LidarProcessor(Node):
    def __init__(self):
        super().__init__('lidar_processor')
        self.subscription = self.create_subscription(
            LaserScan,
            '/humanoid/lidar',
            self.lidar_callback,
            10)

    def lidar_callback(self, msg):
        # Extract range data
        ranges = msg.ranges  # List of distances (meters)
        angles = [msg.angle_min + i * msg.angle_increment
                  for i in range(len(ranges))]

        # Detect closest obstacle
        valid_ranges = [r for r in ranges if msg.range_min < r < msg.range_max]
        if valid_ranges:
            min_distance = min(valid_ranges)
            self.get_logger().info(f'Closest obstacle: {min_distance:.2f}m')

def main():
    rclpy.init()
    node = LidarProcessor()
    rclpy.spin(node)
```

## Depth Cameras (Intel RealSense D435)

**Depth cameras** provide RGB images with per-pixel depth. Essential for manipulation and obstacle avoidance.

```xml
<!-- RealSense D435 mounted on robot chest -->
<sensor name="depth_camera" type="depth_camera">
  <pose>0.15 0 1.2 0 0.3 0</pose> <!-- 0.3 rad (17°) downward tilt -->
  <update_rate>30</update_rate> <!-- 30 FPS -->
  <topic>/humanoid/depth</topic>

  <camera>
    <horizontal_fov>1.5184</horizontal_fov> <!-- 87° (RealSense spec) -->
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format> <!-- RGB8 -->
    </image>
    <clip>
      <near>0.3</near> <!-- Minimum depth: 30cm -->
      <far>10.0</far> <!-- Maximum depth: 10m -->
    </clip>

    <!-- Depth-specific noise (increases with distance) -->
    <noise>
      <type>gaussian</type>
      <mean>0.0</mean>
      <stddev>0.007</stddev> <!-- 7mm at 1m (realistic for D435) -->
    </noise>
  </camera>

  <plugin name="depth_camera_controller" filename="libgazebo_ros_camera.so">
    <ros>
      <namespace>/humanoid</namespace>
      <argument>image_raw:=rgb/image_raw</argument>
      <argument>depth/image_raw:=depth/image_raw</argument>
      <argument>camera_info:=rgb/camera_info</argument>
    </ros>
  </plugin>
</sensor>
```

**Processing Depth Images (Python + OpenCV)**:

```python
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class DepthProcessor(Node):
    def __init__(self):
        super().__init__('depth_processor')
        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            '/humanoid/depth/image_raw',
            self.depth_callback,
            10)

    def depth_callback(self, msg):
        # Convert ROS Image to OpenCV format (32FC1 - float depth)
        depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')

        # Find graspable objects (20cm - 50cm range)
        mask = cv2.inRange(depth_image, 0.2, 0.5)

        # Morphological operations to clean up noise
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find largest contour (potential grasp target)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M['m00'] > 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                depth = depth_image[cy, cx]
                self.get_logger().info(f'Target at ({cx}, {cy}), depth: {depth:.2f}m')
```

## IMU (Inertial Measurement Unit)

IMUs measure **linear acceleration** and **angular velocity**. Critical for balance control in humanoids.

```xml
<!-- IMU in robot torso (common placement) -->
<sensor name="imu_sensor" type="imu">
  <pose>0 0 1.0 0 0 0</pose> <!-- Center of mass -->
  <update_rate>200</update_rate> <!-- 200 Hz (high-frequency control) -->
  <topic>/humanoid/imu</topic>

  <imu>
    <!-- Accelerometer noise -->
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.017</stddev> <!-- 0.017 m/s² (typical MEMS IMU) -->
          <bias_mean>0.05</bias_mean> <!-- 50 mg bias drift -->
          <bias_stddev>0.01</bias_stddev>
        </noise>
      </x>
      <y><noise type="gaussian"><mean>0</mean><stddev>0.017</stddev></noise></y>
      <z><noise type="gaussian"><mean>0</mean><stddev>0.017</stddev></noise></z>
    </linear_acceleration>

    <!-- Gyroscope noise -->
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.00087</stddev> <!-- 0.05°/s noise -->
          <bias_mean>0.0001</bias_mean> <!-- Gyro drift -->
          <bias_stddev>0.00005</bias_stddev>
        </noise>
      </x>
      <y><noise type="gaussian"><mean>0</mean><stddev>0.00087</stddev></noise></y>
      <z><noise type="gaussian"><mean>0</mean><stddev>0.00087</stddev></noise></z>
    </angular_velocity>
  </imu>
</sensor>
```

**Orientation Estimation with Madgwick Filter**:

```python
from sensor_msgs.msg import Imu
import numpy as np

class OrientationEstimator:
    def __init__(self, beta=0.1):
        self.quaternion = np.array([1.0, 0.0, 0.0, 0.0])  # w, x, y, z
        self.beta = beta  # Filter gain

    def update(self, accel, gyro, dt):
        # Madgwick AHRS algorithm (simplified)
        # Normalize accelerometer
        accel = accel / np.linalg.norm(accel)

        # Gradient descent algorithm corrective step
        q = self.quaternion
        f = np.array([
            2*(q[1]*q[3] - q[0]*q[2]) - accel[0],
            2*(q[0]*q[1] + q[2]*q[3]) - accel[1],
            2*(0.5 - q[1]**2 - q[2]**2) - accel[2]
        ])

        # Update quaternion with gyroscope
        q_dot = 0.5 * self.quaternion_multiply(q, [0, gyro[0], gyro[1], gyro[2]])
        q = q + q_dot * dt

        # Normalize and store
        self.quaternion = q / np.linalg.norm(q)
```

## Joint Encoders and Noise Modeling

Real joint encoders have **quantization** (discrete steps) and **backlash** (dead zone).

```xml
<!-- Joint position sensor with realistic noise -->
<joint name="knee_joint" type="revolute">
  <sensor name="knee_encoder" type="joint_position">
    <update_rate>100</update_rate> <!-- 100 Hz -->
    <noise>
      <type>gaussian</type>
      <mean>0.0</mean>
      <stddev>0.001</stddev> <!-- 0.001 rad (~0.06°) quantization -->
    </noise>
  </sensor>
</joint>
```

**Exercise**: Add all four sensors (LiDAR, depth camera, IMU, joint encoders) to a humanoid model. Create a ROS2 node that fuses IMU and joint encoder data to estimate the robot's tilt angle. Test with a push force applied to the torso.

---

**Next**: [Week 7 - Unity for Robotics](./week-7-unity.md) - High-fidelity simulation with Unity Robotics Hub.
