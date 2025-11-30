# Week 9: Isaac ROS Deployment

## Introduction to Isaac ROS

Isaac ROS is a collection of **hardware-accelerated ROS 2 packages** (called GEMs) designed to run perception and navigation algorithms on NVIDIA GPUs. These packages leverage CUDA and TensorRT to achieve 10-100x speedups over CPU-based implementations.

## Why Hardware Acceleration Matters

Humanoid robots require real-time perception for:
- **Balance control**: Processing IMU and vision data at 200+ Hz
- **Obstacle avoidance**: Detecting objects in < 50ms for dynamic environments
- **Manipulation**: 6-DOF pose estimation at 30 Hz for grasping moving objects

CPU-based perception cannot meet these latency requirements. GPU acceleration makes real-time Physical AI feasible.

## Isaac ROS Architecture

### GEM (GPU-accelerated Module) Structure

Each Isaac ROS GEM follows a standard pipeline:
1. **Input**: ROS 2 messages (images, point clouds, IMU data)
2. **GPU Processing**: CUDA kernels for parallel computation
3. **Output**: ROS 2 messages (poses, detections, maps)

```python
# Conceptual GEM pipeline
def isaac_ros_gem(input_msg):
    # Transfer data to GPU memory
    gpu_data = cuda.to_device(input_msg.data)

    # Parallel processing on thousands of CUDA cores
    result = cuda_kernel_process(gpu_data)

    # Transfer back to CPU for ROS publishing
    output_msg = cuda.from_device(result)
    return output_msg
```

## Installation on Jetson Orin

NVIDIA Jetson Orin is the recommended platform for deploying Isaac ROS on physical robots.

### Prerequisites
- **Hardware**: Jetson Orin Nano/NX/AGX (8GB+ RAM recommended)
- **JetPack**: 5.1 or later (includes CUDA, TensorRT, cuDNN)
- **ROS 2**: Humble Hawksbill

### Installation Steps

```bash
# Install Isaac ROS base dependencies
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    libopencv-dev \
    python3-opencv

# Create workspace for Isaac ROS
mkdir -p ~/isaac_ros_ws/src
cd ~/isaac_ros_ws/src

# Clone Isaac ROS common (required by all GEMs)
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git

# Clone specific GEMs (we'll use Visual SLAM)
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git

# Install dependencies using rosdep
cd ~/isaac_ros_ws
rosdep install --from-paths src --ignore-src -r -y

# Build with colcon
colcon build --symlink-install

# Source workspace
source ~/isaac_ros_ws/install/setup.bash
```

## Hardware-Accelerated Visual SLAM

Visual SLAM (Simultaneous Localization and Mapping) enables robots to build maps while tracking their position using only camera input.

### Traditional CPU VSLAM
- **ORB-SLAM3**: ~5-15 Hz on CPU, high latency
- **RTAB-Map**: ~10-20 Hz, struggles with high-resolution input

### Isaac ROS VSLAM
- **Performance**: 30-60 Hz on Jetson Orin
- **Latency**: < 33ms (suitable for real-time control)
- **Quality**: Leverages GPU for dense feature extraction

### Running Isaac ROS VSLAM

```python
# Python launch file for Isaac ROS Visual SLAM
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Camera driver node (replace with your camera)
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='camera',
            parameters=[{
                'enable_depth': True,
                'depth_module.profile': '640x480x30',  # Resolution @ FPS
                'rgb_camera.profile': '640x480x30'
            }]
        ),

        # Isaac ROS Visual SLAM node
        Node(
            package='isaac_ros_visual_slam',
            executable='isaac_ros_visual_slam',
            name='visual_slam',
            parameters=[{
                'enable_imu': False,          # Set True if IMU available
                'enable_rectified_pose': True, # Correct for camera distortion
                'denoise_input_images': True,  # GPU-accelerated denoising
                'rectified_images': True,
                'enable_debug_mode': False,
                'debug_dump_path': '/tmp/vslam_debug',
                # Feature detection parameters
                'num_cameras': 1,              # Single camera SLAM
                'min_num_images': 10,          # Keyframes before map init
                'horizontal_stereo_camera': False
            }],
            remappings=[
                # Map camera topics to VSLAM inputs
                ('stereo_camera/left/image', '/camera/color/image_raw'),
                ('stereo_camera/left/camera_info', '/camera/color/camera_info'),
                # VSLAM outputs
                ('visual_slam/tracking/odometry', '/odom'),
                ('visual_slam/tracking/vo_pose', '/vo_pose')
            ]
        ),

        # Visualization in RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', './config/vslam.rviz']
        )
    ])
```

## Stereo Vision for Depth Perception

Stereo cameras provide dense depth maps for obstacle avoidance and manipulation.

### Isaac ROS Stereo Disparity

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Stereo camera driver
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            parameters=[{
                'enable_depth': False,  # Use stereo instead of active depth
                'enable_infra1': True,  # Left IR camera
                'enable_infra2': True,  # Right IR camera
                'infra_width': 1280,
                'infra_height': 720,
                'infra_fps': 30
            }]
        ),

        # Isaac ROS Stereo Disparity (GPU-accelerated)
        Node(
            package='isaac_ros_stereo_image_proc',
            executable='disparity_node',
            parameters=[{
                'backends': 'CUDA',     # Force GPU execution
                'max_disparity': 128.0, # Max depth range
                'window_size': 5        # Matching window (odd number)
            }],
            remappings=[
                ('left/image_rect', '/camera/infra1/image_rect_raw'),
                ('left/camera_info', '/camera/infra1/camera_info'),
                ('right/image_rect', '/camera/infra2/image_rect_raw'),
                ('right/camera_info', '/camera/infra2/camera_info'),
                ('disparity', '/disparity')
            ]
        ),

        # Convert disparity to point cloud
        Node(
            package='isaac_ros_stereo_image_proc',
            executable='point_cloud_node',
            parameters=[{
                'use_color': False  # Set True if RGB available
            }],
            remappings=[
                ('disparity', '/disparity'),
                ('left/camera_info', '/camera/infra1/camera_info'),
                ('points2', '/points')
            ]
        )
    ])
```

## DNN Inference with TensorRT

Isaac ROS uses TensorRT to optimize neural networks for NVIDIA hardware.

### Converting PyTorch Model to TensorRT

```python
import torch
import torch.onnx
from torch2trt import TRTModule

# 1. Export PyTorch model to ONNX
model = torch.load('object_detector.pth')
model.eval()

dummy_input = torch.randn(1, 3, 640, 640).cuda()  # Batch size 1, 3 channels, 640x640
torch.onnx.export(
    model,
    dummy_input,
    "object_detector.onnx",
    input_names=['input'],
    output_names=['boxes', 'scores', 'classes'],
    dynamic_axes={
        'input': {0: 'batch_size'},  # Variable batch size
        'boxes': {0: 'batch_size'},
        'scores': {0: 'batch_size'}
    }
)

# 2. Convert ONNX to TensorRT engine
import tensorrt as trt

logger = trt.Logger(trt.Logger.WARNING)
builder = trt.Builder(logger)
network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
parser = trt.OnnxParser(network, logger)

# Parse ONNX model
with open('object_detector.onnx', 'rb') as model_file:
    if not parser.parse(model_file.read()):
        for error in range(parser.num_errors):
            print(parser.get_error(error))

# Configure optimization (FP16 for Jetson)
config = builder.create_builder_config()
config.set_flag(trt.BuilderFlag.FP16)  # Half-precision for 2x speedup
config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)  # 1GB

# Build optimized engine
serialized_engine = builder.build_serialized_network(network, config)
with open('object_detector.trt', 'wb') as f:
    f.write(serialized_engine)

print("TensorRT engine saved - optimized for Jetson Orin")
```

## Performance Benchmarks

| Algorithm | CPU (i7-12700) | GPU (RTX 3060) | Jetson Orin |
|-----------|----------------|----------------|-------------|
| VSLAM     | 12 Hz          | 90 Hz          | 45 Hz       |
| Stereo    | 8 Hz           | 120 Hz         | 60 Hz       |
| YOLOv8    | 15 Hz          | 180 Hz         | 80 Hz       |

## Exercises

1. **VSLAM Deployment**: Run Isaac ROS Visual SLAM with a webcam and observe pose estimates in RViz.

2. **Stereo Depth**: If you have a stereo camera, generate a point cloud and visualize it. Otherwise, use recorded ROS bags from Isaac ROS examples.

3. **TensorRT Conversion**: Convert a simple PyTorch classifier to TensorRT and measure inference time before/after.

4. **GEM Integration**: Create a launch file that runs VSLAM + stereo disparity + object detection simultaneously.

---

**Next**: [Week 9 - Perception for Manipulation](./week-9-perception.md)
