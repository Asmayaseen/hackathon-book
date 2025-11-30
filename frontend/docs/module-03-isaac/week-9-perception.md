# Week 9: Perception for Manipulation

![Perception for Manipulation](/img/ai-10.png)

## The Manipulation Perception Challenge

Robotic manipulation requires knowing the **6-DOF pose** (3D position + 3D orientation) of objects with millimeter-level accuracy. A humanoid robot grasping a cup must know:
- **Position (x, y, z)**: Where is the cup's center?
- **Orientation (roll, pitch, yaw)**: How is the cup rotated?

Traditional 2D object detection only provides bounding boxes, insufficient for 3D grasping.

## Object Detection vs. Pose Estimation

### 2D Object Detection
- **Output**: [x, y, width, height, class, confidence]
- **Use Case**: "Is there a cup in the image?"
- **Limitation**: No depth or orientation information

### 6-DOF Pose Estimation
- **Output**: [x, y, z, qw, qx, qy, qz, class, confidence]
- **Use Case**: "Where exactly is the cup in 3D space?"
- **Enables**: Grasp planning, collision avoidance, precise placement

## DOPE: Deep Object Pose Estimation

DOPE (Deep Object Pose Estimation) is a CNN that predicts 6-DOF poses from RGB images. Trained on synthetic Isaac Sim data, DOPE achieves real-world accuracy through domain randomization.

### DOPE Architecture

```python
# Conceptual DOPE pipeline
def dope_inference(rgb_image):
    # 1. Feature extraction (ResNet backbone)
    features = resnet50(rgb_image)

    # 2. Belief maps for 3D keypoints (e.g., object corners)
    belief_maps = conv2d(features, num_keypoints=8)

    # 3. PnP algorithm to recover 6-DOF pose from 2D keypoints
    keypoints_2d = find_peaks(belief_maps)
    pose_6dof = solve_pnp(keypoints_2d, keypoints_3d_model, camera_matrix)

    return pose_6dof  # [x, y, z, quaternion]
```

### Running Isaac ROS DOPE

```python
# Launch file for DOPE object pose estimation
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Path to trained DOPE model for specific object
    model_path = LaunchConfiguration('model_path', default='/workspaces/isaac_ros-dev/models/dope_soup_60.onnx')

    return LaunchDescription([
        # Camera input
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            parameters=[{
                'rgb_camera.profile': '640x480x30',
                'depth_module.profile': '640x480x30',
                'enable_depth': True,
                'align_depth.enable': True  # Align depth to RGB
            }]
        ),

        # DOPE inference node (TensorRT-accelerated)
        Node(
            package='isaac_ros_dope',
            executable='dope_decoder',
            name='dope',
            parameters=[{
                'object_name': 'soup_can',      # Object class this model detects
                'model_file_path': model_path,
                'configuration_file': '/workspaces/isaac_ros-dev/config/dope_config.yaml',
                # Object dimensions in meters (for PnP)
                'object_dimensions': [0.067, 0.067, 0.103],  # [width, depth, height]
                # Detection threshold
                'map_peak_threshold': 0.1
            }],
            remappings=[
                ('image', '/camera/color/image_raw'),
                ('camera_info', '/camera/color/camera_info'),
                ('dope/pose_array', '/poses')  # Output: PoseArray message
            ]
        ),

        # TF broadcaster to publish object pose in robot frame
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

        # Visualization
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', './config/dope_visualization.rviz']
        )
    ])
```

## Training DOPE on Custom Objects

To detect your own objects, train DOPE using synthetic data from Isaac Sim:

### Step 1: Generate Synthetic Training Data

```python
import omni.replicator.core as rep
from omni.isaac.kit import SimulationApp

simulation_app = SimulationApp({"headless": True})

# Load your custom object (e.g., custom tool)
custom_object = rep.create.from_usd(
    "./assets/custom_tool.usd",
    semantics=[("class", "custom_tool")]
)

def randomize_scene():
    # Randomize object pose
    with custom_object:
        rep.modify.pose(
            position=rep.distribution.uniform((-0.3, -0.3, 0.5), (0.3, 0.3, 0.8)),
            rotation=rep.distribution.uniform((0, 0, 0), (360, 360, 360))
        )
        # Randomize appearance
        rep.randomizer.color(
            colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
        )

    # Randomize lighting
    light = rep.create.light(
        light_type="Dome",
        intensity=rep.distribution.uniform(500, 2000)
    )

    return custom_object

rep.randomizer.register(randomize_scene)

# Camera for data capture
camera = rep.create.camera(
    position=(1.0, 1.0, 0.6),
    look_at=(0, 0, 0.5)
)

# DOPE requires RGB + keypoint annotations
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="./dope_training_data",
    rgb=True,
    bounding_box_2d_tight=True,
    bounding_box_3d=True  # 3D keypoints for DOPE training
)
writer.attach([camera])

# Generate 10,000 training images
with rep.trigger.on_frame(num_frames=10000):
    rep.randomizer.randomize_scene()

rep.orchestrator.run()
simulation_app.close()
```

### Step 2: Train DOPE Model

```bash
# Clone DOPE training repository
git clone https://github.com/NVlabs/Deep_Object_Pose.git
cd Deep_Object_Pose

# Prepare dataset (convert Isaac Sim output to DOPE format)
python scripts/prepare_isaac_sim_data.py \
    --input_dir ./dope_training_data \
    --output_dir ./dope_formatted

# Train DOPE network
python train.py \
    --data ./dope_formatted \
    --object custom_tool \
    --epochs 60 \
    --batch_size 32 \
    --gpus 1

# Export to ONNX for TensorRT optimization
python export_onnx.py \
    --checkpoint ./checkpoints/custom_tool_epoch60.pth \
    --output custom_tool.onnx
```

## Depth Perception for Manipulation

Depth sensors provide distance measurements critical for grasp planning.

### Integrating Depth with DOPE

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

        # Subscribe to DOPE poses
        self.pose_sub = self.create_subscription(
            PoseArray,
            '/poses',
            self.pose_callback,
            10
        )

        # Subscribe to depth image
        self.depth_sub = self.create_subscription(
            Image,
            '/camera/aligned_depth_to_color/image_raw',
            self.depth_callback,
            10
        )

        self.bridge = CvBridge()
        self.latest_depth = None

    def depth_callback(self, msg):
        # Convert ROS depth image to numpy array
        self.latest_depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')

    def pose_callback(self, msg):
        if self.latest_depth is None:
            return

        for pose in msg.poses:
            # DOPE provides pose estimate, but depth can refine Z coordinate
            # Project pose to image coordinates
            u, v = self.project_to_image(pose.position)

            # Look up depth at that pixel
            if 0 <= u < self.latest_depth.shape[1] and 0 <= v < self.latest_depth.shape[0]:
                measured_depth = self.latest_depth[v, u]

                # Refine pose Z coordinate using depth sensor
                refined_z = measured_depth * 0.001  # Convert mm to meters

                self.get_logger().info(
                    f"DOPE Z: {pose.position.z:.3f}m, "
                    f"Depth Z: {refined_z:.3f}m, "
                    f"Error: {abs(pose.position.z - refined_z)*1000:.1f}mm"
                )

    def project_to_image(self, position):
        # Camera intrinsics (replace with actual values from camera_info)
        fx, fy = 615.0, 615.0  # Focal lengths
        cx, cy = 320.0, 240.0  # Principal point

        # Project 3D point to 2D image
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

## Grasp Planning with 6-DOF Poses

Once you have object poses, compute grasp configurations:

```python
import numpy as np
from scipy.spatial.transform import Rotation

def plan_top_down_grasp(object_pose):
    """
    Plan a simple top-down grasp for a known object.

    Args:
        object_pose: geometry_msgs/Pose of the object

    Returns:
        grasp_pose: Desired end-effector pose for grasping
    """
    # Extract object position
    obj_pos = np.array([
        object_pose.position.x,
        object_pose.position.y,
        object_pose.position.z
    ])

    # Grasp approach: 10cm above object, gripper pointing down
    grasp_offset = np.array([0, 0, 0.10])  # 10cm above
    grasp_pos = obj_pos + grasp_offset

    # Gripper orientation: Z-axis pointing down
    grasp_rot = Rotation.from_euler('xyz', [180, 0, 0], degrees=True)

    # Align gripper with object orientation (for non-symmetric objects)
    obj_rot = Rotation.from_quat([
        object_pose.orientation.x,
        object_pose.orientation.y,
        object_pose.orientation.z,
        object_pose.orientation.w
    ])

    # Combined rotation
    final_rot = obj_rot * grasp_rot

    return grasp_pos, final_rot.as_quat()
```

## Exercises

1. **DOPE Deployment**: Run Isaac ROS DOPE with a pre-trained model (soup can or cracker box) and visualize detections in RViz.

2. **Depth Fusion**: Implement the DepthEnhancedPose node and compare DOPE Z estimates with depth sensor measurements.

3. **Custom Object Detection**: Choose a household object, generate 1000 synthetic training images in Isaac Sim, and train a DOPE model.

4. **Grasp Planning**: Given a detected object pose, compute a grasp pose and publish it as a TF frame.

---

**Next**: [Week 10 - Navigation with Nav2](./week-10-nav2.md)
