# ہفتہ 9: مینوپولیشن کے لئے ادراک

![Perception for Manipulation](/img/ai-10.png)

## مینوپولیشن ادراک کا چیلنج

روبوٹک مینوپولیشن کو ملی میٹر کی درستگی کے ساتھ اشیاء کی **6-DOF پوز** (3D پوزیشن + 3D اورینٹیشن) جاننے کی ضرورت ہوتی ہے۔ ایک ہیومنوائڈ روبوٹ کو جام گھونٹنے کے لئے لازمی طور پر معلوم ہونا چاہیے:
- **پوزیشن (x, y, z)**: جام کا مرکز کہاں ہے؟
- **اورینٹیشن (roll, pitch, yaw)**: جام کیسے گھوما ہوا ہے؟

روایتی 2D اشیاء کی شناخت صرف باؤنڈنگ باکسز فراہم کرتی ہے، 3D گریسنگ کے لئے ناکافی ہے۔

## اشیاء کی شناخت بمقابلہ پوز ایسٹیمیشن

### 2D اشیاء کی شناخت
- **آؤٹ پٹ**: [x, y, چوڑائی, اونچائی, کلاس, یقین]
- **استعمال کا مقصد**: "کیا تصویر میں جام ہے؟"
- **محدودیت**: کوئی ڈیپتھ یا اورینٹیشن کی معلومات نہیں

### 6-DOF پوز ایسٹیمیشن
- **آؤٹ پٹ**: [x, y, z, qw, qx, qy, qz, کلاس, یقین]
- **استعمال کا مقصد**: "3D سپیس میں جام بالکل کہاں ہے؟"
- **قابل فعال**: گریس پلاننگ، کالیژن ایوائڈنس، درست پلیسمنٹ

## DOPE: ڈیپ آبجیکٹ پوز ایسٹیمیشن

DOPE (ڈیپ آبجیکٹ پوز ایسٹیمیشن) ایک CNN ہے جو RGB امیجز سے 6-DOF پوزز کی پیشن گوئی کرتا ہے۔ سینتھیٹک Isaac Sim ڈیٹا پر تربیت یافتہ، DOPE ڈومین رینڈمائزیشن کے ذریعے حقیقی دنیا کی درستگی حاصل کرتا ہے۔

### DOPE آرکیٹیکچر

```python
# تصوراتی DOPE پائپ لائن
def dope_inference(rgb_image):
    # 1. فیچر ایکسٹریکشن (ResNet بیک بون)
    features = resnet50(rgb_image)

    # 2. 3D کی پوائنٹس کے لئے عقیدت کے نقشے (مثلاً، اشیاء کے کونے)
    belief_maps = conv2d(features, num_keypoints=8)

    # 3. PnP الگوری دھم 2D کی پوائنٹس سے 6-DOF پوز بازیافت کرنے کے لئے
    keypoints_2d = find_peaks(belief_maps)
    pose_6dof = solve_pnp(keypoints_2d, keypoints_3d_model, camera_matrix)

    return pose_6dof  # [x, y, z, quaternion]
```

### Isaac ROS DOPE چلانا

```python
# DOPE اشیاء کی پوز ایسٹیمیشن کے لئے لانچ فائل
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # مخصوص اشیاء کے لئے تربیت یافتہ DOPE ماڈل کا راستہ
    model_path = LaunchConfiguration('model_path', default='/workspaces/isaac_ros-dev/models/dope_soup_60.onnx')

    return LaunchDescription([
        # کیمرہ ان پٹ
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            parameters=[{
                'rgb_camera.profile': '640x480x30',
                'depth_module.profile': '640x480x30',
                'enable_depth': True,
                'align_depth.enable': True  # ڈیپتھ کو RGB سے مطابقت دیں
            }]
        ),

        # DOPE انفرس نوڈ (TensorRT-ایکسلریٹڈ)
        Node(
            package='isaac_ros_dope',
            executable='dope_decoder',
            name='dope',
            parameters=[{
                'object_name': 'soup_can',      # اس ماڈل کے لئے اشیاء کی کلاس
                'model_file_path': model_path,
                'configuration_file': '/workspaces/isaac_ros-dev/config/dope_config.yaml',
                # اشیاء کے ابعاد میٹر میں (PnP کے لئے)
                'object_dimensions': [0.067, 0.067, 0.103],  # [چوڑائی, گہرائی, اونچائی]
                # ڈیٹیکشن تھریش ہولڈ
                'map_peak_threshold': 0.1
            }],
            remappings=[
                ('image', '/camera/color/image_raw'),
                ('camera_info', '/camera/color/camera_info'),
                ('dope/pose_array', '/poses')  # آؤٹ پٹ: PoseArray میسج
            ]
        ),

        # TF براڈکاسٹر روبوٹ فریم میں اشیاء کی پوز شائع کرنے کے لئے
        Node(
            package='isaac_ros_dope',
            executable='dope_pose_to_tf',
            parameters=[{
                'object_frame_id': 'soup_can',
                'reference_frame_id': 'camera_color_optical_frame'
            }],
            remappings=[
                ('dope/pose_array', '/poses')
            ]
        ),

        # وژوئلائزیشن
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', './config/dope_visualization.rviz']
        )
    ])
```

## حسب ضرورت اشیاء پر DOPE تربیت دینا

اپنی اشیاء کو ڈیٹیکٹ کرنے کے لئے، Isaac Sim کے سینتھیٹک ڈیٹا کا استعمال کرتے ہوئے DOPE تربیت دیں:

### قدم 1: سینتھیٹک تربیت ڈیٹا تخلیق کریں

```python
import omni.replicator.core as rep
from omni.isaac.kit import SimulationApp

simulation_app = SimulationApp({"headless": True})

# اپنی حسب ضرورت اشیاء لوڈ کریں (مثلاً، حسب ضرورت ٹول)
custom_object = rep.create.from_usd(
    "./assets/custom_tool.usd",
    semantics=[("class", "custom_tool")]
)

def randomize_scene():
    # اشیاء کی پوز بے ترتیب کریں
    with custom_object:
        rep.modify.pose(
            position=rep.distribution.uniform((-0.3, -0.3, 0.5), (0.3, 0.3, 0.8)),
            rotation=rep.distribution.uniform((0, 0, 0), (360, 360, 360))
        )
        # ظہور کو بے ترتیب کریں
        rep.randomizer.color(
            colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
        )

    # لائٹنگ کو بے ترتیب کریں
    light = rep.create.light(
        light_type="Dome",
        intensity=rep.distribution.uniform(500, 2000)
    )

    return custom_object

rep.randomizer.register(randomize_scene)

# ڈیٹا کیپچر کے لئے کیمرہ
camera = rep.create.camera(
    position=(1.0, 1.0, 0.6),
    look_at=(0, 0, 0.5)
)

# DOPE کو RGB + کی پوائنٹ اینوٹیشنز کی ضرورت ہے
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="./dope_training_data",
    rgb=True,
    bounding_box_2d_tight=True,
    bounding_box_3d=True  # DOPE تربیت کے لئے 3D کی پوائنٹس
)
writer.attach([camera])

# 10,000 تربیتی امیجز تخلیق کریں
with rep.trigger.on_frame(num_frames=10000):
    rep.randomizer.randomize_scene()

rep.orchestrator.run()
simulation_app.close()
```

### قدم 2: DOPE ماڈل تربیت دیں

```bash
# DOPE تربیت ریپوزٹری کلون کریں
git clone https://github.com/NVlabs/Deep_Object_Pose.git
cd Deep_Object_Pose

# ڈیٹا تیار کریں (Isaac Sim آؤٹ پٹ کو DOPE فارمیٹ میں تبدیل کریں)
python scripts/prepare_isaac_sim_data.py \
    --input_dir ./dope_training_data \
    --output_dir ./dope_formatted

# DOPE نیٹ ورک تربیت دیں
python train.py \
    --data ./dope_formatted \
    --object custom_tool \
    --epochs 60 \
    --batch_size 32 \
    --gpus 1

# TensorRT آپٹیمائزیشن کے لئے ONNX میں ایکسپورٹ کریں
python export_onnx.py \
    --checkpoint ./checkpoints/custom_tool_epoch60.pth \
    --output custom_tool.onnx
```

## مینوپولیشن کے لئے ڈیپتھ ادراک

ڈیپتھ سینسرز گریس پلاننگ کے لئے ضروری فاصلے کی پیمائش فراہم کرتے ہیں۔

### DOPE کے ساتھ ڈیپتھ کا انضمام

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np

class DepthEnhancedPose(Node):
    def __init__(self):
        super().__init__('depth_enhanced_pose')

        # DOPE پوزز کے لئے سبسکرائب کریں
        self.pose_sub = self.create_subscription(
            PoseArray,
            '/poses',
            self.pose_callback,
            10
        )

        # ڈیپتھ امیج کے لئے سبسکرائب کریں
        self.depth_sub = self.create_subscription(
            Image,
            '/camera/aligned_depth_to_color/image_raw',
            self.depth_callback,
            10
        )

        self.bridge = CvBridge()
        self.latest_depth = None

    def depth_callback(self, msg):
        # ROS ڈیپتھ امیج کو numpy ارے میں تبدیل کریں
        self.latest_depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')

    def pose_callback(self, msg):
        if self.latest_depth is None:
            return

        for pose in msg.poses:
            # DOPE پوز ایسٹیمیٹ فراہم کرتا ہے، لیکن ڈیپتھ Z کوآرڈینیٹ کو صاف کر سکتا ہے
            # پوز کو امیج کوآرڈینیٹس میں پروجیکٹ کریں
            u, v = self.project_to_image(pose.position)

            # اس پکسل پر ڈیپتھ دیکھیں
            if 0 <= u < self.latest_depth.shape[1] and 0 <= v < self.latest_depth.shape[0]:
                measured_depth = self.latest_depth[v, u]

                # Z کوآرڈینیٹ کو ڈیپتھ سینسر کا استعمال کرتے ہوئے صاف کریں
                refined_z = measured_depth * 0.001  # ملی میٹر کو میٹر میں تبدیل کریں

                self.get_logger().info(
                    f"DOPE Z: {pose.position.z:.3f}m, "
                    f"Depth Z: {refined_z:.3f}m, "
                    f"Error: {abs(pose.position.z - refined_z)*1000:.1f}mm"
                )

    def project_to_image(self, position):
        # کیمرہ انٹرنسکس (اصل اقدار کو camera_info سے تبدیل کریں)
        fx, fy = 615.0, 615.0  # فوکل لمبائیاں
        cx, cy = 320.0, 240.0  # مرکزی پوائنٹ

        # 3D پوائنٹ کو 2D امیج میں پروجیکٹ کریں
        u = int(fx * position.x / position.z + cx)
        v = int(fy * position.y / position.z + cy)
        return u, v

def main():
    rclpy.init()
    node = DepthEnhancedPose()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 6-DOF پوزز کے ساتھ گریس پلاننگ

ایک بار جب آپ کے پاس اشیاء کی پوز ہو جاتی ہے، گریس کنفیگریشنز کا حساب لگائیں:

```python
import numpy as np
from scipy.spatial.transform import Rotation

def plan_top_down_grasp(object_pose):
    """
    ایک جانی پہچانی اشیاء کے لئے ایک سادہ ٹاپ ڈاؤن گریس منصوبہ بندی کریں۔

    Args:
        object_pose: geometry_msgs/Pose اشیاء کی
    Returns:
        grasp_pose: گریسنگ کے لئے مطلوبہ اینڈ ایفیکٹر پوز
    """
    # اشیاء کی پوزیشن نکالیں
    obj_pos = np.array([
        object_pose.position.x,
        object_pose.position.y,
        object_pose.position.z
    ])

    # گریس ایپروچ: اشیاء کے اوپر 10سینٹی میٹر، گریپر نیچے کی طرف
    grasp_offset = np.array([0, 0, 0.10])  # 10سینٹی میٹر اوپر
    grasp_pos = obj_pos + grasp_offset

    # گریپر اورینٹیشن: Z-ایکسز نیچے کی طرف
    grasp_rot = Rotation.from_euler('xyz', [180, 0, 0], degrees=True)

    # گریپر کو اشیاء کی اورینٹیشن کے ساتھ مطابقت دیں (غیر متناظر اشیاء کے لئے)
    obj_rot = Rotation.from_quat([
        object_pose.orientation.x,
        object_pose.orientation.y,
        object_pose.orientation.z,
        object_pose.orientation.w
    ])

    # مجموعی گردش
    final_rot = obj_rot * grasp_rot

    return grasp_pos, final_rot.as_quat()
```

## ورزشیں

1. **DOPE ڈیپلائمنٹ**: ایک پیش تربیت یافتہ ماڈل (soup can یا cracker box) کے ساتھ Isaac ROS DOPE چلائیں اور RViz میں ڈیٹیکشنز وژوئلائز کریں۔

2. **ڈیپتھ فیوژن**: DepthEnhancedPose نوڈ لاگو کریں اور DOPE Z ایسٹیمیٹس کو ڈیپتھ سینسر پیمائش سے موازنہ کریں۔

3. **حسب ضرورت اشیاء کی شناخت**: ایک گھریلو اشیاء منتخب کریں، Isaac Sim میں 1000 سینتھیٹک تربیتی امیجز تخلیق کریں، اور DOPE ماڈل تربیت دیں۔

4. **گریس پلاننگ**: ڈیٹیکٹ کی گئی اشیاء کی پوز کے مطابق، گریس پوز کا حساب لگائیں اور اسے TF فریم کے طور پر شائع کریں۔

---

**اگلا**: [ہفتہ 10 - Nav2 کے ساتھ نیوی گیشن](./week-10-nav2.md)