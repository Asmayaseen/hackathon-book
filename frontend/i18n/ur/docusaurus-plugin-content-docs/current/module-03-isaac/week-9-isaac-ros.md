# ہفتہ 9: Isaac ROS ڈیپلائمنٹ

## Isaac ROS کا تعارف

Isaac ROS **ہارڈ ویئر-ایکسلریٹڈ ROS 2 پیکجز** (GEMs کہا جاتا ہے) کا مجموعہ ہے جو NVIDIA GPU پر ادراک اور نیوی گیشن الگوری دھم چلانے کے لئے ڈیزائن کیا گیا ہے۔ یہ پیکجز CUDA اور TensorRT کا فائدہ اٹھاتے ہیں CPU-بیسڈ امپلیمنٹیشنز پر 10-100x اسپیڈ اپ حاصل کرنے کے لئے۔

## کیوں ہارڈ ویئر ایکسلریشن اہم ہے

ہیومنوائڈ روبوٹس کو ریل ٹائم ادراک کی ضرورت ہوتی ہے:
- **توازن کنٹرول**: 200+ Hz پر IMU اور وژن ڈیٹا کی پروسیسنگ
- **رکاوٹ سے بچاؤ**: متحرک ماحول کے لئے < 50ms میں اشیاء کو ڈیٹیکٹ کرنا
- **مینوپولیشن**: 6-DOF پوز کا تخمینہ 30 Hz پر چلتی ہوئی اشیاء کو تھامنے کے لئے

CPU-بیسڈ ادراک ان لیسی تقاضوں کو پورا نہیں کر سکتا۔ GPU ایکسلریشن ریل ٹائم فزیکل AI کو ممکن بناتا ہے۔

## Isaac ROS آرکیٹیکچر

### GEM (GPU-ایکسلریٹڈ ماڈیول) سٹرکچر

ہر Isaac ROS GEM ایک معیاری پائپ لائن پر عمل کرتا ہے:
1. **ان پٹ**: ROS 2 پیغامات (امیجز، پوائنٹ کلاؤڈز، IMU ڈیٹا)
2. **GPU پروسیسنگ**: متوازی کمپیوٹیشن کے لئے CUDA کرنلز
3. **آؤٹ پٹ**: ROS 2 پیغامات (پوزز، ڈیٹیکشنز، میپس)

```python
# تصوراتی GEM پائپ لائن
def isaac_ros_gem(input_msg):
    # ڈیٹا کو GPU میموری میں منتقل کریں
    gpu_data = cuda.to_device(input_msg.data)

    # ہزاروں CUDA کورز پر متوازی پروسیسنگ
    result = cuda_kernel_process(gpu_data)

    # ROS پبلشنگ کے لئے CPU میں واپس منتقل کریں
    output_msg = cuda.from_device(result)
    return output_msg
```

## Jetson Orin پر انسٹالیشن

NVIDIA Jetson Orin جسمانی روبوٹس پر Isaac ROS ڈیپلائے کرنے کے لئے تجویز کردہ پلیٹ فارم ہے۔

### ضروریات

- **ہارڈ ویئر**: Jetson Orin Nano/NX/AGX (8GB+ RAM تجویز کردہ)
- **JetPack**: 5.1 یا بعد کا (CUDA، TensorRT، cuDNN شامل ہے)
- **ROS 2**: Humble Hawksbill

### انسٹالیشن اسٹیپس

```bash
# Isaac ROS بیس کی ضروریات انسٹال کریں
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    libopencv-dev \
    python3-opencv

# Isaac ROS کے لئے ورک سپیس تخلیق کریں
mkdir -p ~/isaac_ros_ws/src
cd ~/isaac_ros_ws/src

# Isaac ROS عام کلون کریں (تمام GEMs کے لئے ضروری)
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git

# مخصوص GEMs کلون کریں (ہم VSLAM استعمال کریں گے)
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git

# rosdep کا استعمال کرتے ہوئے ضروریات انسٹال کریں
cd ~/isaac_ros_ws
rosdep install --from-paths src --ignore-src -r -y

# colcon کے ساتھ تعمیر کریں
colcon build --symlink-install

# ورک سپیس سورس کریں
source ~/isaac_ros_ws/install/setup.bash
```

## ہارڈ ویئر-ایکسلریٹڈ وژوئل SLAM

وژوئل SLAM (ہم آہنگ مقام کی دریافت اور میپنگ) روبوٹس کو میپس تعمیر کرنے کے قابل بناتا ہے جبکہ صرف کیمرہ ان پٹ کا استعمال کرتے ہوئے اپنی پوزیشن ٹریک کرتے ہیں۔

### روایتی CPU VSLAM
- **ORB-SLAM3**: CPU پر ~5-15 Hz، زیادہ لیسی
- **RTAB-Map**: ~10-20 Hz، زیادہ ریزولوشن ان پٹ کے ساتھ مشکل میں ہوتا ہے

### Isaac ROS VSLAM
- **کارکردگی**: Jetson Orin پر 30-60 Hz
- **لیسی**: < 33ms (ریل ٹائم کنٹرول کے لئے مناسب)
- **معیار**: گھن ویژن ایکٹریکشن کے لئے GPU کا فائدہ اٹھاتا ہے

### Isaac ROS VSLAM چلانا

```python
# Isaac ROS وژوئل SLAM کے لئے پائیتھن لانچ فائل
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # کیمرہ ڈرائیور نوڈ (اپنے کیمرہ کو تبدیل کریں)
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='camera',
            parameters=[{
                'enable_depth': True,
                'depth_module.profile': '640x480x30',  # ریزولوشن @ FPS
                'rgb_camera.profile': '640x480x30'
            }]
        ),

        # Isaac ROS وژوئل SLAM نوڈ
        Node(
            package='isaac_ros_visual_slam',
            executable='isaac_ros_visual_slam',
            name='visual_slam',
            parameters=[{
                'enable_imu': False,          # اگر IMU دستیاب ہو تو True سیٹ کریں
                'enable_rectified_pose': True, # کیمرہ ڈسٹورشن کے لئے درست کریں
                'denoise_input_images': True,  # GPU-ایکسلریٹڈ ڈی نوائسنگ
                'rectified_images': True,
                'enable_debug_mode': False,
                'debug_dump_path': '/tmp/vslam_debug',
                # ویژن ایکٹریکشن پیرامیٹرز
                'num_cameras': 1,              # سنگل کیمرہ SLAM
                'min_num_images': 10,          # میپ شروع کرنے سے پہلے کلیدی فریم
                'horizontal_stereo_camera': False
            }],
            remappings=[
                # کیمرہ ٹاپکس کو VSLAM ان پٹس میں میپ کریں
                ('stereo_camera/left/image', '/camera/color/image_raw'),
                ('stereo_camera/left/camera_info', '/camera/color/camera_info'),
                # VSLAM آؤٹ پٹس
                ('visual_slam/tracking/odometry', '/odom'),
                ('visual_slam/tracking/vo_pose', '/vo_pose')
            ]
        ),

        # RViz میں وژوئلائزیشن
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', './config/vslam.rviz']
        )
    ])
```

## ڈیپتھ ادراک کے لئے اسٹیریو وژن

اسٹیریو کیمرز رکاوٹ سے بچاؤ اور مینوپولیشن کے لئے گھن ڈیپتھ میپس فراہم کرتے ہیں۔

### Isaac ROS اسٹیریو ڈسپیرٹی

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # اسٹیریو کیمرہ ڈرائیور
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            parameters=[{
                'enable_depth': False,  # ایکٹو ڈیپتھ کے بجائے اسٹیریو استعمال کریں
                'enable_infra1': True,  # بائیں IR کیمرہ
                'enable_infra2': True,  # دائیں IR کیمرہ
                'infra_width': 1280,
                'infra_height': 720,
                'infra_fps': 30
            }]
        ),

        # Isaac ROS اسٹیریو ڈسپیرٹی (GPU-ایکسلریٹڈ)
        Node(
            package='isaac_ros_stereo_image_proc',
            executable='disparity_node',
            parameters=[{
                'backends': 'CUDA',     # GPU ایکزیکیوشن پر مجبور کریں
                'max_disparity': 128.0, # زیادہ سے زیادہ ڈیپتھ رینج
                'window_size': 5        # میچنگ ونڈو (اکثر نمبر)
            }],
            remappings=[
                ('left/image_rect', '/camera/infra1/image_rect_raw'),
                ('left/camera_info', '/camera/infra1/camera_info'),
                ('right/image_rect', '/camera/infra2/image_rect_raw'),
                ('right/camera_info', '/camera/infra2/camera_info'),
                ('disparity', '/disparity')
            ]
        ),

        # ڈسپیرٹی کو پوائنٹ کلاؤڈ میں تبدیل کریں
        Node(
            package='isaac_ros_stereo_image_proc',
            executable='point_cloud_node',
            parameters=[{
                'use_color': False  # اگر RGB دستیاب ہو تو True سیٹ کریں
            }],
            remappings=[
                ('disparity', '/disparity'),
                ('left/camera_info', '/camera/infra1/camera_info'),
                ('points2', '/points')
            ]
        )
    ])
```

## TensorRT کے ساتھ DNN انفرس

Isaac ROS TensorRT کا استعمال NVIDIA ہارڈ ویئر کے لئے نیورل نیٹ ورکس کو بہتر بنانے کے لئے کرتا ہے۔

### PyTorch ماڈل کو TensorRT میں تبدیل کرنا

```python
import torch
import torch.onnx
from torch2trt import TRTModule

# 1. PyTorch ماڈل کو ONNX میں ایکسپورٹ کریں
model = torch.load('object_detector.pth')
model.eval()

dummy_input = torch.randn(1, 3, 640, 640).cuda()  # بیچ سائز 1، 3 چینلز، 640x640
torch.onnx.export(
    model,
    dummy_input,
    "object_detector.onnx",
    input_names=['input'],
    output_names=['boxes', 'scores', 'classes'],
    dynamic_axes={
        'input': {0: 'batch_size'},  # متغیر بیچ سائز
        'boxes': {0: 'batch_size'},
        'scores': {0: 'batch_size'}
    }
)

# 2. ONNX کو TensorRT انجن میں تبدیل کریں
import tensorrt as trt

logger = trt.Logger(trt.Logger.WARNING)
builder = trt.Builder(logger)
network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
parser = trt.OnnxParser(network, logger)

# ONNX ماڈل کو پارس کریں
with open('object_detector.onnx', 'rb') as model_file:
    if not parser.parse(model_file.read()):
        for error in range(parser.num_errors):
            print(parser.get_error(error))

# آپٹیمائزیشن کنفیگر کریں (FP16 Jetson کے لئے)
config = builder.create_builder_config()
config.set_flag(trt.BuilderFlag.FP16)  # نصف-درستگی 2x اسپیڈ اپ کے لئے
config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)  # 1GB

# آپٹیمائزڈ انجن تعمیر کریں
serialized_engine = builder.build_serialized_network(network, config)
with open('object_detector.trt', 'wb') as f:
    f.write(serialized_engine)

print("TensorRT انجن محفوظ - Jetson Orin کے لئے بہتر")
```

## کارکردگی کے معیار

| الگوری دھم | CPU (i7-12700) | GPU (RTX 3060) | Jetson Orin |
|-----------|----------------|----------------|-------------|
| VSLAM     | 12 Hz          | 90 Hz          | 45 Hz       |
| اسٹیریو   | 8 Hz           | 120 Hz         | 60 Hz       |
| YOLOv8    | 15 Hz          | 180 Hz         | 80 Hz       |

## ورزشیں

1. **VSLAM ڈیپلائمنٹ**: ایک ویب کیمرہ کے ساتھ Isaac ROS وژوئل SLAM چلائیں اور RViz میں پوز تخمینہ دیکھیں۔

2. **اسٹیریو ڈیپتھ**: اگر آپ کے پاس اسٹیریو کیمرہ ہے، تو پوائنٹ کلاؤڈ تخلیق کریں اور وژوئلائز کریں۔ بصورت دیگر، Isaac ROS مثالوں سے ریکارڈ کردہ ROS bags استعمال کریں۔

3. **TensorRT تبدیلی**: ایک سادہ PyTorch کلاسیفائر کو TensorRT میں تبدیل کریں اور پہلے/بعد میں انفرس ٹائم ناپیں۔

4. **GEM انضمام**: ایک لانچ فائل تخلیق کریں جو VSLAM + اسٹیریو ڈسپیرٹی + اشیاء کی شناخت کو ایک ساتھ چلاتا ہے۔

---

**اگلا**: [ہفتہ 9 - مینوپولیشن کے لئے ادراک](./week-9-perception.md)