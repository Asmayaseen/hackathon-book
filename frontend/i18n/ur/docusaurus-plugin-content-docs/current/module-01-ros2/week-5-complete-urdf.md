# ہفتہ 5: مکمل ہیومنوائڈ URDF مثال

## جائزہ

یہ باب ٹورسو، اعضا، اور ٹانگوں والے ایک سادہ ہیومنوائڈ روبوٹ کے لئے مکمل، کام کرتا URDF ماڈل پیش کرتا ہے۔ ماڈل میں شامل ہے:
- مکمل کنیمیٹک چین (18 ڈگریز آف فریڈم)
- سیلف-کولیژن سے بچاؤ کے لئے درست کولیژن جیومیٹری
- حقیقی ڈائنامکس سیمولیشن کے لئے انرٹیل خصوصیات
- پوزیشن اور ایفروٹ کنٹرول کے لئے ros2_control کا انضمام
- ماڈیولریٹی اور دیکھ بھال کے لئے Xacro میکروز

یہ روبوٹ Gazebo میں سیمولیٹ کیا جا سکتا ہے، RViz میں وژوئلائز کیا جا سکتا ہے، اور ros2_control کے ذریعے کنٹرول کیا جا سکتا ہے— ہیومنوائڈ تحقیق اور ترقی کے لئے بنیاد فراہم کرتا ہے۔

## روبوٹ کی تفصیلات

**ڈگریز آف فریڈم**:
- ٹورسو: 1 (کمر کی گردش)
- اعضا: 8 (4 فی بازو: شولڈر پچ/رول، البو، wrist گردش)
- ٹانگیں: 8 (4 فی ٹانگ: ہپ پچ/رول، گھٹنا، ankle پچ)
- ہاتھ: سادہ (اس ورژن میں انفرادی انگلی جوائنٹس نہیں)

**جسمانی ابعاد** (میٹرز میں):
- اونچائی: 1.65م (اوسط انسان کے قابل موازنہ)
- ٹورسو: 0.5م اونچا، 0.3م چوڑا
- اپر ارمل: 0.3م لمبائی
- فور ارمل: 0.25م لمبائی
- تھigh: 0.4م لمبائی
- شن: 0.4م لمبائی

## مکمل Xacro ماڈل

### مرکزی روبوٹ فائل: `humanoid.urdf.xacro`

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="simple_humanoid">

  <!-- دہرائے گئے ڈھانچوں کے لئے میکروز شامل کریں -->
  <xacro:include filename="$(find humanoid_description)/urdf/macros.xacro"/>
  <xacro:include filename="$(find humanoid_description)/urdf/materials.xacro"/>

  <!-- روبوٹ پیرامیٹرز -->
  <xacro:property name="pi" value="3.14159265359"/>

  <!-- لنک ابعاد (میٹرز میں) -->
  <xacro:property name="torso_width" value="0.3"/>
  <xacro:property name="torso_depth" value="0.2"/>
  <xacro:property name="torso_height" value="0.5"/>

  <xacro:property name="upper_arm_length" value="0.3"/>
  <xacro:property name="upper_arm_radius" value="0.05"/>
  <xacro:property name="forearm_length" value="0.25"/>
  <xacro:property name="forearm_radius" value="0.04"/>

  <xacro:property name="thigh_length" value="0.4"/>
  <xacro:property name="thigh_radius" value="0.06"/>
  <xacro:property name="shin_length" value="0.4"/>
  <xacro:property name="shin_radius" value="0.05"/>

  <xacro:property name="foot_length" value="0.2"/>
  <xacro:property name="foot_width" value="0.1"/>
  <xacro:property name="foot_height" value="0.05"/>

  <!-- لنک ماسز (kg میں) -->
  <xacro:property name="torso_mass" value="25.0"/>
  <xacro:property name="upper_arm_mass" value="2.5"/>
  <xacro:property name="forearm_mass" value="1.5"/>
  <xacro:property name="hand_mass" value="0.5"/>
  <xacro:property name="thigh_mass" value="5.0"/>
  <xacro:property name="shin_mass" value="3.0"/>
  <xacro:property name="foot_mass" value="1.0"/>

  <!-- ======================== -->
  <!-- بیس اور ٹورسو            -->
  <!-- ======================== -->

  <!-- بیس لنک (سیمولیشن میں دنیا سے منسلک) -->
  <link name="base_link">
    <visual>
      <origin xyz="0 0 0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.4 0.3 0.05"/>
      </geometry>
      <material name="dark_grey"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.025" rpy="0 0 0"/>
      <geometry>
        <box size="0.4 0.3 0.05"/>
      </geometry>
    </collision>
    <xacro:box_inertia mass="10.0" x="0.4" y="0.3" z="0.05"/>
  </link>

  <!-- ٹورسو لنک -->
  <link name="torso">
    <visual>
      <origin xyz="0 0 ${torso_height/2}" rpy="0 0 0"/>
      <geometry>
        <box size="${torso_width} ${torso_depth} ${torso_height}"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 ${torso_height/2}" rpy="0 0 0"/>
      <geometry>
        <box size="${torso_width} ${torso_depth} ${torso_height}"/>
      </geometry>
    </collision>
    <xacro:box_inertia mass="${torso_mass}" x="${torso_width}" y="${torso_depth}" z="${torso_height}"/>
  </link>

  <!-- کمر جوائنٹ: Z-axis کے گرد گردش -->
  <joint name="waist_rotation" type="continuous">
    <parent link="base_link"/>
    <child link="torso"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit effort="150.0" velocity="1.5"/>
    <dynamics damping="1.0" friction="0.5"/>
  </joint>

  <!-- ======================== -->
  <!-- اعضا (میکرو کا استعمال)    -->
  <!-- ======================== -->

  <!-- بائیں بازو -->
  <xacro:arm_assembly
    side="left"
    reflect="1"
    parent="torso"
    origin_xyz="0.0 ${torso_depth/2 + 0.05} ${torso_height - 0.1}"
    origin_rpy="0 0 0"/>

  <!-- دائیں بازو -->
  <xacro:arm_assembly
    side="right"
    reflect="-1"
    parent="torso"
    origin_xyz="0.0 ${-(torso_depth/2 + 0.05)} ${torso_height - 0.1}"
    origin_rpy="0 0 0"/>

  <!-- ======================== -->
  <!-- ٹانگیں (میکرو کا استعمال)   -->
  <!-- ======================== -->

  <!-- بائیں ٹانگ -->
  <xacro:leg_assembly
    side="left"
    reflect="1"
    parent="base_link"
    origin_xyz="0.0 ${torso_depth/4} 0.05"
    origin_rpy="0 0 0"/>

  <!-- دائیں ٹانگ -->
  <xacro:leg_assembly
    side="right"
    reflect="-1"
    parent="base_link"
    origin_xyz="0.0 ${-torso_depth/4} 0.05"
    origin_rpy="0 0 0"/>

  <!-- ======================== -->
  <!-- ros2_control انضمام -->
  <!-- ======================== -->

  <xacro:include filename="$(find humanoid_description)/urdf/ros2_control.xacro"/>
  <xacro:humanoid_ros2_control/>

  <!-- ======================== -->
  <!-- Gazebo پلگ انز           -->
  <!-- ======================== -->

  <xacro:include filename="$(find humanoid_description)/urdf/gazebo.xacro"/>

</robot>
```

### میکروز فائل: `macros.xacro`

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- ======================== -->
  <!-- انرٹیا میکروز           -->
  <!-- ======================== -->

  <!-- باکس انرٹیا -->
  <xacro:macro name="box_inertia" params="mass x y z">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="${mass}"/>
      <inertia
        ixx="${mass * (y*y + z*z) / 12.0}"
        ixy="0.0" ixz="0.0"
        iyy="${mass * (x*x + z*z) / 12.0}"
        iyz="0.0"
        izz="${mass * (x*x + y*y) / 12.0}"/>
    </inertial>
  </xacro:macro>

  <!-- سلنڈر انرٹیا (Z کے ساتھ ایکسز) -->
  <xacro:macro name="cylinder_inertia" params="mass radius length">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="${mass}"/>
      <inertia
        ixx="${mass * (3*radius*radius + length*length) / 12.0}"
        ixy="0.0" ixz="0.0"
        iyy="${mass * (3*radius*radius + length*length) / 12.0}"
        iyz="0.0"
        izz="${mass * radius * radius / 2.0}"/>
    </inertial>
  </xacro:macro>

  <!-- ======================== -->
  <!-- ارمل اسمبلی میکرو       -->
  <!-- ======================== -->

  <xacro:macro name="arm_assembly" params="side reflect parent origin_xyz origin_rpy">

    <!-- اپر ارمل لنک -->
    <link name="${side}_upper_arm">
      <visual>
        <origin xyz="0 0 ${-upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${upper_arm_radius}" length="${upper_arm_length}"/>
        </geometry>
        <material name="blue"/>
      </visual>
      <collision>
        <origin xyz="0 0 ${-upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${upper_arm_radius}" length="${upper_arm_length}"/>
        </geometry>
      </collision>
      <xacro:cylinder_inertia mass="${upper_arm_mass}" radius="${upper_arm_radius}" length="${upper_arm_length}"/>
    </link>

    <!-- شولڈر پچ جوائنٹ (آگے/پیچھے) -->
    <joint name="${side}_shoulder_pitch" type="revolute">
      <parent link="${parent}"/>
      <child link="${side}_upper_arm"/>
      <origin xyz="${origin_xyz}" rpy="${origin_rpy}"/>
      <axis xyz="0 ${reflect} 0"/>
      <limit lower="${-pi/2}" upper="${pi/2}" effort="100.0" velocity="2.0"/>
      <dynamics damping="0.7" friction="0.5"/>
    </joint>

    <!-- فور ارمل لنک -->
    <link name="${side}_forearm">
      <visual>
        <origin xyz="0 0 ${-forearm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${forearm_radius}" length="${forearm_length}"/>
        </geometry>
        <material name="light_blue"/>
      </visual>
      <collision>
        <origin xyz="0 0 ${-forearm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${forearm_radius}" length="${forearm_length}"/>
        </geometry>
      </collision>
      <xacro:cylinder_inertia mass="${forearm_mass}" radius="${forearm_radius}" length="${forearm_length}"/>
    </link>

    <!-- البو جوائنٹ -->
    <joint name="${side}_elbow" type="revolute">
      <parent link="${side}_upper_arm"/>
      <child link="${side}_forearm"/>
      <origin xyz="0 0 ${-upper_arm_length}" rpy="0 0 0"/>
      <axis xyz="0 ${reflect} 0"/>
      <limit lower="0.0" upper="${pi * 0.75}" effort="80.0" velocity="2.0"/>
      <dynamics damping="0.5" friction="0.3"/>
    </joint>

    <!-- ہینڈ لنک -->
    <link name="${side}_hand">
      <visual>
        <origin xyz="0 0 -0.05" rpy="0 0 0"/>
        <geometry>
          <box size="0.08 0.05 0.1"/>
        </geometry>
        <material name="grey"/>
      </visual>
      <collision>
        <origin xyz="0 0 -0.05" rpy="0 0 0"/>
        <geometry>
          <box size="0.08 0.05 0.1"/>
        </geometry>
      </collision>
      <xacro:box_inertia mass="${hand_mass}" x="0.08" y="0.05" z="0.1"/>
    </link>

    <!-- wrist جوائنٹ -->
    <joint name="${side}_wrist_rotation" type="continuous">
      <parent link="${side}_forearm"/>
      <child link="${side}_hand"/>
      <origin xyz="0 0 ${-forearm_length}" rpy="0 0 0"/>
      <axis xyz="0 0 ${reflect}"/>
      <limit effort="30.0" velocity="3.0"/>
      <dynamics damping="0.2" friction="0.1"/>
    </joint>

  </xacro:macro>

  <!-- ======================== -->
  <!-- لیگ اسمبلی میکرو       -->
  <!-- ======================== -->

  <xacro:macro name="leg_assembly" params="side reflect parent origin_xyz origin_rpy">

    <!-- تھigh لنک -->
    <link name="${side}_thigh">
      <visual>
        <origin xyz="0 0 ${-thigh_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${thigh_radius}" length="${thigh_length}"/>
        </geometry>
        <material name="dark_blue"/>
      </visual>
      <collision>
        <origin xyz="0 0 ${-thigh_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${thigh_radius}" length="${thigh_length}"/>
        </geometry>
      </collision>
      <xacro:cylinder_inertia mass="${thigh_mass}" radius="${thigh_radius}" length="${thigh_length}"/>
    </link>

    <!-- ہپ پچ جوائنٹ (آگے/پیچھے) -->
    <joint name="${side}_hip_pitch" type="revolute">
      <parent link="${parent}"/>
      <child link="${side}_thigh"/>
      <origin xyz="${origin_xyz}" rpy="${origin_rpy}"/>
      <axis xyz="0 ${reflect} 0"/>
      <limit lower="${-pi/3}" upper="${pi/2}" effort="200.0" velocity="1.5"/>
      <dynamics damping="1.0" friction="0.8"/>
    </joint>

    <!-- شن لنک -->
    <link name="${side}_shin">
      <visual>
        <origin xyz="0 0 ${-shin_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${shin_radius}" length="${shin_length}"/>
        </geometry>
        <material name="blue"/>
      </visual>
      <collision>
        <origin xyz="0 0 ${-shin_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${shin_radius}" length="${shin_length}"/>
        </geometry>
      </collision>
      <xacro:cylinder_inertia mass="${shin_mass}" radius="${shin_radius}" length="${shin_length}"/>
    </link>

    <!-- گھٹنا جوائنٹ -->
    <joint name="${side}_knee" type="revolute">
      <parent link="${side}_thigh"/>
      <child link="${side}_shin"/>
      <origin xyz="0 0 ${-thigh_length}" rpy="0 0 0"/>
      <axis xyz="0 ${reflect} 0"/>
      <limit lower="0.0" upper="${pi * 0.7}" effort="150.0" velocity="1.5"/>
      <dynamics damping="0.8" friction="0.6"/>
    </joint>

    <!-- فُٹ لنک -->
    <link name="${side}_foot">
      <visual>
        <origin xyz="${foot_length/4} 0 ${-foot_height/2}" rpy="0 0 0"/>
        <geometry>
          <box size="${foot_length} ${foot_width} ${foot_height}"/>
        </geometry>
        <material name="black"/>
      </visual>
      <collision>
        <origin xyz="${foot_length/4} 0 ${-foot_height/2}" rpy="0 0 0"/>
        <geometry>
          <box size="${foot_length} ${foot_width} ${foot_height}"/>
        </geometry>
      </collision>
      <xacro:box_inertia mass="${foot_mass}" x="${foot_length}" y="${foot_width}" z="${foot_height}"/>
    </link>

    <!-- ankle پچ جوائنٹ -->
    <joint name="${side}_ankle_pitch" type="revolute">
      <parent link="${side}_shin"/>
      <child link="${side}_foot"/>
      <origin xyz="0 0 ${-shin_length}" rpy="0 0 0"/>
      <axis xyz="0 ${reflect} 0"/>
      <limit lower="${-pi/4}" upper="${pi/4}" effort="100.0" velocity="1.0"/>
      <dynamics damping="0.5" friction="0.4"/>
    </joint>

  </xacro:macro>

</robot>
```

### مواد فائل: `materials.xacro`

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- وژوئلائزیشن کے لئے رنگ کی تعریفیں -->

  <material name="blue">
    <color rgba="0.2 0.2 0.8 1.0"/>
  </material>

  <material name="light_blue">
    <color rgba="0.4 0.6 1.0 1.0"/>
  </material>

  <material name="dark_blue">
    <color rgba="0.1 0.1 0.4 1.0"/>
  </material>

  <material name="grey">
    <color rgba="0.5 0.5 0.5 1.0"/>
  </material>

  <material name="dark_grey">
    <color rgba="0.3 0.3 0.3 1.0"/>
  </material>

  <material name="black">
    <color rgba="0.1 0.1 0.1 1.0"/>
  </material>

  <material name="white">
    <color rgba="0.9 0.9 0.9 1.0"/>
  </material>

  <material name="red">
    <color rgba="0.8 0.1 0.1 1.0"/>
  </material>

  <material name="green">
    <color rgba="0.1 0.8 0.1 1.0"/>
  </material>

</robot>
```

### ros2_control کنفیگریشن: `ros2_control.xacro`

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <xacro:macro name="humanoid_ros2_control">

    <ros2_control name="HumanoidSystem" type="system">

      <hardware>
        <plugin>gazebo_ros2_control/GazeboSystem</plugin>
      </hardware>

      <!-- کمر جوائنٹ -->
      <joint name="waist_rotation">
        <command_interface name="effort"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <!-- بائیں بازو جوائنٹس -->
      <joint name="left_shoulder_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="left_elbow">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="left_wrist_rotation">
        <command_interface name="effort"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <!-- دائیں بازو جوائنٹس (بائیں کا عکس) -->
      <joint name="right_shoulder_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="right_elbow">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="right_wrist_rotation">
        <command_interface name="effort"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <!-- بائیں ٹانگ جوائنٹس -->
      <joint name="left_hip_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="left_knee">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="left_ankle_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <!-- دائیں ٹانگ جوائنٹس (بائیں کا عکس) -->
      <joint name="right_hip_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="right_knee">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

      <joint name="right_ankle_pitch">
        <command_interface name="effort"/>
        <command_interface name="position"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
        <state_interface name="effort"/>
      </joint>

    </ros2_control>

    <!-- Gazebo ros2_control پلگ ان لوڈ کریں -->
    <gazebo>
      <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
        <parameters>$(find humanoid_control)/config/controllers.yaml</parameters>
      </plugin>
    </gazebo>

  </xacro:macro>

</robot>
```

## ماڈل کی ٹیسٹنگ

### RViz میں وژوئلائز کریں

```bash
# Xacro کو URDF میں تبدیل کریں
xacro humanoid.urdf.xacro > humanoid.urdf

# خامیوں کی جانچ کریں
check_urdf humanoid.urdf

# RViz لانچ کریں
ros2 launch urdf_tutorial display.launch.py model:=humanoid.urdf.xacro
```

### Gazebo میں سیمولیٹ کریں

```bash
# روبوٹ کے ساتھ Gazebo لانچ کریں
ros2 launch humanoid_description gazebo.launch.py

# کنٹرولرز کی فہرست
ros2 control list_controllers

# بائیں بازو کو ٹیسٹ کمانڈ بھیجیں
ros2 topic pub /left_arm_position_controller/commands std_msgs/msg/Float64MultiArray \
  "{data: [0.5, 1.0]}"
```

## ماڈیول کا خلاصہ

مبارک ہو! آپ نے ماڈیول 1: ROS 2 کی بنیادیں مکمل کر لیا ہے۔ اب آپ کر سکتے ہیں:

- ROS 2 ڈویلپمنٹ ماحول انسٹال کریں اور کنفیگر کریں
- شائع کار، سبسکرائبرز، سروسز، اور ایکشن سرورز تخلیق کریں
- URDF اور Xacro کے ساتھ ہیومنوائڈ روبوٹس کو ماڈل کریں
- سیمولیشن اور ہارڈ ویئر کے لئے ros2_control کا انضمام کریں
- RViz اور Gazebo میں روبوٹس کو وژوئلائز کریں اور ٹیسٹ کریں

یہ بنیاد آپ کو ماڈیول 2: سیمولیشن ماحول کے لئے تیار کرتی ہے، جہاں آپ Gazebo کی اعلیٰ تکنیک، سینسر سیمولیشن، اور ہیومنوائڈ چالن کے لئے فزکس-بیسڈ کانٹیکٹ ماڈلنگ سیکھیں گے۔

### اگلے اقدامات

1. مکمل ہیومنوائڈ ماڈل کے ساتھ تجربہ کریں: جوائنٹ حدود میں تبدیلی کریں، سینسرز شامل کریں (کیمرز، IMU)، کنٹرولر گینز ٹیون کریں
2. ایک توازن کنٹرولر نافذ کریں جو IMU فیڈ بیک کا استعمال کرے تاکہ گرنے سے بچا جا سکے
3. مربوط وہول-بอดی موشنز (ہاتھ ہلانا، ڈگم لگانا) کے لئے ٹریجیکٹری فائلیں تخلیق کریں
4. کولیژن سے بچاؤ کے ساتھ موشن منصوبہ بندی کے لئے MoveIt انضمام کو دریافت کریں

فزیکل AI اور ہیومنوائڈ روبوٹکس میں اپنی مہارت کی تعمیر جاری رکھیں!