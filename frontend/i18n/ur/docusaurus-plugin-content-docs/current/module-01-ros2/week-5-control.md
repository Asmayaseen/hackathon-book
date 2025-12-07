# ہفتہ 5: ros2_control فریم ورک

## ros2_control کا تعارف

ros2_control فریم ورک ROS 2 میں روبوٹ کنٹرول سسٹم کے لئے ایک معیاری آرکیٹیکچر فراہم کرتا ہے۔ یہ کنٹرولر الگوری دھم کو ہارڈ ویئر-مخصوص کوڈ سے خوبصورتی سے وضاحت شدہ انٹرفیسز کے ذریعے الگ کرتا ہے، جس سے آپ کنٹرول کی حکمت عملی تیار کر سکتے ہیں جو سیمولیشن اور حقیقی روبوٹس دونوں میں بے داغ کام کرے۔

### ros2_control کیوں؟

**ہارڈ ویئر ایب سٹریکشن**: کنٹرولر کوڈ ایک بار لکھیں، مختلف ایکٹو ایٹر قسیم (سرو موٹرز، ہائیڈرولک ایکٹو ایٹرز، الیکٹرک موٹرز) پر ڈیپلائے کریں ہارڈ ویئر انٹرفیس پلگ انز کو تبدیل کر کے۔

**ریل ٹائم سیفٹی**: ros2_control کنٹرولرز کو مخصوص تھریڈز میں چلاتا ہے ریل ٹائم ترجیحات کے ساتھ، یہ یقینی بناتے ہوئے کہ تعیناتی انجام دہی— ہیومنوائڈ توازن کنٹرول کے لئے اہم جہاں تاخیر گرنے کا سبب بن سکتی ہے۔

**ایکو سسٹم انضمام**: MoveIt (موشن منصوبہ بندی)، Gazebo (سیمولیشن)، اور صنعتی روبوٹ ڈرائیورز کے ساتھ مطابقت رکھتا ہے۔ ہیومنوائڈ پروجیکٹس ثابت کنٹرولر امپلیمنٹیشنز کو دوبارہ استعمال کر کے فائدہ اٹھاتے ہیں۔

**اسٹیٹ مینجمنٹ**: کنٹرولرز کے لئے لائف سائیکل مینجمنٹ فراہم کرتا ہے (غیر فعال، فعال، ہنگامی_سٹاپ)، آپریشن کے دوران محفوظ موڈ ٹرانزیشن کو فعال کرتا ہے۔

## آرکیٹیکچر جائزہ

ros2_control تین اہم اجزاء پر مشتمل ہے:

### 1. ہارڈ ویئر انٹرفیس

کنٹرولر کمانڈز اور جسمانی/شبیہہ شدہ ہارڈ ویئر کے درمیان پل بناتا ہے۔ یہ وضاحت کرتا ہے کہ سینسر ڈیٹا (جوائنٹ انکوڈرز، فورس سینسرز) کیسے پڑھنا ہے اور ایکٹو ایٹر کمانڈز (موٹر وولٹیجز، پوزیشن سیٹ پوائنٹس) کیسے لکھنا ہے۔

**انٹرفیس کی اقسام**:
- `CommandInterface`: ہارڈ ویئر پر کمانڈز لکھیں (مثلاً، `position`, `velocity`, `effort`)
- `StateInterface`: سینسر ڈیٹا پڑھیں (مثلاً، `position`, `velocity`, `effort`)

### 2. کنٹرولر مینجر

کنٹرولر لائف سائیکل کا نظم کرتا ہے: لوڈ، کنفیگر، ایکٹیو، غیر فعال کرنا۔ یہ یقینی بناتا ہے کہ صرف ایک کنٹرولر ہر کمانڈ انٹرفیس پر لکھتا ہے (تضادات کو روکتا ہے)۔

### 3. کنٹرولرز

کنٹرول الگوری دھم کو نافذ کریں (PID، ماڈل پریڈکٹو کنٹرول، امپیڈنس کنٹرول)۔ ROS 2 معیاری کنٹرولرز فراہم کرتا ہے:
- **JointTrajectoryController**: ہموار ملٹی-جوائنٹ ٹریجیکٹریز انجام دیتا ہے
- **JointGroupPositionController**: جوائنٹ گروپس کے لئے سادہ پوزیشن کمانڈز
- **DiffDriveController**: موبائل بیسز کے لئے (وہیلڈ ہیومنوائڈز)

## ہیومنوائڈ روبوٹس کے لئے کنٹرولر کی اقسام

### پوزیشن کنٹرولرز

مطلوبہ جوائنٹ اینگلز کا کمانڈ دیں۔ ہارڈ ویئر انٹرفیس (یا ایکٹو ایٹر میں نچلی سطح کا کنٹرولر) ہدف پوزیشن حاصل کرنے کے لئے کنٹرول لوپ بند کرتا ہے۔

**استعمال کے معاملات**:
- ہدف کی پوز پر پہنچنا (بازو سامنے کی طرف تان دیا گیا)
- اسٹیٹک پوسٹر ہولڈ کرنا (کھڑے ہونا)
- پہلے سے ریکارڈ شدہ حرکات کو پلے بیک کرنا

**پابندیاں**: براہ راست کانٹیکٹ فورسز کنٹرول نہیں کر سکتا— گریپنگ یا مطیع سطحوں پر توازن کے کاموں کے لئے مسئلہ۔

### رفتار کنٹرولرز

مطلوبہ جوائنٹ رفتاروں کا کمانڈ دیں۔ ایسی جاری حرکات کے لئے مفید جہاں درست پوزیشن کے بجائے ہموار رفتار کے پروفائلز زیادہ اہم ہوں۔

**استعمال کے معاملات**:
- مقررہ جوائنٹ رفتار پروفائلز کے ساتھ چلنا
- بیرونی فورسز کے ساتھ مطابقت رکھنے والی مطیع حرکات
- ٹیلی آپریشن (جواستک ان پٹ جوائنٹ اسپیڈز میں میپ ہوتا ہے)

**پابندیاں**: فیڈ بیک کی اصلاح کے بغیر وقت کے ساتھ پوزیشن ڈریفٹ۔

### ایفروٹ کنٹرولرز

مطلوبہ جوائنٹ ٹورکس/فورسز کا کمانڈ دیں۔ انٹرایکشن فورسز پر براہ راست کنٹرول فراہم کرتا ہے— اعلیٰ ہیومنوائڈ رویوں کے لئے ضروری۔

**استعمال کے معاملات**:
- محفوظ انسان-روبوٹ انٹرایکشن کے لئے امپیڈنس کنٹرول
- فورس-بیسڈ گریپنگ (ہدف کی فورس کا پتہ چلنے تک گریپر بند کریں)
- ankle/hip ٹورکس کا استعمال کرتے ہوئے مرکزِ ماس کو ریگولیٹ کرنے کے لئے توازن کنٹرول

**چیلنجز**: درست ڈائنامک ماڈلز اور فورس/ٹورک سینسنگ کی ضرورت ہوتی ہے۔ زیادہ تر ہیومنوائڈ تحقیق ایفروٹ کنٹرول موڈ میں کام کرتی ہے۔

## URDF میں ros2_control کنفیگریشن

ros2_control کو استعمال کرنے کے لئے، اپنے URDF میں خصوصی ٹیگز شامل کریں جو ہارڈ ویئر انٹرفیسز اور کنٹرولرز کی وضاحت کرتے ہیں۔

### ہارڈ ویئر انٹرفیس کی وضاحت

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid">

  <!-- ros2_control Xacro میکروز شامل کریں -->
  <xacro:include filename="$(find ros2_control)/urdf/ros2_control.xacro"/>

  <!-- ros2_control ہارڈ ویئر انٹرفیس کی وضاحت کریں -->
  <ros2_control name="HumanoidRobotSystem" type="system">

    <!-- ہارڈ ویئر پلگ ان (سیمولیشن کے لئے Gazebo استعمال کریں) -->
    <hardware>
      <plugin>gazebo_ros2_control/GazeboSystem</plugin>
    </hardware>

    <!-- جوائنٹ 1: بائیں شولڈر پچ -->
    <joint name="left_shoulder_pitch">
      <!-- اسٹیٹ انٹرفیسز: جو سینسر پڑھ سکتے ہیں -->
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>

      <!-- کمانڈ انٹرفیسز: جو کنٹرولرز لکھ سکتے ہیں -->
      <command_interface name="position">
        <!-- اختیاری: ابتدائی کمانڈ قیمت سیٹ کریں -->
        <param name="initial_value">0.0</param>
      </command_interface>
      <command_interface name="effort"/>

      <!-- جوائنٹ حدود (اختیاری، URDF سے بھی پڑھا جا سکتا ہے) -->
      <param name="min_position">-1.57</param>
      <param name="max_position">1.57</param>
      <param name="max_velocity">2.0</param>
      <param name="max_effort">100.0</param>
    </joint>

    <!-- جوائنٹ 2: بائیں شولڈر رول -->
    <joint name="left_shoulder_roll">
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
      <command_interface name="position"/>
      <command_interface name="effort"/>
      <param name="min_position">-0.785</param>
      <param name="max_position">0.785</param>
    </joint>

    <!-- جوائنٹ 3: بائیں البو -->
    <joint name="left_elbow">
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
      <command_interface name="position"/>
      <command_interface name="effort"/>
      <param name="min_position">0.0</param>
      <param name="max_position">2.356</param>
    </joint>

    <!-- دائیں بازو اور ٹانگ جوائنٹس کے لئے دہرائیں... -->

    <!-- اختیاری: توازن کنٹرول کے لئے IMU سینسر -->
    <sensor name="imu_sensor">
      <state_interface name="orientation.x"/>
      <state_interface name="orientation.y"/>
      <state_interface name="orientation.z"/>
      <state_interface name="orientation.w"/>
      <state_interface name="angular_velocity.x"/>
      <state_interface name="angular_velocity.y"/>
      <state_interface name="angular_velocity.z"/>
      <state_interface name="linear_acceleration.x"/>
      <state_interface name="linear_acceleration.y"/>
      <state_interface name="linear_acceleration.z"/>
    </sensor>

  </ros2_control>

  <!-- ros2_control لوڈ کرنے کے لئے Gazebo پلگ ان -->
  <gazebo>
    <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
      <robot_param>robot_description</robot_param>
      <robot_param_node>robot_state_publisher</robot_param_node>
      <parameters>$(find humanoid_control)/config/controllers.yaml</parameters>
    </plugin>
  </gazebo>

</robot>
```

### کنٹرولر کنفیگریشن YAML

`config/controllers.yaml` میں کنٹرولر پیرامیٹرز کی وضاحت کریں:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz - کنٹرول لوپ فریکوئنسی

    # اسٹارٹ اپ پر لوڈ کرنے کے لئے کنٹرولرز کی فہرست
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    arm_position_controller:
      type: position_controllers/JointGroupPositionController

    arm_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController

# جوائنٹ اسٹیٹ براڈکاسٹر: /joint_states ٹاپک شائع کرتا ہے
joint_state_broadcaster:
  ros__parameters:
    # کوئی اضافی کنفیگ کی ضرورت نہیں - خود بخود تمام جوائنٹس براڈکاسٹ کرتا ہے

# ارمل پوزیشن کنٹرولر: سادہ پوزیشن کمانڈز
arm_position_controller:
  ros__parameters:
    joints:
      - left_shoulder_pitch
      - left_shoulder_roll
      - left_elbow
      - right_shoulder_pitch
      - right_shoulder_roll
      - right_elbow

    # کمانڈ کرنے کے لئے انٹرفیس (position، velocity، یا effort)
    interface_name: position

# ارمل ٹریجیکٹری کنٹرولر: ہموار ٹریجیکٹری انجام دہی
arm_trajectory_controller:
  ros__parameters:
    joints:
      - left_shoulder_pitch
      - left_shoulder_roll
      - left_elbow
      - right_shoulder_pitch
      - right_shoulder_roll
      - right_elbow

    # کمانڈ انٹرفیس
    command_interfaces:
      - position

    # فیڈ بیک کے لئے اسٹیٹ انٹرفیسز
    state_interfaces:
      - position
      - velocity

    # ٹریجیکٹری انجام دہی کے لئے پابندیاں
    constraints:
      stopped_velocity_tolerance: 0.01  # rad/s
      goal_time: 0.5  # سیکنڈز - ہدف تک پہنچنے کے لئے ٹائم ٹو لرنس
    # ٹریجیکٹری ٹریکنگ کے لئے PID گینز (فی جوائنٹ)
    gains:
      left_shoulder_pitch: {p: 100.0, d: 10.0, i: 0.0, i_clamp: 1.0}
      left_shoulder_roll: {p: 80.0, d: 8.0, i: 0.0, i_clamp: 1.0}
      left_elbow: {p: 60.0, d: 6.0, i: 0.0, i_clamp: 1.0}
      right_shoulder_pitch: {p: 100.0, d: 10.0, i: 0.0, i_clamp: 1.0}
      right_shoulder_roll: {p: 80.0, d: 8.0, i: 0.0, i_clamp: 1.0}
      right_elbow: {p: 60.0, d: 6.0, i: 0.0, i_clamp: 1.0}
```

## کنٹرول لوپ کی بنیاد

ros2_control کنٹرول لوپ اس ترتیب پر عمل کرتا ہے (`update_rate` پر، مثلاً 100 Hz):

### 1. اسٹیٹ پڑھیں

ہارڈ ویئر انٹرفیس انکوڈرز/سینسرز سے موجودہ جوائنٹ پوزیشنز، رفتاروں، اور ایفروٹس پڑھتا ہے۔

```cpp
// جھوٹا کوڈ - حقیقی امپلیمنٹ ہارڈ ویئر پلگ ان میں ہے
for (auto& joint : joints_) {
  joint.position = read_encoder(joint.name);
  joint.velocity = compute_velocity(joint.position, previous_position, dt);
  joint.effort = read_current_sensor(joint.name);
}
```

### 2. کنٹرولرز اپ ڈیٹ کریں

ہر فعال کنٹرولر اپنا کنٹرول الگوری دھم چلاتا ہے، اسٹیٹ پڑھتا ہے اور کمانڈز کا حساب لگاتا ہے۔

```cpp
// JointTrajectoryController اپ ڈیٹ (سادہ)
for (size_t i = 0; i < joints_.size(); ++i) {
  // موجودہ وقت پر ٹریجیکٹری سے ہدف کی پوزیشن حاصل کریں
  double target_position = trajectory_.sample(current_time, i);

  // PID کنٹرول لاء
  double error = target_position - joint_state_[i].position;
  double error_derivative = -joint_state_[i].velocity;  // یہ سمجھتا ہے کہ ہدف کی رفتار = 0 ہے

  // کمانڈ کا حساب (اس کیس میں ایفروٹ)
  joint_commands_[i].effort = gains_[i].p * error + gains_[i].d * error_derivative;

  // جوائنٹ حدود تک محدود کریں
  joint_commands_[i].effort = std::clamp(
    joint_commands_[i].effort,
    -max_effort_[i],
    max_effort_[i]
  );
}
```

### 3. کمانڈز لکھیں

ہارڈ ویئر انٹرفیس ایکٹو ایٹرز کو کمانڈز بھیجتا ہے۔

```cpp
// جھوٹا کوڈ
for (auto& joint : joints_) {
  write_motor_command(joint.name, joint.command_effort);
}
```

### 4. دہرائیں

لوپ مقررہ شرح پر دہرتا ہے۔ ریل ٹائم شیڈولنگ یقینی بناتی ہے کہ تعیناتی ٹائمزنگ۔

## ros2_control سسٹم لانچ کرنا

```python
#!/usr/bin/env python3
"""
ros2_control کے ساتھ ہیومنوائڈ روبوٹ کے لئے لانچ فائل۔
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # URDF فائل کا پتہ حاصل کریں
    urdf_path = os.path.join(
        get_package_share_directory('humanoid_description'),
        'urdf',
        'humanoid.urdf.xacro'
    )

    # کنٹرولر کنفیگ کا پتہ
    controller_config = os.path.join(
        get_package_share_directory('humanoid_control'),
        'config',
        'controllers.yaml'
    )

    return LaunchDescription([
        # Gazebo سیمولیشن شروع کریں
        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
            output='screen'
        ),

        # Gazebo میں روبوٹ اسپون کریں
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-entity', 'humanoid', '-topic', 'robot_description'],
            output='screen'
        ),

        # روبوٹ کی وضاحت شائع کریں
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_path).read()}],
            output='screen'
        ),

        # کنٹرولر مینجر لوڈ اور شروع کریں
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[controller_config],
            output='screen'
        ),

        # کنٹرولرز اسپون کریں
        ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                 'joint_state_broadcaster'],
            output='screen'
        ),

        ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                 'arm_trajectory_controller'],
            output='screen'
        ),

        # RViz لانچ کریں وژوئلائزیشن کے لئے
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.join(
                get_package_share_directory('humanoid_description'),
                'rviz',
                'humanoid.rviz'
            )],
            output='screen'
        ),
    ])
```

## کنٹرولرز ٹیسٹ کرنا

```bash
# دستیاب کنٹرولرز کی فہرست
ros2 control list_controllers

# کنٹرولر کی حیثیت چیک کریں
ros2 control list_hardware_interfaces

# ارمل کنٹرولر کو پوزیشن کمانڈ بھیجیں
ros2 topic pub /arm_position_controller/commands std_msgs/msg/Float64MultiArray \
  "{data: [0.5, 0.3, 1.2, -0.5, -0.3, -1.2]}"

# ٹریجیکٹری کنٹرولر کو ٹریجیکٹری بھیجیں
ros2 action send_goal /arm_trajectory_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  -f trajectory_goal.yaml
```

## حقیقی روبوٹس کے لئے ہارڈ ویئر انٹرفیسز

جسمانی ہیومنوائڈ ہارڈ ویئر کے لئے، ایک حسب ضرورت ہارڈ ویئر انٹرفیس پلگ ان نافذ کریں:

```cpp
#include "hardware_interface/system_interface.hpp"

class HumanoidHardwareInterface : public hardware_interface::SystemInterface
{
public:
  // ہارڈ ویئر شروع کریں (سیریل پورٹس کھولیں، موٹر کنٹرولرز سے منسلک ہوں)
  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override;

  // انکوڈرز سے جوائنٹ اسٹیٹس پڑھیں
  hardware_interface::return_type read(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

  // موٹرز کو کمانڈز لکھیں
  hardware_interface::return_type write(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  // ہارڈ ویئر رابطہ (مثلاً، CAN بس، EtherCAT)
  std::unique_ptr<MotorController> motor_controller_;

  // کیچ شدہ اسٹیٹ/کمانڈ اقدار
  std::vector<double> joint_positions_;
  std::vector<double> joint_velocities_;
  std::vector<double> joint_efforts_;
  std::vector<double> joint_commands_;
};
```

## اگلے اقدامات

آپ اب سمجھتے ہیں کہ ros2_control سیمولیشن اور ہارڈ ویئر کو معیاری انٹرفیسز کے ذریعے کیسے جوڑتا ہے۔ آخری باب ایک **مکمل URDF مثال** فراہم کرتا ہے جس میں ros2_control کنفیگریشن کا انضمام ہے— Gazebo میں سیمولیشن کے لئے تیار ایک کام کرتا ہیومنوائڈ روبوٹ۔

### مشق ورزش

1. `controllers.yaml` میں ہپ اور گھٹنے کے جوائنٹس کے لئے ایک `leg_position_controller` تخلیق کرنے کے لئے تبدیل کریں
2. Gazebo میں سسٹم لانچ کریں
3. `ros2 topic pub` کا استعمال کرتے ہوئے ٹانگوں کو حرکت دینے کے لئے کمانڈز بھیجیں
4. `ros2 topic echo /joint_states` کے ساتھ جوائنٹ اسٹیٹس مانیٹر کریں
5. PID گینز ٹیون کریں تاکہ بے تکلف حرکت حاصل کی جا سکے بنا آسیلیشن کے