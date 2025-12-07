# ہفتہ 7: روبوٹکس کے لئے یونٹی

![Unity for Robotics](/img/ai-17.png)

## کیوں روبوٹکس کے لئے یونٹی؟

جبکہ Gazebo ROS2 انضمام میں بہتر ہے، **یونٹی** یہ فراہم کرتا ہے:

1. **فوٹو ریلسٹک رینڈرنگ**: وژن-بیسڈ پالیسیز اور سیم-ٹو-ریل ٹرانسفر کے لئے ضروری
2. **NVIDIA PhysX**: GPU ایکسلریشن کے ساتھ ہائی-پرفارمنس فزکس
3. **ML-Agents انضمام**: بلٹ ان ریفورسمنٹ لرننگ فریم ورک
4. **VR/AR سپورٹ**: انسان-روبوٹ انٹرایکشن سٹڈیز اور ٹیلی آپریشن

**یونٹی روبوٹکس ہب** یونٹی کو TCP کے ذریعے ROS2 سے جوڑتا ہے، بے داغ انضمام کو فعال کرتا ہے۔

## انسٹالیشن اور سیٹ اپ

```bash
# ضروریات: یونٹی 2021.3 LTS یا بعد کا ورژن
# یونٹی ہب https://unity.com/download سے ڈاؤن لوڈ کریں

# یونٹی میں یونٹی روبوٹکس ہب پیکجز انسٹال کریں:
# 1. یونٹی ایڈیٹر کھولیں
# 2. ونڈو → پیکج مینیجر → گٹ URL سے پیکج شامل کریں:
#    - com.unity.robotics.urdf-importer
#    - com.unity.robotics.ros-tcp-connector

# ROS2 سائیڈ انسٹال کریں (ROS-TCP-Endpoint)
cd ~/ros2_ws/src
git clone https://github.com/Unity-Technologies/ROS-TCP-Endpoint.git
cd ~/ros2_ws
colcon build --packages-select ros_tcp_endpoint
source install/setup.bash

# ROS2 اینڈ پوائنٹ (بریج) لانچ کریں
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1
```

## URDF امپورٹر: ROS سے یونٹی تک

یونٹی **articulation bodies** (PhysX خصوصیت) کا استعمال کرتا ہے ملٹی-بodies ڈائنامکس کے لئے۔ URDF امپورٹر ROS روبوٹ کی وضاحت کو یونٹی GameObjects میں تبدیل کرتا ہے۔

**ورک فلو**:

1. ROS2 ورک سپیس سے URDF ایکسپورٹ کریں (مثال: TurtleBot3)

```bash
# URDF فائل تلاش کریں
find ~/ros2_ws/src -name "*.urdf"
# مثال: ~/ros2_ws/src/turtlebot3/turtlebot3_description/urdf/turtlebot3_waffle.urdf
```

2. یونٹی میں امپورٹ کریں:
   - `Assets → Import Robot from URDF`
   - `.urdf` فائل منتخب کریں
   - **امپورٹ سیٹنگز** منتخب کریں:
     - **Mesh Decomposition**: Convex hull (تیز کولیژن)
     - **Axis Type**: Y-Up (یونٹی کنونشن)
     - **Articulation Body**: فعال

3. نتیجہ: GameObject ہائیرارکی کے ساتھ:
   - **ArticulationBody** کمپونینٹس (جوائنٹس)
   - **MeshRenderer** (وژوئل)
   - **MeshCollider** (کولیژن)

**مثال: URDF میں سادہ 2-DOF بازو**:

```xml
<!-- two_dof_arm.urdf -->
<robot name="simple_arm">
  <link name="base_link">
    <visual>
      <geometry><box size="0.1 0.1 0.2"/></geometry>
      <material name="blue"><color rgba="0 0 1 1"/></material>
    </visual>
    <collision>
      <geometry><box size="0.1 0.1 0.2"/></geometry>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.005"/>
    </inertial>
  </link>

  <joint name="shoulder_joint" type="revolute">
    <parent link="base_link"/>
    <child link="upper_arm"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 0 1"/> <!-- Z کے گرد گھومیں -->
    <limit lower="-1.57" upper="1.57" effort="10" velocity="2.0"/>
  </joint>

  <link name="upper_arm">
    <visual>
      <geometry><cylinder radius="0.05" length="0.3"/></geometry>
      <material name="red"><color rgba="1 0 0 1"/></material>
    </visual>
    <collision>
      <geometry><cylinder radius="0.05" length="0.3"/></geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.008" ixy="0" ixz="0" iyy="0.008" iyz="0" izz="0.001"/>
    </inertial>
  </link>
</robot>
```

امپورٹ کے بعد، یونٹی تخلیق کرتا ہے:
- `base_link` (GameObject کے ساتھ ArticulationBody، غیر متحرک اینکر)
- `upper_arm` (بچہ GameObject، ArticulationBody کے ساتھ revolute جوائنٹ)

## Articulation Bodies: یونٹی کا ملٹی-بodies فزکس

**ArticulationBody** یونٹی کا حل ہے روبوٹک چینز کے لئے (legacy ConfigurableJoint کی جگہ)۔ کلیدی خصوصیات:

```csharp
// C# اسکرپٹ جوائنٹ کنٹرول کے لئے (upper_arm GameObject سے منسلک کریں)
using UnityEngine;

public class JointController : MonoBehaviour
{
    private ArticulationBody articulationBody;

    void Start()
    {
        articulationBody = GetComponent<ArticulationBody>();

        // جوائنٹ ڈرائی کنفیگر کریں (PD کنٹرولر)
        var drive = articulationBody.xDrive;
        drive.stiffness = 1000f;  // P گین (پوزیشن کنٹرول)
        drive.damping = 100f;     // D گین (ولوسٹی ڈیمپنگ)
        drive.forceLimit = 10f;   // زیادہ سے زیادہ ٹورک (10 Nm)
        articulationBody.xDrive = drive;
    }

    void Update()
    {
        // ہدف پوزیشن سیٹ کریں (ڈگریز میں)
        float targetAngle = Mathf.Sin(Time.time) * 90f; // ±90° اوسیلیٹ

        var drive = articulationBody.xDrive;
        drive.target = targetAngle;
        articulationBody.xDrive = drive;

        // موجودہ جوائنٹ اسٹیٹ پڑھیں
        float currentAngle = articulationBody.jointPosition[0] * Mathf.Rad2Deg;
        float currentVelocity = articulationBody.jointVelocity[0];

        Debug.Log($"Joint Angle: {currentAngle:F2}°, Velocity: {currentVelocity:F2} rad/s");
    }
}
```

**Gazebo سے کلیدی فرق**: یونٹی **ضمنی سپرنگ-ڈیمپر ڈرائیز** (بلٹ ان PD کنٹرول) استعمال کرتا ہے، جبکہ Gazebo پلگ انز کے ذریعے بیرونی کنٹرولرز کی ضرورت ہوتی ہے۔

## PhysX انجن کنفیگریشن

یونٹی کا **PhysX** مستحکم ہیومنوائڈ سیمولیشن کے لئے ٹیوننگ کی ضرورت ہوتی ہے۔

**Project Settings → Physics**:

```csharp
// رن ٹائم پر فزکس کنفیگر کرنے کے لئے اسکرپٹ (خالی GameObject سے منسلک کریں)
using UnityEngine;

public class PhysicsConfig : MonoBehaviour
{
    void Start()
    {
        // عالمی فزکس سیٹنگز
        Physics.gravity = new Vector3(0, -9.81f, 0); // زمین کی گریویٹی
        Physics.defaultSolverIterations = 12;        // زیادہ = زیادہ مستحکم جوائنٹس
        Physics.defaultSolverVelocityIterations = 8; // ولوسٹی کنٹرینٹ اٹریشنز

        // ٹائم سیٹنگز (فزکس کے لئے فکسڈ ٹائم سٹیپ)
        Time.fixedDeltaTime = 0.01f; // 100 Hz فزکس اپ ڈیٹ (0.01s)

        // Articulation-مخصوص سیٹنگز
        Physics.ArticulationSolverIterations = 16; // ہیومنوائڈ استحکام کے لئے اہم
        Physics.ArticulationSolverVelocityIterations = 4;
    }
}
```

**استحکام ٹِپس**:
- **Solver Iterations**: ہیومنوائڈز کے لئے 16-24 تک بڑھائیں (ڈیفالٹ 6 بہت کم ہے)
- **Fixed Timestep**: 0.01s (100Hz) پر رکھیں یا ملٹی-بodies استحکام کے لئے کم
- **Continuous Collision Detection**: فاسٹ-موونگ لنکس پر فعال کریں (سوئنگ فیز کے دوران فُٹس)

## ROS2 انضمام: جوائنٹ اسٹیٹس شائع کرنا

**یونٹی → ROS2 رابطہ**:

```csharp
// ROS2 میں جوائنٹ اسٹیٹس شائع کریں (ROS-TCP-Connector کی ضرورت ہے)
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class JointStatePublisher : MonoBehaviour
{
    private ROSConnection ros;
    private ArticulationBody[] joints;
    private float publishInterval = 0.1f; // 10 Hz
    private float timer = 0f;

    void Start()
    {
        // ROS سے منسلک ہوں
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<JointStateMsg>("/joint_states");

        // روبوٹ میں تمام articulation bodies تلاش کریں
        joints = GetComponentsInChildren<ArticulationBody>();
    }

    void FixedUpdate()
    {
        timer += Time.fixedDeltaTime;

        if (timer >= publishInterval)
        {
            timer = 0f;
            PublishJointStates();
        }
    }

    void PublishJointStates()
    {
        var msg = new JointStateMsg
        {
            header = new RosMessageTypes.Std.HeaderMsg
            {
                stamp = new RosMessageTypes.Std.TimeMsg
                {
                    sec = (int)Time.time,
                    nanosec = (uint)((Time.time % 1) * 1e9)
                }
            },
            name = new string[joints.Length],
            position = new double[joints.Length],
            velocity = new double[joints.Length],
            effort = new double[joints.Length]
        };

        for (int i = 0; i < joints.Length; i++)
        {
            msg.name[i] = joints[i].name;
            msg.position[i] = joints[i].jointPosition[0]; // ریڈینز
            msg.velocity[i] = joints[i].jointVelocity[0]; // Rad/s
            msg.effort[i] = joints[i].jointForce[0];      // ٹورک (Nm)
        }

        ros.Publish("/joint_states", msg);
    }
}
```

**ROS2 سبسکرائبر (ڈیٹا کی تصدیق)**:

```bash
ros2 topic echo /joint_states
```

## یونٹی ML-Agents ریفورسمنٹ لرننگ کے لئے

یونٹی کا **ML-Agents** فریم ورک پالیسیز کو براہ راست یونٹی میں تربیت دینے کی اجازت دیتا ہے (Isaac Gym کے متبادل کے طور پر)۔

**فوری شروع**:

```csharp
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;

public class HumanoidAgent : Agent
{
    private ArticulationBody[] joints;

    public override void Initialize()
    {
        joints = GetComponentsInChildren<ArticulationBody>();
    }

    // مشاہدات: جوائنٹ پوزیشنز + رفتاریں
    public override void CollectObservations(VectorSensor sensor)
    {
        foreach (var joint in joints)
        {
            sensor.AddObservation(joint.jointPosition[0]); // پوزیشن
            sensor.AddObservation(joint.jointVelocity[0]); // رفتار
        }
    }

    // ایکشنز: ہدف جوائنٹ اینگلز
    public override void OnActionReceived(ActionBuffers actions)
    {
        for (int i = 0; i < joints.Length; i++)
        {
            var drive = joints[i].xDrive;
            drive.target = actions.ContinuousActions[i] * 90f; // ±90° رینج
            joints[i].xDrive = drive;
        }
    }

    // انعام: کھڑے ہونے کی حیثیت
    public void FixedUpdate()
    {
        float uprightBonus = transform.up.y; // 1.0 اگر مکمل طور پر عمودی
        AddReward(uprightBonus * 0.01f); // ہر اسٹیپ پر چھوٹا انعام

        if (transform.position.y < 0.5f) // گر گیا
        {
            SetReward(-1f);
            EndEpisode();
        }
    }
}
```

**ٹریننگ**: PPO الگوری دھم کے ساتھ `mlagents-learn` (پائیتھن پیکج) استعمال کریں۔

**ورزش**: ہیومنوائڈ URDF کو یونٹی میں امپورٹ کریں۔ C# اسکرپٹ تخلیق کریں جو سائنسوڈل جوائنٹ کمانڈز لگاتا ہے تاکہ روبوٹ ایک بازو کو ہلاتا ہے۔ ROS2 میں جوائنٹ اسٹیٹس شائع کریں اور RViz میں وژوئلائز کریں۔

---

**اگلا**: [ہفتہ 7 - حسب ضرورت دنیا تخلیق کرنا](./week-7-worlds.md) - زمینیں، رکاوٹیں، اور حقیقی ماحول۔