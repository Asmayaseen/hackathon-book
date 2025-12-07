# ہفتہ 5: ہیومنوائڈ روبوٹس کے لئے URDF

## URDF کا تعارف

یونیفائیڈ روبوٹ کی وضاحت فارمیٹ (URDF) روبوٹ کنیمیٹکس، ڈائنامکس، اور وژوئل اظہار کی وضاحت کے لئے XML-بیسڈ وضاحت ہے۔ URDF فائلیں روبوٹ کی ساخت کو لنکس (ریجیڈ باڈیز) کے درخت کے بطور وضاحت کرتی ہیں جو جوائنٹس (موو ایبل یا فکسڈ کنکشنز) کے ذریعے منسلک ہیں۔

ہیومنوائڈ روبوٹس کے لئے، URDF اجازت دیتا ہے:
- **سیمولیشن**: Gazebo یا RViz میں ہارڈ ویئر ٹیسٹنگ سے پہلے روبوٹ موشن کو دیکھنا
- **کنیمیٹکس**: پوز منصوبہ بندی کے لئے فارورڈ/معکوس کنیمیٹکس کا حساب لگانا
- **کولیژن ڈیٹیکشن**: پیچیدہ حرکات کے دوران سیلف-کولیژن کو روکنا
- **کنٹرول**: جوائنٹ کی وضاحت سے کنٹرولر کنفیگریشنز تیار کرنا

### URDF فلسفہ

URDF روبوٹس کو کنیمیٹک ٹریز کے بطور ظاہر کرتا ہے جس میں ایک سنگل روت لنک (عام طور پر `base_link`) ہوتا ہے۔ ہر جوائنٹ ایک والد لنک کو ایک بچہ لنک سے منسلک کرتا ہے، ان کے درمیان ریلیٹو موشن کی وضاحت کرتا ہے۔ یہ ٹری ساخت اکثر روبوٹس کی فزیکل حقیقت سے مماثل ہے: ایک ہیومنوائڈ میں ایک ٹورسو (روت) ہوتا ہے جس سے اعضا باہر کی طرف شاخیں ہوتی ہیں۔

## جوائنٹ کی اقسام

URDF چھ جوائنٹ کی اقسام کی حمایت کرتا ہے، ہر ایک مختلف موشن کنٹرولز کی وضاحت کرتا ہے:

### ریوولوٹ جوائنٹس

ایک سنگل ایکسز کے گرد گھومتے ہیں جن میں اینگل حدود ہیں (روبوٹ جوائنٹس کے لئے سب سے عام)۔

```xml
<!-- شولڈر پچ جوائنٹ: Y-ایکسز کے گرد گھومتا ہے -->
<joint name="left_shoulder_pitch" type="revolute">
  <parent link="torso"/>
  <child link="left_upper_arm"/>

  <!-- والد لنک کے رشتے میں جوائنٹ کا اصل مقام -->
  <origin xyz="0.0 0.15 0.4" rpy="0 0 0"/>

  <!-- جوائنٹ فریم میں گردش کا ایکسز -->
  <axis xyz="0 1 0"/>

  <!-- جوائنٹ کی حدود (ریڈینز میں) -->
  <limit lower="-1.57" upper="1.57" effort="100.0" velocity="2.0"/>

  <!-- جوائنٹ ڈائنامکس (اختیاری) -->
  <dynamics damping="0.7" friction="0.5"/>
</joint>
```

**پیرامیٹرز**:
- `lower/upper`: ریڈینز میں اینگل حدود (اس مثال میں ±90°)
- `effort`: زیادہ سے زیادہ ٹورک (Nm) جو ایکٹو ایٹر لگا سکتا ہے
- `velocity`: زیادہ سے زیادہ اینگولر رفتار (rad/s)
- `damping`: بیرنگز میں انرجی ڈسیپیشن کی شبیہہ
- `friction`: اسٹیٹک/کنیٹک فرکشن کے ماڈلز

### پریزمیٹک جوائنٹس

ایک سنگل ایکسز کے ساتھ منتقل کرتے ہیں (ٹیلیسکوپنگ اعضا یا لکیری ایکٹو ایٹرز کے لئے استعمال ہوتا ہے)۔

```xml
<!-- ٹیلیسکوپنگ ٹورسو جوائنٹ -->
<joint name="torso_lift" type="prismatic">
  <parent link="base_link"/>
  <child link="torso"/>

  <origin xyz="0 0 0.5" rpy="0 0 0"/>

  <!-- منتقلی کا ایکسز -->
  <axis xyz="0 0 1"/>

  <!-- لکیری حدود (میٹرز میں) -->
  <limit lower="0.0" upper="0.3" effort="500.0" velocity="0.1"/>
</joint>
```

### کنٹینیوئس جوائنٹس

اےنگل حدود کے بغیر ریوولوٹ جوائنٹس (وہیلز یا غیر محدود گردش کے لئے)۔

```xml
<!-- کمر کی گردش (360° گردش) -->
<joint name="waist_yaw" type="continuous">
  <parent link="pelvis"/>
  <child link="torso"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit effort="80.0" velocity="1.5"/>
</joint>
```

### فکسڈ جوائنٹس

لنکس کو سختی سے منسلک کرتے ہیں (کوئی موشن نہیں)۔ سینسرز، اینڈ-ایفیکٹرز، یا سٹرکچرل کمپونینٹس کے لئے استعمال ہوتا ہے۔

```xml
<!-- سر پر نصب کیمرہ -->
<joint name="head_camera_joint" type="fixed">
  <parent link="head"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0.05" rpy="0 0 0"/>
</joint>
```

## لنک ساخت: وژوئل اور کولیژن جیومیٹری

ہر لنک وژوئل اظہار (RViz/Gazebo میں دیکھنے کے لئے) اور کولیژن جیومیٹری (فزکس سیمولیشن کے لئے) دونوں کی وضاحت کرتا ہے۔

```xml
<link name="left_upper_arm">
  <!-- وژوئل اظہار (RViz/Gazebo میں آپ جو دیکھتے ہیں) -->
  <visual>
    <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    <geometry>
      <!-- سلنڈر: ریڈیس=0.05م، لمبائی=0.3م -->
      <cylinder radius="0.05" length="0.3"/>
    </geometry>
    <material name="blue">
      <color rgba="0.0 0.0 0.8 1.0"/>
    </material>
  </visual>

  <!-- کولیژن جیومیٹری (فزکس/کانٹیکٹ ڈیٹیکشن کے لئے) -->
  <!-- اکثر کارکردگی کے لئے سادہ کیا جاتا ہے -->
  <collision>
    <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    <geometry>
      <!-- وژوئل کے ساتھ سادہ شکلوں کے لئے ایک جیسا -->
      <cylinder radius="0.05" length="0.3"/>
    </geometry>
  </collision>

  <!-- انرٹیل خصوصیات (ڈائنامکس سیمولیشن کے لئے) -->
  <inertial>
    <origin xyz="0 0 -0.15" rpy="0 0 0"/>
    <mass value="2.5"/>  <!-- kg -->

    <!-- سلنڈر کے لئے انرٹیا ٹینسر سینٹر آف ماس کے بارے میں -->
    <!-- استعمال کرتے ہوئے حساب: I = m*r²/2 (z-axis), I = m*(3r²+h²)/12 (x,y-axes) -->
    <inertia
      ixx="0.0208" ixy="0.0" ixz="0.0"
      iyy="0.0208" iyz="0.0"
      izz="0.003125"/>
  </inertial>
</link>
```

### جیومیٹری کے اختیارات

```xml
<!-- باکس (چوڑائی، گہرائی، اونچائی میٹرز میں) -->
<geometry>
  <box size="0.1 0.2 0.05"/>
</geometry>

<!-- سپیئر (ریڈیس میٹرز میں) -->
<geometry>
  <sphere radius="0.08"/>
</geometry>

<!-- میش (STL/DAE فائل سے لوڈ) -->
<geometry>
  <mesh filename="package://humanoid_description/meshes/hand.stl" scale="1.0 1.0 1.0"/>
</geometry>
```

## Xacro: ماڈیولر URDF

پیچیدہ روبوٹس کے لئے خام URDF لکھنا دہرائے ہوئے کوڈ کی طرف لے جاتا ہے۔ Xacro (XML میکروز) URDF کو یہ چیزیں دے کر توسیع دیتا ہے:
- **متغیرات**: کنستس کی وضاحت (لنک کی لمبائی، ماسز)
- **میکروز**: دہرائے گئے ڈھانچوں (بائیں/دائیں اعضا) کے لئے دوبارہ استعمال کے قابل ٹیمپلیٹس
- **ریاضی**: اقدار کا حساب (انرٹیا ٹینسرز، کمپاؤنڈ ٹرانسفارمز)
- **فائل انکلیوژن**: روبوٹ کو ماڈیولر فائلوں میں تقسیم کرنا

### Xacro مثال: پیرامیٹرائزڈ بازو

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid_arm">

  <!-- کنستس کی وضاحت کریں -->
  <xacro:property name="upper_arm_length" value="0.3"/>
  <xacro:property name="forearm_length" value="0.25"/>
  <xacro:property name="arm_radius" value="0.05"/>
  <xacro:property name="arm_mass" value="2.5"/>

  <!-- اعضا کے لنکس کے لئے میکرو (بائیں/دائیں کے لئے دوبارہ استعمال) -->
  <xacro:macro name="arm_links" params="side reflect">

    <!-- اپر ارمل لنک -->
    <link name="${side}_upper_arm">
      <visual>
        <origin xyz="0 0 ${-upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${arm_radius}" length="${upper_arm_length}"/>
        </geometry>
        <material name="blue">
          <color rgba="0.2 0.2 0.8 1.0"/>
        </material>
      </visual>

      <collision>
        <origin xyz="0 0 ${-upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${arm_radius}" length="${upper_arm_length}"/>
        </geometry>
      </collision>

      <xacro:cylinder_inertia
        mass="${arm_mass}"
        radius="${arm_radius}"
        length="${upper_arm_length}"/>
    </link>

    <!-- شولڈر جوائنٹ -->
    <joint name="${side}_shoulder_pitch" type="revolute">
      <parent link="torso"/>
      <child link="${side}_upper_arm"/>

      <!-- ریفلیکٹ پیرامیٹر: 1 بائیں کے لئے، -1 دائیں کے لئے -->
      <origin xyz="0.0 ${reflect * 0.15} 0.4" rpy="0 0 0"/>

      <axis xyz="0 1 0"/>
      <limit lower="-1.57" upper="1.57" effort="100.0" velocity="2.0"/>
      <dynamics damping="0.7"/>
    </joint>

    <!-- فور ارم لنک -->
    <link name="${side}_forearm">
      <visual>
        <origin xyz="0 0 ${-forearm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${arm_radius * 0.8}" length="${forearm_length}"/>
        </geometry>
        <material name="blue"/>
      </visual>

      <collision>
        <origin xyz="0 0 ${-forearm_length/2}" rpy="0 0 0"/>
        <geometry>
          <cylinder radius="${arm_radius * 0.8}" length="${forearm_length}"/>
        </geometry>
      </collision>

      <xacro:cylinder_inertia
        mass="${arm_mass * 0.8}"
        radius="${arm_radius * 0.8}"
        length="${forearm_length}"/>
    </link>

    <!-- البو جوائنٹ -->
    <joint name="${side}_elbow" type="revolute">
      <parent link="${side}_upper_arm"/>
      <child link="${side}_forearm"/>

      <origin xyz="0 0 ${-upper_arm_length}" rpy="0 0 0"/>

      <axis xyz="0 1 0"/>
      <!-- البو صرف ایک ہی سمت میں مڑتا ہے -->
      <limit lower="0.0" upper="2.356" effort="80.0" velocity="2.0"/>
      <dynamics damping="0.5"/>
    </joint>

  </xacro:macro>

  <!-- سلنڈر انرٹیا کا حساب لگانے کے لئے میکرو -->
  <xacro:macro name="cylinder_inertia" params="mass radius length">
    <inertial>
      <origin xyz="0 0 ${-length/2}" rpy="0 0 0"/>
      <mass value="${mass}"/>
      <inertia
        ixx="${mass * (3*radius*radius + length*length) / 12}"
        ixy="0.0" ixz="0.0"
        iyy="${mass * (3*radius*radius + length*length) / 12}"
        iyz="0.0"
        izz="${mass * radius * radius / 2}"/>
    </inertial>
  </xacro:macro>

  <!-- ٹورسو لنک (روت) -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
      <material name="grey">
        <color rgba="0.5 0.5 0.5 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="15.0"/>
      <inertia ixx="0.4" ixy="0.0" ixz="0.0"
               iyy="0.5" iyz="0.0" izz="0.2"/>
    </inertial>
  </link>

  <!-- بائیں اور دائیں اعضا کو فعال کریں -->
  <xacro:arm_links side="left" reflect="1"/>
  <xacro:arm_links side="right" reflect="-1"/>

</robot>
```

### Xacro فائلز کی پروسیسنگ

```bash
# Xacro کو URDF میں تبدیل کریں
xacro humanoid_arm.urdf.xacro > humanoid_arm.urdf

# RViz میں دیکھیں
ros2 launch urdf_tutorial display.launch.py model:=humanoid_arm.urdf.xacro

# خامیوں کی جانچ کریں
check_urdf humanoid_arm.urdf
```

## مکمل ہیومنوائڈ URDF مثال

ایک مکمل کام کرتے ہوئے ہیومنوائڈ روبوٹ کے لئے اگلے باب (**ہفتہ 5: مکمل URDF مثال**) دیکھیں جس میں ٹورسو، اعضا، ٹانگیں، اور ہاتھ ہیں— Gazebo میں سیمولیشن اور ros2_control کے ساتھ کنٹرول کے لئے تیار۔

## بہترین طریقے

1. **سادہ روبوٹس کے علاوہ تمام کے لئے Xacro استعمال کریں**: کاپی-پیسٹ کی خامیوں سے بچیں اور آسان پیرامیٹر ٹیوننگ کی اجازت دیں
2. **انرٹیل خصوصیات کی وضاحت کریں**: فزکس سیمولیشن کو درست ماس/انرٹیا کی ضرورت ہوتی ہے
3. **کولیژن جیومیٹری کو سادہ بنائیں**: کارکردگی کے لئے پیچیدہ میشز کے بجائے بنیادی شکلیں (باکسز، سلنڈرز) استعمال کریں
4. **نامزدگی کے قواعد کو فالو کریں**: `<side>_<body_part>_<motion>` (مثلاً، `left_shoulder_pitch`) استعمال کریں
5. **حقیقی حدود سیٹ کریں**: جوائنٹ حدود ہارڈ ویئر کی خصوصیات سے مماثل ہونی چاہئیں
6. **تدریجی ٹیسٹ کریں**: روبوٹ کو لنک-بائے-لنک بنائیں، ہر اضافے کے بعد وژوئلائزیشن ٹیسٹ کریں

## اگلے اقدامات

اگلے باب **ros2_control** کو کور کرتا ہے، URDF ماڈلز کو اصل کنٹرولرز (پوزیشن، رفتار، ایفروٹ) اور ہارڈ ویئر انٹرفیسز سے منسلک کرنے کا فریم ورک۔ آپ سیکھیں گے کہ اپنے URDF روبوٹ کو سیمولیشن میں کیسے چلایا جائے اور حقیقی ہارڈ ویئر پر منتقل کیا جائے۔

### مشق ورزش

بازو Xacro میکرو کو وسعت دیں تاکہ یہ شامل ہو:
1. ایک wrist گردش جوائنٹ (کنٹینیوئس قسم)
2. دو انگلیوں والے ایک سادہ گریپر (پریزمیٹک جوائنٹس)
3. wrist پر فورس/ٹورک سینسر لنک (فکسڈ جوائنٹ)

RViz میں وژوئلائز کریں اور یقین کریں کہ جوائنٹ حدود متوقع طور پر کام کرتی ہیں۔