# ہفتہ 3: نوڈس اور ٹاپکس

## شائع کریں-سبسکرائب نمونہ کو سمجھنا

شائع کریں-سبسکرائب نمونہ ROS 2 رابطے کی پشت ہے۔ ماڈیولز کے درمیان براہ راست فنکشن کالز کے برعکس، پب-سب ڈیٹا پیدا کرنے والے اور صارفین کو ایک دوسرے سے الگ کرتا ہے۔ ایک شائع کار ایک نامزد ٹاپک پر پیغامات نشر کرتا ہے جبکہ یہ نہیں جانتا کہ کون سے نوڈس (اگر کوئی ہیں) سنتے ہیں۔ سبسکرائبرز ان ٹاپکس سے تمام پیغامات وصول کرتے ہیں جن میں وہ دلچسپی رکھتے ہیں، ماخذ کو نہیں جانتے ہوئے۔

ہیومنوائڈ روبوٹس کے لئے، یہ نمونہ ضروری ہے۔ تصور کریں کہ ایک توازن کنٹرولر کو فُٹ دباؤ کا ڈیٹا چاہیے۔ متعدد سینسرز (بائیں پاؤں، دائیں پاؤں، انگوٹھے کا دباؤ، اڑیل کا دباؤ) الگ الگ ٹاپکس پر شائع کر سکتے ہیں۔ توازن کنٹرولر تمام متعلقہ ٹاپکس کو سبسکرائب کرتا ہے، ڈیٹا کو اس کے آنے پر پروسیس کرتا ہے— مخصوص سینسر امplementations کے ساتھ تنگ کوپلنگ کے بغیر۔

### ٹاپک کی خصوصیات

**ٹاپکس ٹائپڈ ہیں**: ہر ٹاپک کی ایک مخصوص پیغام کی قسم ہوتی ہے (مثلاً، `sensor_msgs/msg/JointState`)۔ شائع کاروں اور سبسکرائبرز کو قسم پر اتفاق کرنا چاہیے، کمپائل ٹائم پر قسم کی سلامتی کو یقینی بناتے ہوئے۔

**ٹاپکس بہت سے-سے-بہت سے ہیں**: ایک ٹاپک پر متعدد شائع کار لکھ سکتے ہیں (مثلاً، متعدد کیمرز تصاویر شائع کرتے ہیں)۔ ایک ٹاپک سے متعدد سبسکرائبرز پڑھ سکتے ہیں (مثلاً، ایک لاگر اور ایک وژن الگوری دیم کو ایک ساتھ کیمرے کا ڈیٹا استعمال کرتے ہیں)۔

**ٹاپکس غیر ہم وقتہ ہیں**: شائع کار سبسکرائبرز کا انتظار نہیں کرتے ہیں۔ اگر کوئی سبسکرائبرز موجود نہیں ہیں، تو پیغامات کو مسترد کر دیا جاتا ہے۔ یہ وقت- critical کنٹرول لوپس میں بلاکنگ کو روکتا ہے۔

## rclpy کے ساتھ پائیتھن نوڈس تخلیق کرنا

`rclpy` لائبریری ROS 2 کے لئے پائیتھن بائنڈنگ فراہم کرتی ہے۔ آئیں ایک مکمل مثال بناتے ہیں: ایک نوڈ جو ہیومنوائڈ روبوٹ کے لئے جوائنٹ اینگل کمانڈز شائع کرتا ہے۔

### شائع کار نوڈ: جوائنٹ کمانڈ شائع کار

```python
#!/usr/bin/env python3
"""
ہیومنوائڈ روبوٹ کے لئے جوائنٹ کمانڈ شائع کار۔
شولڈر، البو، ہپ، اور نی جوائنٹس کے لئے ہدف کے اینگلز شائع کرتا ہے۔
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import math

class JointCommandPublisher(Node):
    """
    جوائنٹ کمانڈز کو م_PERIODIC طور پر شائع کرتا ہے تاکہ بازو کی حرکت کو شبیہہ کیا جا سکے۔
    """

    def __init__(self):
        # نام 'joint_command_publisher' کے ساتھ نوڈ کو شروع کریں
        super().__init__('joint_command_publisher')

        # /joint_commands ٹاپک پر شائع کار تخلیق کریں
        # 10 کی قطار کا سائز 10 پیغامات کو ذخیرہ کرتا ہے اگر سبسکرائبر پیچھے نہیں رہ سکتا
        self.publisher_ = self.create_publisher(
            JointState,
            '/joint_commands',
            10
        )

        # 10 Hz (100ms دورانیہ) پر شائع کرنے کے لئے ٹائمر تخلیق کریں
        # ہیومنوائڈ کنٹرول عام طور پر 100-1000 Hz پر چلتا ہے؛ 10 Hz نمائش کے لئے ہے
        timer_period = 0.1  # سیکنڈز
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # سنوسوڈل موشن کے لئے وقت ٹریک کریں
        self.time_step = 0

        # ہیومنوائڈ بازو کے لئے جوائنٹ نامزد کریں (URDF کنونشن سے مماثل)
        self.joint_names = [
            'left_shoulder_pitch',
            'left_shoulder_roll',
            'left_elbow',
            'right_shoulder_pitch',
            'right_shoulder_roll',
            'right_elbow'
        ]

        self.get_logger().info('جوائنٹ کمانڈ شائع کار شروع ہوا')

    def timer_callback(self):
        """
        ہر 100ms میں کال کیا جاتا ہے تاکہ نئے جوائنٹ کمانڈز شائع کیے جا سکیں۔
        ہموار بازو کی حرکت کے لئے سنوسوڈل ٹریجیکٹریز تیار کرتا ہے۔
        """
        msg = JointState()

        # ہیڈر کو ٹائم اسٹیمپ کے ساتھ پُر کریں (سینسر ڈیٹا کے لئے ضروری)
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        # جوائنٹ نامزد سیٹ کریں
        msg.name = self.joint_names

        # سنوسوڈل جوائنٹ اینگلز تیار کریں (ریڈینز میں)
        # 0.5 rad کی ایمپلی ٹیوڈ ≈ 28 ڈگری محفوظ حرکت کی حد فراہم کرتی ہے
        msg.position = [
            0.5 * math.sin(self.time_step),      # بائیں شولڈر پچ: آگے/پیچھے
            0.3 * math.cos(self.time_step),      # بائیں شولڈر رول: طرفین
            0.8 * math.sin(self.time_step * 2),  # بائیں البو: تیزی سے مڑنا/پھیلنا
            -0.5 * math.sin(self.time_step),     # دائیں شولڈر: بائیں کے مطابق
            -0.3 * math.cos(self.time_step),
            -0.8 * math.sin(self.time_step * 2)
        ]

        # رفتار (rad/s) - عام طور پر پوزیشن ڈیریویٹیوز سے حساب کیا جاتا ہے
        # نمائش کے لئے، صفر پر سیٹ کریں (پوزیشن کنٹرول موڈ)
        msg.velocity = [0.0] * len(self.joint_names)

        # ایفروٹ (Nm میں ٹورک) - پوزیشن کنٹرول میں استعمال نہیں ہوتا
        msg.effort = []

        # پیغام شائع کریں
        self.publisher_.publish(msg)

        # ہر 1 سیکنڈ (10 پیغامات) میں لاگ
        if self.time_step % 10 < 0.1:
            self.get_logger().info(f't={self.time_step:.1f}s پر جوائنٹ کمانڈز شائع کیے گئے')

        # اگلے اٹریشن کے لئے وقت میں اضافہ کریں
        self.time_step += 0.1

def main(args=None):
    # rclpy لائبریری کو شروع کریں
    rclpy.init(args=args)

    # نوڈ کا مثالی انسٹانس تخلیق کریں
    node = JointCommandPublisher()

    try:
        # کال بیکس کو پروسیس کرنے کے لئے نوڈ کو چلائیں (Ctrl+C تک چلتا رہتا ہے)
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Ctrl+C پر گریس فل شٹ ڈاؤن
        node.get_logger().info('جوائنٹ کمانڈ شائع کار کو بند کیا جا رہا ہے')
    finally:
        # وسائل کو صاف کریں
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### سبسکرائبر نوڈ: جوائنٹ اسٹیٹ مانیٹر

```python
#!/usr/bin/env python3
"""
ہیومنوائڈ روبوٹ کے لئے جوائنٹ اسٹیٹ مانیٹر۔
جوائنٹ کمانڈز کو سبسکرائب کرتا ہے اور موجودہ پوزیشنز کو لاگ کرتا ہے۔
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class JointStateMonitor(Node):
    """
    جوائنٹ کمانڈز کو مانیٹر کرتا ہے اور ممکنہ سیفٹی کی خلاف ورزیوں کو تلاش کرتا ہے۔
    """

    def __init__(self):
        super().__init__('joint_state_monitor')

        # /joint_commands ٹاپک کے لئے سبسکرپشن تخلیق کریں
        # QoS گہرائی شائع کار سے مماثل ہے
        self.subscription = self.create_subscription(
            JointState,
            '/joint_commands',
            self.listener_callback,
            10
        )

        # سیفٹی چیکنگ کے لئے جوائنٹ حدود کی وضاحت کریں (ریڈینز میں)
        # پیداوار میں، یہ URDF یا کنفیگ فائل سے آئیں گے
        self.joint_limits = {
            'left_shoulder_pitch': (-1.57, 1.57),   # ±90 ڈگری
            'left_shoulder_roll': (-0.785, 0.785),  # ±45 ڈگری
            'left_elbow': (0.0, 2.356),             # 0 سے 135 ڈگری
            'right_shoulder_pitch': (-1.57, 1.57),
            'right_shoulder_roll': (-0.785, 0.785),
            'right_elbow': (0.0, 2.356)
        }

        self.get_logger().info('جوائنٹ اسٹیٹ مانیٹر شروع ہوا')

    def listener_callback(self, msg):
        """
        /joint_commands پر کوئی پیغام شائع ہونے پر خودکار طور پر کال کیا جاتا ہے۔

        آرگس:
            msg (JointState): موصول شدہ جوائنٹ اسٹیٹ پیغام
        """
        # سیفٹی کی خلاف ورزیوں کے لئے چیک کریں
        for i, joint_name in enumerate(msg.name):
            if joint_name in self.joint_limits:
                position = msg.position[i]
                min_limit, max_limit = self.joint_limits[joint_name]

                if position < min_limit or position > max_limit:
                    self.get_logger().warning(
                        f'سیفٹی: {joint_name} at {position:.3f} rad '
                        f'حدوں [{min_limit:.3f}, {max_limit:.3f}] سے تجاوز کر رہا ہے'
                    )

        # موصول شدہ ڈیٹا لاگ کریں (اسپیم سے بچنے کے لئے تھروٹل کیا گیا)
        # پیداوار میں، ڈیٹا ریکارڈر یا ڈیش بورڈ پر بھیج دیا جائے گا
        if len(msg.position) > 0:
            self.get_logger().info(
                f'وصول ہوا: {len(msg.position)} جوائنٹس، '
                f'پہلا پوزیشن: {msg.position[0]:.3f} rad'
            )

def main(args=None):
    rclpy.init(args=args)
    node = JointStateMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('جوائنٹ اسٹیٹ مانیٹر کو بند کیا جا رہا ہے')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## مثال چلانا

### قدم 1: نوڈس کو پیکج میں شامل کریں

شائع کار کو `humanoid_ws/src/humanoid_control/humanoid_control/joint_publisher.py` کے بطور محفوظ کریں اور سبسکرائبر کو `joint_monitor.py` کے بطور محفوظ کریں۔ `setup.py` کو اپ ڈیٹ کریں:

```python
entry_points={
    'console_scripts': [
        'joint_publisher = humanoid_control.joint_publisher:main',
        'joint_monitor = humanoid_control.joint_monitor:main',
    ],
},
```

### قدم 2: تعمیر اور چلانا

```bash
# ورک سپیس تعمیر کریں
cd ~/humanoid_ws
colcon build --symlink-install
source install/setup.bash

# ٹرمنل 1: شائع کار شروع کریں
ros2 run humanoid_control joint_publisher

# ٹرمنل 2: مانیٹر شروع کریں (نئے ٹرمنل میں، ذریعہ کے بعد)
ros2 run humanoid_control joint_monitor

# ٹرمنل 3: رابطہ کی تحقیق کریں
ros2 topic hz /joint_commands  # ~10 Hz دکھانا چاہیے
ros2 topic echo /joint_commands  # خام پیغامات دیکھیں
```

## ٹرٹل سیم مثال: ٹاپکس کو دیکھنا

ٹرٹل سیم pub-sub رابطے کا بصری مظاہرہ فراہم کرتا ہے۔ ٹرٹل کا پوزیشن `/turtle1/cmd_vel` ٹاپک کے ذریعے کنٹرول کیا جاتا ہے۔

```bash
# ٹرٹل سیم نوڈ شروع کریں
ros2 run turtlesim turtlesim_node

# نئے ٹرمنل میں: رفتار کمانڈز شائع کریں
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.0}}"

# ٹرٹل کو چکر میں حرکت کرتے دیکھیں (2 m/s آگے، 1 rad/s گردش)
```

ایک حسب ضرورت کنٹرولر تخلیق کریں:

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
        # سرپل پیٹرن بنانے کے لئے لکیری رفتار کو متغیر بنائیں
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

## پیغام کی اقسام کا گہرا جائزہ

**sensor_msgs/msg/JointState**: روبوٹ جوائنٹ ڈیٹا کے لئے معیاری پیغام
- `header`: ٹائم اسٹیمپ اور کوآرڈینیٹ فریم
- `name[]`: جوائنٹ شناخت کار (URDF سے مماثل ہونا چاہیے)
- `position[]`: اینگلز (rad) یا جگہیں (m)
- `velocity[]`: اینگولر یا لکیری رفتاریں
- `effort[]`: ٹورکس (Nm) یا قوتیں (N)

**geometry_msgs/msg/Twist**: موبائل روبوٹس کے لئے رفتار کمانڈ
- `linear`: x، y، z میں رفتار (m/s)
- `angular`: x، y، z کے گرد گردش (rad/s)

استعمال سے پہلے ہمیشہ `ros2 interface show <msg_type>` کے ساتھ پیغام کی تعریف چیک کریں۔

## اگلے اقدامات

آپ اب ٹاپک-بیسڈ رابطے کو سمجھتے ہیں اور شائع کار اور سبسکرائبرز تخلیق کر سکتے ہیں۔ اگلے باب **سروسز اور ایکشنز** کو کور کرتا ہے درخواست-جواب نمونے اور طویل مدتی کاموں کے لئے— زیادہ سطحی روبوٹ کے رویوں کے لئے ضروری جیسے "کھڑے ہو جاؤ" یا "آبجیکٹ تھامو"۔

### مشق ورزش

جوائنٹ مانیٹر کو وسعت دیں تاکہ جوائنٹ رفتاریں حساب کریں اور شائع کریں:
1. `/joint_commands` کو سبسکرائب کریں
2. رفتار کو (موجودہ_پوزیشن - گزشتہ_پوزیشن) / dt کے بطور حساب کریں
3. نئے ٹاپک `/joint_velocities` پر شائع کریں
4. `rqt_plot /joint_velocities` کے ساتھ دیکھیں