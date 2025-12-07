# ہفتہ 10: بائی پیڈل لوکوموشن کنٹرول

## بائی پیڈل استحکام کا چیلنج

دو ٹانگوں پر چلنا بنیادی طور پر غیر مستحکم ہے۔ وہیلڈ روبوٹس کے مقابلے جن کے پاس سٹیٹک استحکام ہے (جب روکا جاتا ہے تو سیدھے رہتے ہیں)، ہیومنوائڈز کو **ڈائنامک طور پر توازن** برقرار رکھنا ہوتا ہے - گرنے سے بچنے کے لئے مستقل طور پر ایڈجسٹ کرنا۔

### کلیدی چیلنج

1. **چھوٹا سپورٹ پولی گون**: پاؤں کو وہیلڈ بیسز کے مقابلے میں کم سے کم رابطہ کا علاقہ فراہم کرتے ہیں
2. **اونچا مرکزی دھڑ**: ہیومنوائڈ ٹورسو لمبی ہے، بڑے ٹوپلنگ مومینٹس پیدا کرتی ہے
3. **انڈر ایکچو ایشن**: ڈگریز آف فریڈم کے مقابلے میں کم ایکچو ایٹرز (براہ راست تمام موشن کو کنٹرول نہیں کر سکتے)
4. **فیز ٹرانزیشنز**: سنگل لیگ اور ڈبل لیگ سپورٹ کے درمیان سوئچ کرنا منقطع ہے

## زیرو مومینٹ پوائنٹ (ZMP) معیار

**زیرو مومینٹ پوائنٹ** زمین پر وہ پوائنٹ ہے جہاں گریوی ٹیشنل اور ایเนشیل فورسز کا مجموعہ صفر مومینٹ (ٹورک) پیدا کرتا ہے۔ مستحکم چلنے کے لئے، ZMP کو **سپورٹ پولی گون** (پاؤں کے رابطہ پوائنٹس کا محدب ہل) کے اندر رہنا چاہیے۔

### ریاضیاتی تعریف

```python
import numpy as np

def compute_zmp(robot_state):
    """
    روبوٹ کی حالت سے زیرو مومینٹ پوائنٹ کا حساب لگائیں۔

    Args:
        robot_state: کیز کے ساتھ ڈکشنری:
            - 'com_pos': مرکزی ماس کی پوزیشن [x, y, z]
            - 'com_vel': مرکزی ماس کی رفتار [vx, vy, vz]
            - 'com_acc': مرکزی ماس کا ایکسیلریشن [ax, ay, az]
            - 'mass': کل روبوٹ کا ماس (kg)

    Returns:
        zmp: ZMP کے [x, y] کوآرڈینیٹس زمینی سطح پر
    """
    g = 9.81  # گریوی ٹیشنل ایکسیلریشن (m/s²)

    # حالت نکالیں
    x, y, z = robot_state['com_pos']
    vx, vy, vz = robot_state['com_vel']
    ax, ay, az = robot_state['com_acc']
    m = robot_state['mass']

    # ZMP ایکویشنز (یہ فرض کرتے ہوئے کہ زمین z=0 پر ہے)
    # ZMP_x = x - z * (ax + g*θ_y) / (az + g)
    # ZMP_y = y - z * (ay - g*θ_x) / (az + g)
    # چھوٹے زاویوں کے لئے سادہ:
    zmp_x = x - z * ax / (az + g)
    zmp_y = y - z * ay / (az + g)

    return np.array([zmp_x, zmp_y])

def is_stable(zmp, support_polygon):
    """
    چیک کریں کہ آیا ZMP سپورٹ پولی گون کے اندر ہے۔

    Args:
        zmp: [x, y] ZMP کوآرڈینیٹس
        support_polygon: [x, y] پوائنٹس کی فہرست جو پاؤں کے رابطے کی وضاحت کرتی ہے

    Returns:
        stable: صحیح اگر ZMP پولی گون کے اندر ہے (مستحکم)
    """
    from shapely.geometry import Point, Polygon

    zmp_point = Point(zmp)
    support = Polygon(support_polygon)

    return support.contains(zmp_point)

# مثال کا استعمال
robot_state = {
    'com_pos': [0.0, 0.0, 0.8],      # CoM 80cm اونچائی پر
    'com_vel': [0.3, 0.0, 0.0],      # 0.3 m/s کے ساتھ آگے کی طرف چل رہا ہے
    'com_acc': [0.1, 0.0, -0.5],     # آگے کی طرف ایکسیلریٹنگ
    'mass': 45.0                      # 45kg ہیومنوائڈ
}

zmp = compute_zmp(robot_state)
print(f"ZMP پوزیشن: ({zmp[0]:.3f}, {zmp[1]:.3f})")

# سنگل لیگ اسٹینس کے دوران سپورٹ پولی گون (رائٹ فُٹ)
right_foot_polygon = [
    [0.05, 0.05],   # فرنٹ رائٹ کونر
    [0.05, -0.05],  # فرنٹ لیفٹ کونر
    [-0.05, -0.05], # بیک لیفٹ کونر
    [-0.05, 0.05]   # بیک رائٹ کونر
]

stable = is_stable(zmp, right_foot_polygon)
print(f"روبوٹ {'مستحکم ہے' if stable else 'غیر مستحکم ہے'}")
```

## گیٹ جنریشن

**گیٹ** لیگ موشنز کا ایک منظم پیٹرن ہے۔ ہیومنوائڈ چلنا عام طور پر چار فیز والی م_PERIODIC گیٹ استعمال کرتا ہے:

1. **ڈبل سپورٹ**: دونوں پاؤں زمین پر (مستحکم لیکن سست)
2. **لیفٹ سوئنگ**: رائٹ فُٹ سپورٹ، لیفٹ فُٹ آگے کی طرف جاتا ہے
3. **ڈبل سپورٹ**: دونوں پاؤں زمین پر (ٹرانزیشن)
4. **رائٹ سوئنگ**: لیفٹ فُٹ سپورٹ، رائٹ فُٹ آگے کی طرف جاتا ہے

### سادہ گیٹ ٹریجکٹری جنریٹر

```python
import numpy as np

class BipedGaitGenerator:
    def __init__(self, step_length=0.15, step_height=0.05, step_duration=0.8):
        """
        بائی پیڈل گیٹ جنریٹر کا ابتدائی کریں۔

        Args:
            step_length: فی اسٹیپ آگے کی طرف فاصلہ (میٹر)
            step_height: زیادہ سے زیادہ فُٹ لفٹ اونچائی (میٹر)
            step_duration: ایک اسٹیپ کا وقت (سیکنڈ)
        """
        self.step_length = step_length
        self.step_height = step_height
        self.step_duration = step_duration
        self.double_support_ratio = 0.2  # اسٹیپ کا 20% ڈبل سپورٹ میں

    def generate_foot_trajectory(self, t, foot='left'):
        """
        سوئنگ فیز کے لئے فُٹ ٹریجکٹری تیار کریں۔

        Args:
            t: موجودہ اسٹیپ کے اندر وقت (0 سے اسٹیپ ڈوریشن تک)
            foot: 'left' یا 'right'

        Returns:
            foot_pos: [x, y, z] فُٹ کی پوزیشن
        """
        # وقت کو [0, 1] میں نارملائز کریں
        phase = t / self.step_duration

        # اسٹیپ کے آغاز اور اختتام پر ڈبل سپورٹ
        ds_time = self.double_support_ratio

        if phase < ds_time or phase > (1 - ds_time):
            # ڈبل سپورٹ - فُٹ زمین پر
            return self._stance_position(foot)
        else:
            # سوئنگ فیز - فُٹ ہوا میں
            swing_phase = (phase - ds_time) / (1 - 2*ds_time)  # [0, 1] میں نارملائز کریں

            # فارورڈ موشن (لکیری)
            x = self.step_length * swing_phase

            # لیٹرل آفسیٹ (پاؤں کو ہپ چوڑائی کے ذریعے الگ کیا گیا)
            y = 0.1 if foot == 'left' else -0.1

            # عمودی موشن (سMOOTH لفٹ/لینڈنگ کے لئے پیرابولک آرک)
            z = 4 * self.step_height * swing_phase * (1 - swing_phase)

            return np.array([x, y, z])

    def _stance_position(self, foot):
        """اسٹینس فیز کے دوران فُٹ کی پوزیشن واپس کریں۔"""
        y = 0.1 if foot == 'left' else -0.1
        return np.array([0.0, y, 0.0])

    def generate_com_trajectory(self, t, num_steps):
        """
        مرکزی ماس ٹریجکٹری تیار کریں۔
        سنگل سپورٹ کے دوران CoM سپورٹ فُٹ کے ارد گرد لیٹرلی شفٹ ہوتا ہے۔

        Args:
            t: موجودہ وقت
            num_steps: منصوبہ بند کردہ اسٹیپس کی تعداد

        Returns:
            com_pos: [x, y, z] CoM پوزیشن
        """
        # فارورڈ رفتار
        vx = self.step_length / self.step_duration
        com_x = vx * t

        # لیٹرل شفٹ (بائیں اور دائیں کے درمیان آسیلیٹ)
        step_index = int(t / self.step_duration)
        phase = (t % self.step_duration) / self.step_duration

        # CoM کو سپورٹ فُٹ پر شفٹ کریں
        if step_index % 2 == 0:
            # رائٹ فُٹ سپورٹ - CoM کو دائیں طرف شفٹ کریں
            com_y = -0.05 * np.sin(np.pi * phase)
        else:
            # لیفٹ فُٹ سپورٹ - CoM کو بائیں طرف شفٹ کریں
            com_y = 0.05 * np.sin(np.pi * phase)

        # مستقل اونچائی (سادہ)
        com_z = 0.8

        return np.array([com_x, com_y, com_z])

# استعمال کی مثال
gait = BipedGaitGenerator(step_length=0.15, step_height=0.05, step_duration=0.8)

# ایک اسٹیپ کی سیمولیشن
dt = 0.01  # 100 Hz کنٹرول
for t in np.arange(0, 0.8, dt):
    left_foot = gait.generate_foot_trajectory(t, foot='left')
    right_foot = gait.generate_foot_trajectory(t, foot='right')
    com = gait.generate_com_trajectory(t, num_steps=5)

    # حقیقی امپلیمنٹیشن میں، ان کو ان ورس کنیمیٹکس میں بھیجا جائے گا
    # جوائنٹ اینگلز کا حساب لگانے کے لئے
    if int(t / dt) % 10 == 0:  # ہر 0.1s میں پرنٹ کریں
        print(f"t={t:.2f}s  CoM: {com}  L_foot: {left_foot}  R_foot: {right_foot}")
```

## توازن کنٹرول

توازن برقرار رکھنے کے لئے رکاوٹوں کی اصلاح کے لئے **ریل ٹائم فیڈ بیک کنٹرول** کی ضرورت ہوتی ہے۔

### PID توازن کنٹرولر

```python
class ZMPBalanceController:
    def __init__(self, kp=0.5, ki=0.01, kd=0.1):
        """
        ZMP کو سپورٹ پولی گون کے اندر رکھنے کے لئے PID کنٹرولر۔

        Args:
            kp, ki, kd: پوزیشن، انٹیگرل، ڈیرویٹیو کنٹرول کے لئے PID گینز
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd

        # کنٹرولر کی حالت
        self.zmp_error_integral = np.zeros(2)
        self.prev_zmp_error = np.zeros(2)

    def compute_correction(self, desired_zmp, actual_zmp, dt):
        """
        CoM ایکسیلریشن کی اصلاح کا حساب لگائیں تاکہ مطلوبہ ZMP حاصل کیا جا سکے۔

        Args:
            desired_zmp: ٹارگیٹ ZMP پوزیشن [x, y]
            actual_zmp: موجودہ ZMP پوزیشن [x, y]
            dt: ٹائم اسٹیپ (سیکنڈ)
        Returns:
            com_acc_correction: [ax, ay] CoM ایکسیلریشن میں شامل کرنے کے لئے
        """
        # ZMP خامی
        zmp_error = desired_zmp - actual_zmp

        # انٹیگرل اپ ڈیٹ کریں
        self.zmp_error_integral += zmp_error * dt

        # ڈیرویٹیو کا حساب لگائیں
        zmp_error_derivative = (zmp_error - self.prev_zmp_error) / dt
        self.prev_zmp_error = zmp_error

        # PID کنٹرول لاء
        correction = (
            self.kp * zmp_error +
            self.ki * self.zmp_error_integral +
            self.kd * zmp_error_derivative
        )

        return correction

# کنٹرول لوپ میں استعمال
controller = ZMPBalanceController(kp=0.5, ki=0.01, kd=0.1)

# سیمولیٹڈ کنٹرول لوپ
dt = 0.01
desired_zmp = np.array([0.0, 0.0])  # ZMP کو فُٹ کے مرکز پر رکھیں

for i in range(100):
    # موجودہ حالت ماپیں
    actual_zmp = compute_zmp(robot_state)

    # اصلاح کا حساب لگائیں
    com_acc_correction = controller.compute_correction(desired_zmp, actual_zmp, dt)

    # CoM ایکسیلریشن میں اصلاح شامل کریں
    robot_state['com_acc'][:2] += com_acc_correction

    # روبوٹ کی حالت اپ ڈیٹ کریں (سادہ ڈائنامکس)
    robot_state['com_vel'] += robot_state['com_acc'] * dt
    robot_state['com_pos'] += robot_state['com_vel'] * dt

    if i % 10 == 0:
        print(f"ZMP خامی: {np.linalg.norm(desired_zmp - actual_zmp):.4f}m")
```

## Nav2 کے ساتھ انضمام

Nav2 نیوی گیشن سے بائی پیڈل لوکوموشن کو جوڑنے کے لئے ایک **رفتار کمانڈ انٹرپریٹر** کی ضرورت ہوتی ہے جو Nav2 کی کمانڈ کردہ رفتاروں کو گیٹ پیرامیٹرز میں تبدیل کرتا ہے:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray

class BipedalLocomotionNode(Node):
    def __init__(self):
        super().__init__('bipedal_locomotion')

        # Nav2 رفتار کمانڈز کے لئے سبسکرائب کریں
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.velocity_callback,
            10
        )

        # روبوٹ کو جوائنٹ کمانڈز شائع کریں
        self.joint_pub = self.create_publisher(
            Float64MultiArray,
            '/joint_commands',
            10
        )

        # گیٹ جنریٹر
        self.gait = BipedGaitGenerator()
        self.controller = ZMPBalanceController()

        # 100 Hz پر کنٹرول لوپ
        self.timer = self.create_timer(0.01, self.control_loop)

        self.target_vx = 0.0
        self.target_vy = 0.0
        self.target_omega = 0.0
        self.time = 0.0

    def velocity_callback(self, msg):
        """Nav2 سے رفتار کمانڈز وصول کریں۔"""
        self.target_vx = msg.linear.x
        self.target_vy = msg.linear.y
        self.target_omega = msg.angular.z

        # کمانڈ کردہ رفتار کے مطابق گیٹ پیرامیٹرز ایڈجسٹ کریں
        self.gait.step_length = self.target_vx * self.gait.step_duration
        self.gait.step_length = np.clip(self.gait.step_length, 0.0, 0.3)  # زیادہ سے زیادہ 30cm اسٹیپس

    def control_loop(self):
        """100 Hz پر گیٹ اور توازن کنٹرول تیار کریں۔"""
        # مطلوبہ فُٹ اور CoM پوزیشنز تیار کریں
        left_foot = self.gait.generate_foot_trajectory(self.time, 'left')
        right_foot = self.gait.generate_foot_trajectory(self.time, 'right')
        com_ref = self.gait.generate_com_trajectory(self.time, num_steps=5)

        # توازن کنٹرول (سادہ - حقیقی امپلیمنٹیشن کو مکمل حالت کی ضرورت ہوگی)
        desired_zmp = np.array([0.0, 0.0])  # سپورٹ فُٹ کا مرکز
        actual_zmp = np.array([0.0, 0.0])   # سینسرز سے آئے گا
        com_correction = self.controller.compute_correction(desired_zmp, actual_zmp, 0.01)

        # TODO: فُٹ/CoM پوزیشنز کو جوائنٹ اینگلز میں تبدیل کرنے کے لئے ان ورس کنیمیٹکس
        # joint_angles = inverse_kinematics(left_foot, right_foot, com_ref)

        # جوائنٹ کمانڈز شائع کریں
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

## ورزشیں

1. **ZMP تجزیہ**: CoM کے مختلف لیٹرل پوزیشنز پر اسٹیشنری ہیومنوائڈ کے لئے ZMP کا حساب لگائیں۔ استحکام کی حد کی شناخت کریں۔

2. **گیٹ وژوئلائزیشن**: 5 اسٹیپس پر فُٹ اور CoM ٹریجکٹریز کو پلاٹ کرنے کے لئے matplotlib استعمال کریں۔ تصدیق کریں کہ CoM سپورٹ فُٹ کے اوپر مناسب طریقے سے شفٹ ہوتا ہے۔

3. **PID ٹیوننگ**: ZMP توازن کنٹرولر امپلیمنٹ کریں اور سیٹلنگ ٹائم کو کم کرنے کے لئے PID گینز ٹیون کریں جبکہ آسیلیشنز سے بچا جائے۔

4. **Nav2 انضمام**: اپنے گیٹ جنریٹر کو Nav2 رفتار کمانڈز سے منسلک کریں۔ سیمولیشن میں ویپوائنٹس تک نیوی گیشن کا ٹیسٹ کریں۔

---

**مبارک ہو!** آپ نے موڈیول 3: NVIDIA Isaac پلیٹ فارم مکمل کر لیا ہے۔ آپ اب GPU-ایکسلریٹڈ سیمولیشن، سینتھیٹک ڈیٹا جنریشن، ہارڈ ویئر-ایکسلریٹڈ ادراک، اور بائی پیڈل لوکوموشن کنٹرول کو سمجھتے ہیں - اگلی نسل کے ہیومنوائڈ روبوٹس کو فعال کرنے والی کلیدی ٹیکنالوجیز۔

**اگلا موڈیول**: [موڈیول 4 - وژن-لینگویج-ایکشن ماڈلز](../module-04-vla/intro.md)