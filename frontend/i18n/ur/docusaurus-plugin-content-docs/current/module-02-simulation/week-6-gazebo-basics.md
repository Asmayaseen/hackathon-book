# ہفتہ 6: گیزبو کی بنیادیں

## انسٹالیشن اور سیٹ اپ

Gazebo ROS2 سے گہرائی سے انضمام کرتا ہے۔ ہم **Gazebo Fortress** (سابق Ignition Gazebo) استعمال کریں گے، Gazebo Classic کی جدید جگہ۔

```bash
# Ubuntu 22.04 پر Gazebo Fortress انسٹال کریں
sudo apt-get update
sudo apt-get install -y gazebo-fortress

# انسٹالیشن کی تصدیق کریں
ign gazebo --version
# متوقع آؤٹ پٹ: Gazebo Fortress 6.x.x

# Humble کے لئے ROS2 Gazebo برج انسٹال کریں
sudo apt-get install ros-humble-ros-gz-bridge ros-humble-ros-gz-sim
```

**اہم فرق**: Gazebo Classic `gazebo` کمانڈز استعمال کرتا تھا؛ Ignition/Fortress `ign gazebo` استعمال کرتا ہے۔

## SDF ماڈلز: روبوٹ کی وضاحت کی زبان

**SDF (سیمولیشن ڈسکرپشن فارمیٹ)** XML-بیسڈ ہے اور URDF سے زیادہ اظہاری ہے۔ URDF کے برعکس (kinematics کے لئے ڈیزائن شدہ)، SDF دستی طور پر ساتھ دیتا ہے:

- بند کنیمیٹک لوپس
- ایک فائل میں متعدد ماڈلز
- سینسرز اور کنٹرولرز کے لئے پلگ ان کنفیگریشنز

**مثال**: دو بازوؤں کے ساتھ ایک سادہ ہیومنوائڈ ٹورسو (وضاحت کے لئے سادہ کیا گیا)۔

```xml
<!-- humanoid_torso.sdf -->
<?xml version="1.0"?>
<sdf version="1.8">
  <model name="humanoid_torso">
    <!-- بیس لنک (ٹورسو) -->
    <link name="torso">
      <pose>0 0 1.0 0 0 0</pose> <!-- x y z roll pitch yaw -->
      <inertial>
        <mass>15.0</mass> <!-- 15 kg ٹورسو -->
        <inertia>
          <ixx>0.5</ixx> <ixy>0</ixy> <ixz>0</ixz>
          <iyy>0.6</iyy> <iyz>0</iyz> <izz>0.3</izz>
        </inertia>
      </inertial>
      <collision name="torso_collision">
        <geometry>
          <box><size>0.3 0.4 0.6</size></box> <!-- چوڑائی گہرائی اونچائی -->
        </geometry>
      </collision>
      <visual name="torso_visual">
        <geometry>
          <box><size>0.3 0.4 0.6</size></box>
        </geometry>
        <material>
          <ambient>0.2 0.2 0.8 1</ambient> <!-- نیلا ٹورسو -->
        </material>
      </visual>
    </link>

    <!-- دائیں شولڈر جوائنٹ -->
    <joint name="right_shoulder" type="revolute">
      <parent>torso</parent>
      <child>right_upper_arm</child>
      <axis>
        <xyz>1 0 0</xyz> <!-- X-axis کے گرد گھومیں (پچ) -->
        <limit>
          <lower>-1.57</lower> <!-- -90 ڈگری -->
          <upper>1.57</upper>  <!-- +90 ڈگری -->
          <effort>50</effort>   <!-- زیادہ سے زیادہ ٹورک: 50 Nm -->
          <velocity>2.0</velocity> <!-- زیادہ سے زیادہ رفتار: 2 rad/s -->
        </limit>
      </axis>
    </joint>

    <!-- دائیں اپر ارمل لنک -->
    <link name="right_upper_arm">
      <pose relative_to="right_shoulder">0 -0.25 0 0 0 0</pose>
      <inertial>
        <mass>2.0</mass>
        <inertia>
          <ixx>0.01</ixx> <ixy>0</ixy> <ixz>0</ixz>
          <iyy>0.01</iyy> <iyz>0</iyz> <izz>0.005</izz>
        </inertia>
      </inertial>
      <collision name="arm_collision">
        <geometry>
          <cylinder><radius>0.05</radius><length>0.3</length></cylinder>
        </geometry>
      </collision>
      <visual name="arm_visual">
        <geometry>
          <cylinder><radius>0.05</radius><length>0.3</length></cylinder>
        </geometry>
      </visual>
    </link>
  </model>
</sdf>
```

**اہم تصورات**:
- `<pose>`: پوزیشن (x, y, z) اور اورینٹیشن (roll, pitch, yaw ریڈینز میں)
- `<inertial>`: ماس اور مومنٹ آف انرٹیا ٹینسر (مستحکم سیمولیشن کے لئے اہم)
- `relative_to`: بچہ لنک والد جوائنٹ فریم کے رشتے میں پوزیشنز

## فزکس انجن: ODE بمقابلہ بُلیٹ

Gazebo متعدد فزکس انجن کی حمایت کرتا ہے۔ ہیومنوائڈ روبوٹکس کے لئے دو سب سے عام ہیں:

### ODE (Open Dynamics Engine)
- **فائدے**: تیز، بڑی تعداد میں کانٹیکٹس کو اچھی طرح سے ہینڈل کرتا ہے
- **نقصانات**: کم درست کانٹیکٹ ریزولوشن، "باؤنسی" ہو سکتا ہے
- **کے لئے بہتر**: ملٹی-لیگڈ روبوٹس، روغ زمین کی نیوی گیشن

### بُلیٹ
- **فائدے**: درست کولیژن ڈیٹیکشن، مستحکم اسٹیکنگ
- **نقصانات**: کئی کانٹیکٹس کے لئے سست
- **کے لئے بہتر**: مینوپولیشن کام، درست کانٹیکٹ ماڈلنگ

**ورلڈ فائل کنفیگریشن**:

```xml
<!-- world_file.sdf -->
<?xml version="1.0"?>
<sdf version="1.8">
  <world name="humanoid_world">
    <!-- فزکس انجن کا انتخاب کریں: ode، bullet، dart -->
    <physics name="default_physics" type="bullet">
      <max_step_size>0.001</max_step_size> <!-- 1ms ٹائم سٹیپ -->
      <real_time_factor>1.0</real_time_factor> <!-- ریل ٹائم رفتار پر چلائیں -->
      <real_time_update_rate>1000</real_time_update_rate> <!-- 1000 Hz -->
    </physics>

    <!-- وژوئلائزیشن کے لئے لائٹنگ -->
    <light name="sun" type="directional">
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
    </light>

    <!-- زمین کا طیل
    <model name="ground">
      <static>true</static>
      <link name="ground_link">
        <collision name="ground_collision">
          <geometry>
            <plane><normal>0 0 1</normal></plane>
          </geometry>
          <surface>
            <friction>
              <ode><mu>1.0</mu></ode> <!-- فرکشن کوائفیشینٹ -->
            </friction>
          </surface>
        </collision>
      </link>
    </model>

    <!-- ہمارے ہیومنوائڈ ماڈل شامل کریں -->
    <include>
      <uri>file://humanoid_torso.sdf</uri>
      <pose>0 0 1.5 0 0 0</pose> <!-- زمین سے 1.5م اوپر اسپون کریں -->
    </include>
  </world>
</sdf>
```

## روبوٹس اسپون کرنا اور سیمولیشن چلانا

```bash
# ورلڈ فائل کے ساتھ Gazebo لانچ کریں
ign gazebo world_file.sdf

# متبادل: کمانڈ کے ذریعے ماڈل کو ڈائنامک طور پر اسپون کریں
ign service -s /world/humanoid_world/create \
  --reqtype ignition.msgs.EntityFactory \
  --reptype ignition.msgs.Boolean \
  --timeout 1000 \
  --req 'sdf_filename: "humanoid_torso.sdf", pose: {position: {z: 2.0}}'
```

**ورزش**: `humanoid_torso.sdf` کو بائیں بازو شامل کرنے کے لئے تبدیل کریں (دائیں بازو کو عکس دہرائیں)۔ انرٹیا اقدار کو ایڈجسٹ کریں اور تصدیق کریں کہ روبوٹ کو اسپون کرتے وقت گرتا نہیں ہے۔

---

**اگلا**: [ہفتہ 6 - فزکس کنفیگریشن](./week-6-physics.md) - حقیقی ہیومنوائڈ رویے کے لئے کولیژن، فرکشن، اور کانٹیکٹ فورسز کو ٹیون کرنا۔