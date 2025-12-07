# ہفتہ 7: سینسر سیمولیشن

![Sensor Simulation](/img/ai-8.png)

## کیوں سینسر سیمولیشن اہم ہے

فزیکل AI سسٹم نوائس، نامکمل سینسر ڈیٹا پر انحصار کرتے ہیں۔ حقیقی خصوصیات کے ساتھ سینسرز کی تقلید سیم-ٹو-ریل ٹرانسفر کے لئے اہم ہے۔ کلیدی چیلنجز:

1. **نوائس اور ڈریفٹ**: حقیقی سینسرز میں گاؤسی نوائس، بائس ڈریفٹ، اور کوانٹائزیشن ہوتا ہے
2. **اپ ڈیٹ ریٹس**: سینسرز مختلف فریکوئنسیز پر چلتے ہیں (IMU: 200Hz، LiDAR: 10-20Hz، کیمرہ: 30Hz)
3. **لیسی**: ڈیٹا دیری کے ساتھ آتا ہے (10-50ms عام)
4. **ماحولیاتی اثرات**: لائٹنگ کی تبدیلیاں کیمرز کو متاثر کرتی ہیں، ریفلیکٹو سطحیں LiDAR کو الجھاتی ہیں

## LiDAR سیمولیشن

**LiDAR (لائٹ ڈیٹیکشن اینڈ رینجنگ)** لیزر پلسز کے ٹائم کر کے فاصلے کو پیمائش کرتا ہے۔ آؤٹ ڈور نیوی گیشن میں عام۔

```xml
<!-- ہیومنوائڈ سر میں LiDAR سینسر شامل کریں -->
<link name="head">
  <pose>0 0 1.7 0 0 0</pose> <!-- 1.7م اونچائی -->

  <sensor name="lidar_sensor" type="gpu_lidar">
    <pose>0 0 0.1 0 0 0</pose> <!-- سر کے مرکز سے آف سیٹ -->
    <update_rate>10</update_rate> <!-- 10 Hz (روبوٹکس کے لئے عام) -->
    <topic>/humanoid/lidar</topic>

    <lidar>
      <scan>
        <horizontal>
          <samples>720</samples> <!-- 720 ا_POINTS فی اسکین -->
          <resolution>1.0</resolution>
          <min_angle>-3.14159</min_angle> <!-- -180 ڈگری -->
          <max_angle>3.14159</max_angle>  <!-- +180 ڈگری -->
        </horizontal>
        <vertical>
          <samples>16</samples> <!-- 16 عمودی لیئرز -->
          <resolution>1.0</resolution>
          <min_angle>-0.2618</min_angle> <!-- -15 ڈگری -->
          <max_angle>0.2618</max_angle>  <!-- +15 ڈگری -->
        </vertical>
      </scan>

      <range>
        <min>0.1</min> <!-- کم از کم رینج: 10cm -->
        <max>30.0</max> <!-- زیادہ سے زیادہ رینج: 30م -->
        <resolution>0.01</resolution> <!-- 1cm درستگی -->
      </range>

      <!-- حقیقی نوائس ماڈل -->
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.02</stddev> <!-- 2cm معیاری انحراف -->
      </noise>
    </lidar>

    <visualize>true</visualize> <!-- GUI میں ریز دکھائیں -->
  </sensor>
</link>
```

**ROS2 سبسکرائبر (پائیتھن)**:

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
        # رینج ڈیٹا نکالیں
        ranges = msg.ranges  # فاصلے کی فہرست (میٹرز)
        angles = [msg.angle_min + i * msg.angle_increment
                  for i in range(len(ranges))]

        # قریب ترین رکاوٹ کا پتہ لگائیں
        valid_ranges = [r for r in ranges if msg.range_min < r < msg.range_max]
        if valid_ranges:
            min_distance = min(valid_ranges)
            self.get_logger().info(f'قریب ترین رکاوٹ: {min_distance:.2f}م')

def main():
    rclpy.init()
    node = LidarProcessor()
    rclpy.spin(node)
```

## ڈیپتھ کیمرز (Intel RealSense D435)

**ڈیپتھ کیمرز** فی-پکسل ڈیپتھ کے ساتھ RGB امیجز فراہم کرتے ہیں۔ مینوپولیشن اور رکاوٹ سے بچاؤ کے لئے ضروری۔

```xml
<!-- روبوٹ چیسٹ پر نصب RealSense D435 -->
<sensor name="depth_camera" type="depth_camera">
  <pose>0.15 0 1.2 0 0.3 0</pose> <!-- 0.3 rad (17°) نیچے کی طرف جھکاؤ -->
  <update_rate>30</update_rate> <!-- 30 FPS -->
  <topic>/humanoid/depth</topic>

  <camera>
    <horizontal_fov>1.5184</horizontal_fov> <!-- 87° (RealSense سپیک) -->
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format> <!-- RGB8 -->
    </image>
    <clip>
      <near>0.3</near> <!-- کم از کم ڈیپتھ: 30cm -->
      <far>10.0</far> <!-- زیادہ سے زیادہ ڈیپتھ: 10م -->
    </clip>

    <!-- ڈیپتھ-مخصوص نوائس (فاصلے کے ساتھ بڑھ جاتا ہے) -->
    <noise>
      <type>gaussian</type>
      <mean>0.0</mean>
      <stddev>0.007</stddev> <!-- 1m پر 7mm (D435 کے لئے حقیقی) -->
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

**ڈیپتھ امیجز کی پروسیسنگ (پائیتھن + OpenCV)**:

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
        # ROS Image کو OpenCV فارمیٹ میں تبدیل کریں (32FC1 - فلوٹ ڈیپتھ)
        depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')

        # گریسپیبل آبجیکٹس تلاش کریں (20cm - 50cm رینج)
        mask = cv2.inRange(depth_image, 0.2, 0.5)

        # نوائس کو صاف کرنے کے لئے مورفولوجیکل آپریشنز
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # سب سے بڑا کنٹور تلاش کریں (م potential گریسپ ٹارگیٹ)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M['m00'] > 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                depth = depth_image[cy, cx]
                self.get_logger().info(f'ٹارگیٹ at ({cx}, {cy}), ڈیپتھ: {depth:.2f}م')
```

## IMU (انرٹیل میجورمٹ یونٹ)

IMU **لکیری ایکسلریشن** اور **اینگولر رفتار** کو پیمائش کرتے ہیں۔ ہیومنوائڈز میں توازن کنٹرول کے لئے اہم۔

```xml
<!-- روبوٹ ٹورسو میں IMU (عام جگہ) -->
<sensor name="imu_sensor" type="imu">
  <pose>0 0 1.0 0 0 0</pose> <!-- ماس کا مرکز -->
  <update_rate>200</update_rate> <!-- 200 Hz (ہائی فریکوئنسی کنٹرول) -->
  <topic>/humanoid/imu</topic>

  <imu>
    <!-- ایکسلیرومیٹر نوائس -->
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.017</stddev> <!-- 0.017 m/s² (typical MEMS IMU) -->
          <bias_mean>0.05</bias_mean> <!-- 50 mg بائس ڈریفٹ -->
          <bias_stddev>0.01</bias_stddev>
        </noise>
      </x>
      <y><noise type="gaussian"><mean>0</mean><stddev>0.017</stddev></noise></y>
      <z><noise type="gaussian"><mean>0</mean><stddev>0.017</stddev></noise></z>
    </linear_acceleration>

    <!-- جائراسکوپ نوائس -->
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.00087</stddev> <!-- 0.05°/s نوائس -->
          <bias_mean>0.0001</bias_mean> <!-- جائراسکوپ ڈریفٹ -->
          <bias_stddev>0.00005</bias_stddev>
        </noise>
      </x>
      <y><noise type="gaussian"><mean>0</mean><stddev>0.00087</stddev></noise></y>
      <z><noise type="gaussian"><mean>0</mean><stddev>0.00087</stddev></noise></z>
    </angular_velocity>
  </imu>
</sensor>
```

**Madgwick فلٹر کے ساتھ اورینٹیشن کا تخمینہ**:

```python
from sensor_msgs.msg import Imu
import numpy as np

class OrientationEstimator:
    def __init__(self, beta=0.1):
        self.quaternion = np.array([1.0, 0.0, 0.0, 0.0])  # w, x, y, z
        self.beta = beta  # فلٹر گین

    def update(self, accel, gyro, dt):
        # Madgwick AHRS الگوری دھم (سادہ)
        # نارملائز ایکسلیرومیٹر
        accel = accel / np.linalg.norm(accel)

        # گریڈینٹ ڈیسینٹ الگوری دھم کریکٹو اسٹیپ
        q = self.quaternion
        f = np.array([
            2*(q[1]*q[3] - q[0]*q[2]) - accel[0],
            2*(q[0]*q[1] + q[2]*q[3]) - accel[1],
            2*(0.5 - q[1]**2 - q[2]**2) - accel[2]
        ])

        # جائراسکوپ کے ساتھ کوویٹرین کو اپ ڈیٹ کریں
        q_dot = 0.5 * self.quaternion_multiply(q, [0, gyro[0], gyro[1], gyro[2]])
        q = q + q_dot * dt

        # نارملائز اور سٹور کریں
        self.quaternion = q / np.linalg.norm(q)
```

## جوائنٹ انکوڈرز اور نوائس ماڈلنگ

حقیقی جوائنٹ انکوڈرز میں **کوانٹائزیشن** (ڈسکریٹ اسٹیپس) اور **بیک لیش** (ڈیڈ زون) ہوتا ہے۔

```xml
<!-- حقیقی نوائس کے ساتھ جوائنٹ پوزیشن سینسر -->
<joint name="knee_joint" type="revolute">
  <sensor name="knee_encoder" type="joint_position">
    <update_rate>100</update_rate> <!-- 100 Hz -->
    <noise>
      <type>gaussian</type>
      <mean>0.0</mean>
      <stddev>0.001</stddev> <!-- 0.001 rad (~0.06°) کوانٹائزیشن -->
    </noise>
  </sensor>
</joint>
```

**ورزش**: چاروں سینسرز (LiDAR، ڈیپتھ کیمرہ، IMU، جوائنٹ انکوڈرز) کو ہیومنوائڈ ماڈل میں شامل کریں۔ IMU اور جوائنٹ انکوڈر ڈیٹا کو فیوژن کرنے والے ROS2 نوڈ کو تخلیق کریں تاکہ روبوٹ کا جھکاؤ زاویہ کا تخمینہ لگایا جا سکے۔ ٹورسو پر لگائی گئی پش فورس کے ساتھ ٹیسٹ کریں۔

---

**اگلا**: [ہفتہ 7 - روبوٹکس کے لئے یونٹی](./week-7-unity.md) - یونٹی روبوٹکس ہب کے ساتھ ہائی فیڈلٹی سیمولیشن۔