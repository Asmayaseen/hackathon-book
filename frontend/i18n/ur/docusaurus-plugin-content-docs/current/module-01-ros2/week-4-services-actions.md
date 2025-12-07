# ہفتہ 4: سروسز اور ایکشنز

![Services and Actions](/img/ai-6.png)

## سروس کلائنٹ-سرور نمونہ

جبکہ ٹاپکس جاری ڈیٹا سٹریمنگ کو فعال کرتے ہیں، کئی روبوٹ کے کاموں کو درخواست-جواب کے تعاملات کی ضرورت ہوتی ہے۔ سروسز مطابقت پذیر RPC (ریموٹ کارروائی کال) سیمنٹکس فراہم کرتے ہیں: ایک کلائنٹ ایک درخواست بھیجتا ہے اور سرور سے جواب ملنے تک بلاک ہو جاتا ہے۔

### سروسز کب استعمال کریں

سروسز کے لئے بہترین ہیں:
- **کم تعدد کے سوالات**: ہدف کی پوز کے لئے معکوس کنیمیٹکس کا حساب لگانا
- **کنفیگریشن میں تبدیلیاں**: کنٹرولر گینز سیٹ کرنا یا آپریشنل موڈز سوئچ کرنا
- **اسٹیٹ کے سوالات**: موجودہ بیٹری کی سطح یا سسٹم کے تشخیص کی درخواست
- **اٹومک کام**: کیلیبریشن کی ترتیبات کو متحرک کرنا جو واپسی سے پہلے مکمل ہونا لازمی ہے

**اہم فرق**: سروسز کالنگ نوڈ کو مکمل ہونے تک بلاک کر دیتے ہیں۔ 1 سیکنڈ سے زیادہ وقت لینے والے کاموں کے لئے کبھی بھی سروسز استعمال نہ کریں— اس کے بجائے ایکشنز استعمال کریں (ذیل میں دیکھیں)۔

### سروس قسم کی ا Anatomy

سروسز ایک درخواست پیغام اور ایک جواب پیغام پر مشتمل ہوتے ہیں۔ مثال: `AddTwoInts.srv`

```
# درخواست
int64 a
int64 b
---
# جواب
int64 sum
```

`---` الگ کرنے والا درخواست اور جواب کو الگ کرتا ہے۔ ہیومنوائڈ روبوٹکس کے لئے، عام سروس کی اقسام میں شامل ہیں:
- `SetBool`: ایک کنٹرولر کو فعال/غیر فعال کرنا
- `Trigger`: کیلیبریشن یا ہومنگ شروع کرنا
- `GetPose`: اینڈ-ایفیکٹر کی پوزیشن کی درخواست

## سروس سرور مثال: معکوس کنیمیٹکس کیلکولیٹر

یہ سرور ہیومنوائڈ کے ہاتھ کو ہدف کے مقام پر رکھنے کے لئے درکار جوائنٹ اینگلز کا حساب لگاتا ہے— مینوپولیشن کاموں کے لئے ایک بنیادی کارروائی۔

```python
#!/usr/bin/env python3
"""
ہیومنوائڈ بازو کے لئے معکوس کنیمیٹکس سروس۔
ہدف کے اینڈ-ایفیکٹر کی پوز کو حاصل کرنے کے لئے جوائنٹ اینگلز کا حساب لگاتا ہے۔
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.srv import GetPlan
from geometry_msgs.msg import Pose, Point, Quaternion
from sensor_msgs.msg import JointState
import math

class IKService(Node):
    """
    سروس کے بطور معکوس کنیمیٹکس حل فراہم کرتا ہے۔
    نمائش کے لئے سادہ 2-DOF بازو۔
    """

    def __init__(self):
        super().__init__('ik_service')

        # /compute_ik ٹاپک پر سروس سرور تخلیق کریں
        # سروس قسم: پیکج میں وضاحت شدہ کسٹم پیغام
        self.srv = self.create_service(
            GetPlan,  # نمائش کے لئے موجودہ قسم کو دوبارہ استعمال کرنا
            'compute_ik',
            self.compute_ik_callback
        )

        # بازو کے پیرامیٹرز (میٹرز)
        self.upper_arm_length = 0.3  # شولڈر سے البو
        self.forearm_length = 0.25   # البو سے wrist

        self.get_logger().info('IK سروس تیار')

    def compute_ik_callback(self, request, response):
        """
        2-DOF پلینر بازو کے لئے معکوس کنیمیٹکس حل کریں۔

        آرگس:
            request: ہدف کی پوز (پوزیشن اور اورینٹیشن) پر مشتمل ہے
            response: جوائنٹ اینگلز کے ساتھ پُر کیا گیا ہے

        واپسی کرتا ہے:
            response: تبدیل شدہ جواب آبجیکٹ (ROS 2 کنونشن)
        """
        # درخواست سے ہدف کی پوزیشن نکالیں
        target_x = request.goal.pose.position.x
        target_y = request.goal.pose.position.y

        self.get_logger().info(f'IK درخواست: ہدف=({target_x:.3f}, {target_y:.3f})')

        # ہدف تک فاصلہ کا حساب لگائیں
        distance = math.sqrt(target_x**2 + target_y**2)

        # چیک کریں کہ ہدف قابل رسائی ہے
        max_reach = self.upper_arm_length + self.forearm_length
        min_reach = abs(self.upper_arm_length - self.forearm_length)

        if distance > max_reach or distance < min_reach:
            self.get_logger().error(
                f'ہدف قابل رسائی نہیں: فاصلہ={distance:.3f}م، '
                f'درست حد=[{min_reach:.3f}, {max_reach:.3f}]'
            )
            # ناکامی کی نشاندہی کے لئے خالی جواب واپس کریں
            return response

        # کوسائنز کے قانون کا استعمال کرکے کوہنہ کا اینگل کا حساب لگائیں
        # c² = a² + b² - 2ab*cos(C)
        cos_elbow = (
            (target_x**2 + target_y**2 -
             self.upper_arm_length**2 - self.forearm_length**2) /
            (2 * self.upper_arm_length * self.forearm_length)
        )

        # [-1, 1] تک محدود کریں تاکہ عددی خامیوں سے بچا جا سکے
        cos_elbow = max(-1.0, min(1.0, cos_elbow))
        elbow_angle = math.acos(cos_elbow)

        # شولڈر اینگل کا حساب لگائیں
        alpha = math.atan2(target_y, target_x)
        beta = math.atan2(
            self.forearm_length * math.sin(elbow_angle),
            self.upper_arm_length + self.forearm_length * math.cos(elbow_angle)
        )
        shoulder_angle = alpha - beta

        # جواب کو پُر کریں (پیداوار میں، JointState پیغام واپس کریں)
        self.get_logger().info(
            f'IK حل: شولڈر={math.degrees(shoulder_angle):.1f}°، '
            f'البو={math.degrees(elbow_angle):.1f}°'
        )

        # نمائش کے لئے، اینگلز کو جواب میں کوڈ کریں
        # حقیقی امپلیمنٹیشن میں، JointState جواب کے ساتھ کسٹم سروس قسم کی وضاحت کریں
        response.plan.poses = []  # جگہ دار

        return response

def main(args=None):
    rclpy.init(args=args)
    node = IKService()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('IK سروس کو بند کیا جا رہا ہے')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## سروس کلائنٹ مثال

```python
#!/usr/bin/env python3
"""
کلائنٹ جو معکوس کنیمیٹکس حل کی درخواست کرتا ہے۔
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.srv import GetPlan
from geometry_msgs.msg import PoseStamped, Point

class IKClient(Node):
    def __init__(self):
        super().__init__('ik_client')

        # سروس کلائنٹ تخلیق کریں
        self.client = self.create_client(GetPlan, 'compute_ik')

        # سروس دستیاب ہونے تک انتظار کریں (5 سیکنڈ ٹائم آؤٹ کے ساتھ)
        self.get_logger().info('IK سروس کا انتظار...')
        if not self.client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('IK سروس دستیاب نہیں ہے')
            return

        self.get_logger().info('IK سروس منسلک ہو گئی')

    def send_request(self, x, y):
        """
        ہدف کی پوزیشن کے لئے IK درخواست بھیجیں۔

        آرگس:
            x (float): ہدف x کوآرڈینیٹ (میٹرز)
            y (float): ہدف y کوآرڈینیٹ (میٹرز)
        """
        # درخواست پیغام تخلیق کریں
        request = GetPlan.Request()
        request.goal = PoseStamped()
        request.goal.pose.position = Point(x=x, y=y, z=0.0)

        # درخواست بے لاگ ان طور پر بھیجیں (غیر-بلاکنگ)
        future = self.client.call_async(request)

        # جب جواب آئے تو کال بیک رجسٹر کریں
        future.add_done_callback(self.handle_response)

    def handle_response(self, future):
        """
        جب سروس جواب موصول ہو تو کال کیا جاتا ہے۔

        آرگس:
            future: جواب پر مشتمل فیوچر آبجیکٹ
        """
        try:
            response = future.result()
            self.get_logger().info('IK حل موصول ہوا')
            # response.plan ڈیٹا یہاں پروسیس کریں
        except Exception as e:
            self.get_logger().error(f'سروس کال ناکام: {e}')

def main(args=None):
    rclpy.init(args=args)
    client = IKClient()

    # پوزیشن (0.4, 0.3) کے لئے IK کی درخواست کریں
    client.send_request(0.4, 0.3)

    # کال بیکس پروسیس کرنے کے لئے چلائیں
    rclpy.spin(client)

if __name__ == '__main__':
    main()
```

## ایکشن سرورز: طویل مدتی کام

ایکشنز ان کاموں کے لئے سروسز کو توسیع دیتے ہیں جن میں کافی وقت (سیکنڈز سے منٹس) لگتا ہے اور پیش رفت کی فیڈ بیک کی ضرورت ہوتی ہے۔ مثالیں شامل ہیں:
- ایک منزل تک چلنا (باقی فاصلہ کی رپورٹ)
- ایک آبجیکٹ کو تھامنا (Approach کے دوران کانٹیکٹ فورسز کی رپورٹ)
- کھڑے ہونے کی ترتیب (ہر مرحلے کی مکمل ہونے کی رپورٹ)

### ایکشن کی ساخت

ایکشنز میں تین اجزاء ہیں:
1. **Goal**: درخواست پیغام (مثلاً، چلنے کے لئے ہدف کی پوزیشن)
2. **Result**: حتمی نتیجہ (مثلاً، کامیابی/ناکامی، حتمی پوز)
3. **Feedback**: مکرر ترقی کی اپ ڈیٹس (مثلاً، ہدف تک موجودہ فاصلہ)

ایکشنز میں **منسوخی** کی بھی حمایت ہے— اس وقت اہم جب ہیومنوائڈ کو حرکت کو مکمل کرنا ہوتا ہے۔

## ایکشن سرور مثال: پوزیشن پر چلنا

```python
#!/usr/bin/env python3
"""
ہیومنوائڈ چلنے کے لئے ایکشن سرور۔
پیش رفت کی فیڈ بیک کے ساتھ چلنا کمانڈز کو انجام دیتے ہیں۔
"""

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from action_msgs.msg import GoalStatus
# پیداوار میں، کسٹم ایکشن کی وضاحت کریں: WalkToPosition.action
# ڈیمو کے لئے، مثال ایکشن قسم کا استعمال
from example_interfaces.action import Fibonacci
import time

class WalkActionServer(Node):
    """
    طویل مدتی ایکشنز کے بطور چلنے کی حرکات کو انجام دیتے ہیں۔
    """

    def __init__(self):
        super().__init__('walk_action_server')

        # ایکشن سرور تخلیق کریں
        self._action_server = ActionServer(
            self,
            Fibonacci,  # کسٹم WalkToPosition ایکشن کو تبدیل کریں
            'walk_to_position',
            self.execute_callback
        )

        # چلنے کے پیرامیٹرز
        self.walking_speed = 0.5  # m/s

        self.get_logger().info('Walk ایکشن سرور شروع ہوا')

    def execute_callback(self, goal_handle):
        """
        چلنے کا ایکشن انجام دیں۔

        آرگس:
            goal_handle: ایکشن انجام دہی کو منظم کرنے کا ہینڈل

        واپسی کرتا ہے:
            نتیجہ پیغام
        """
        self.get_logger().info('چلنے کا ایکشن انجام دیا جا رہا ہے')

        # ہدف نکالیں (حقیقی ایکشن میں، یہ ہدف پوز ہوگا)
        target_distance = 2.0  # میٹرز
        steps_required = int(target_distance / self.walking_speed)

        # فیڈ بیک پیغام تخلیق کریں
        feedback_msg = Fibonacci.Feedback()

        # مکرر فیڈ بیک کے ساتھ چلنے کی شبیہہ
        for step in range(steps_required):
            # چیک کریں کہ منسوخی کی درخواست ہے
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Walk ایکشن منسوخ ہو گیا')
                return Fibonacci.Result()

            # پیش رفت کا حساب لگائیں
            distance_covered = step * self.walking_speed
            distance_remaining = target_distance - distance_covered

            # فیڈ بیک شائع کریں (حقیقی امپلیمنٹیشن میں، موجودہ پوز شامل کریں)
            feedback_msg.sequence = [int(distance_covered * 100), int(distance_remaining * 100)]
            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f'چلنا: {distance_covered:.2f}م کا احاطہ، '
                f'{distance_remaining:.2f}م باقی'
            )

            # ایک سیکنڈ چلنے کی شبیہہ
            time.sleep(1.0)

        # ایکشن کو کامیاب کے بطور نشان لگائیں
        goal_handle.succeed()

        # نتیجہ واپس کریں
        result = Fibonacci.Result()
        result.sequence = [int(target_distance * 100)]
        self.get_logger().info(f'چلنا مکمل: {target_distance}م')

        return result

def main(args=None):
    rclpy.init(args=args)
    node = WalkActionServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Walk ایکشن سرور کو بند کیا جا رہا ہے')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## پیرامیٹرز اور ڈائنامک ری کنفیگر

پیرامیٹرز رن ٹائم کنفیگریشن کی اجازت دیتے ہیں بغیر نوڈس کو دوبارہ شروع کیے— ٹیسٹنگ کے دوران کنٹرولر گینز کو ٹیون کرنے کے لئے ضروری۔

```python
#!/usr/bin/env python3
"""
ROS 2 پیرامیٹر کے استعمال کا مظاہرہ کنٹرولر ٹیوننگ کے لئے۔
"""

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult

class BalanceController(Node):
    def __init__(self):
        super().__init__('balance_controller')

        # ڈیفالٹ اقدار کے ساتھ پیرامیٹرز کا اعلان کریں
        self.declare_parameter('kp_pitch', 50.0)   # pitch کے لئے م_PROPORATIONAL گین
        self.declare_parameter('kd_pitch', 10.0)   # DERIVATIVE گین
        self.declare_parameter('kp_roll', 50.0)
        self.declare_parameter('kd_roll', 10.0)
        self.declare_parameter('max_torque', 100.0)  # Nm

        # پیرامیٹر تبدیلیوں کے لئے کال بیک رجسٹر کریں
        self.add_on_set_parameters_callback(self.parameter_callback)

        # ابتدائی پیرامیٹر اقدار کو پڑھیں
        self.update_gains()

        self.get_logger().info(
            f'بیلنس کنٹرولر شروع کیا گیا: '
            f'kp_pitch={self.kp_pitch}, kd_pitch={self.kd_pitch}'
        )

    def update_gains(self):
        """موجودہ پیرامیٹر اقدار کو پڑھیں۔"""
        self.kp_pitch = self.get_parameter('kp_pitch').value
        self.kd_pitch = self.get_parameter('kd_pitch').value
        self.kp_roll = self.get_parameter('kp_roll').value
        self.kd_roll = self.get_parameter('kd_roll').value
        self.max_torque = self.get_parameter('max_torque').value

    def parameter_callback(self, params):
        """
        CLI یا سروس کے ذریعے پیرامیٹرز میں تبدیلی ہونے پر کال کیا جاتا ہے۔

        آرگس:
            params: تبدیل ہونے والے پیرامیٹرز کی فہرست

        واپسی کرتا ہے:
            SetParametersResult: کامیابی/ناکامی کی نشاندہی
        """
        for param in params:
            self.get_logger().info(f'پیرامیٹر میں تبدیلی: {param.name} = {param.value}')

        # اندرونی گینز کو اپ ڈیٹ کریں
        self.update_gains()

        # پیرامیٹرز کی توثیق کریں (مثال: گینز مثبت ہونا چاہیے)
        if self.kp_pitch < 0 or self.kd_pitch < 0:
            self.get_logger().error('گینز مثبت ہونا چاہیے')
            return SetParametersResult(successful=False)

        return SetParametersResult(successful=True)

def main(args=None):
    rclpy.init(args=args)
    node = BalanceController()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
```

### CLI سے پیرامیٹرز کا استعمال

```bash
# موجودہ پیرامیٹر اقدار حاصل کریں
ros2 param get /balance_controller kp_pitch

# نئی قدر سیٹ کریں (کال بیک متحرک کرتا ہے)
ros2 param set /balance_controller kp_pitch 75.0

# نوڈ کے لئے تمام پیرامیٹرز کی فہرست
ros2 param list /balance_controller

# YAML فائل میں پیرامیٹرز محفوظ کریں
ros2 param dump /balance_controller > controller_params.yaml

# فائل سے پیرامیٹرز اسٹارٹ اپ پر لوڈ کریں
ros2 run humanoid_control balance_controller --ros-args --params-file controller_params.yaml
```

## اگلے اقدامات

آپ اب درخواست-جواب کاموں کے لئے سروسز، فیڈ بیک کے ساتھ طویل مدتی کاموں کے لئے ایکشنز، اور رن ٹائم کنفیگریشن کے لئے پیرامیٹرز کو سمجھتے ہیں۔ اگلے باب، **ہفتہ 5: URDF**، روبوٹ کی ماڈلنگ متعارف کراتا ہے— سیمولیشن اور کنٹرول کے لئے ہیومنوائڈ روبوٹ کی کنیمیٹک ساخت کی وضاحت۔

### مشق ورزش

ایک ایکشن کلائنٹ تخلیق کریں جو:
1. ایکشن سرور کو چلنے کا ہدف بھیجے
2. ٹرمنل میں پیش رفت کی فیڈ بیک دکھائے
3. ایکشن منسوخ کرے اگر صارف 'q' دبا دے

اشارہ: `rclpy.action.ActionClient` استعمال کریں اور فیڈ بیک، نتیجہ، اور گوئل_ریسپانس کے لئے کال بیکس رجسٹر کریں۔