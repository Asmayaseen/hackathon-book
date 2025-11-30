# Week 8: Synthetic Data Generation

## The Synthetic Data Revolution

Manually labeling training data is expensive and time-consuming. A single annotated image for object detection can cost $0.50-$5.00. For a dataset of 100,000 images, this means $50,000-$500,000 in annotation costs.

**Synthetic data generation** solves this by automatically creating labeled training data in simulation. Isaac Sim can generate thousands of perfectly labeled images per hour at near-zero marginal cost.

## Domain Randomization

The key to successful sim-to-real transfer is **domain randomization** - systematically varying scene parameters to create diversity that covers real-world variations.

### Randomization Parameters

1. **Lighting**: Intensity, color temperature, angle
2. **Textures**: Surface materials, colors, reflectivity
3. **Object poses**: Position, rotation, scale
4. **Camera parameters**: FOV, exposure, focus
5. **Backgrounds**: Clutter, distractors, environments

## Using Isaac Sim Replicator

Replicator is Isaac Sim's synthetic data generation framework, providing high-level APIs for creating randomized datasets.

### Basic Synthetic Dataset Generation

```python
import omni.replicator.core as rep
from omni.isaac.kit import SimulationApp

# Initialize headless simulation for faster generation
simulation_app = SimulationApp({"headless": True})

# Define camera for capturing images
camera = rep.create.camera(
    position=(2.0, 2.0, 1.5),  # Camera location
    look_at=(0, 0, 0)           # Point camera at origin
)

# Create randomized scene
def create_scene():
    # Random cube representing target object
    cube = rep.create.cube(
        position=rep.distribution.uniform((-1, -1, 0.5), (1, 1, 1.5)),
        scale=rep.distribution.uniform(0.2, 0.5),
        semantics=[("class", "target_object")]  # Label for detection
    )

    # Randomize cube material/color
    with cube:
        rep.randomizer.color(
            colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
        )

    # Random lighting direction and intensity
    light = rep.create.light(
        light_type="Distant",  # Directional light (sun-like)
        intensity=rep.distribution.uniform(500, 3000),
        rotation=rep.distribution.uniform((0, -180, 0), (0, 180, 0))
    )

    return cube, light

# Register randomization graph
rep.randomizer.register(create_scene)

# Configure output writers for different annotation types
# 1. RGB images
rgb_writer = rep.WriterRegistry.get("BasicWriter")
rgb_writer.initialize(
    output_dir="./synthetic_data/rgb",
    rgb=True
)

# 2. Semantic segmentation (pixel-wise class labels)
semantic_writer = rep.WriterRegistry.get("BasicWriter")
semantic_writer.initialize(
    output_dir="./synthetic_data/semantic",
    semantic_segmentation=True
)

# 3. Bounding boxes for object detection
bbox_writer = rep.WriterRegistry.get("BasicWriter")
bbox_writer.initialize(
    output_dir="./synthetic_data/bbox",
    bounding_box_2d_tight=True
)

# Attach all writers to camera
rgb_writer.attach([camera])
semantic_writer.attach([camera])
bbox_writer.attach([camera])

# Generate 1000 randomized frames
with rep.trigger.on_frame(num_frames=1000):
    rep.randomizer.create_scene()

# Run orchestrator to execute generation
rep.orchestrator.run()

simulation_app.close()
print("Generated 1000 synthetic training samples")
```

## Perception Ground Truth

Isaac Sim automatically generates **perfect labels** for various perception tasks:

### 1. 2D Bounding Boxes
Pixel-perfect boxes around objects for object detection training (YOLO, Faster R-CNN).

### 2. Instance Segmentation
Pixel-wise masks identifying individual object instances.

### 3. Depth Maps
Per-pixel distance from camera for stereo vision and 3D reconstruction.

### 4. 6-DOF Pose
3D position (x, y, z) and orientation (roll, pitch, yaw) for each object.

```python
# Advanced ground truth generation
import omni.replicator.core as rep

camera = rep.create.camera()

# Enable multiple annotation types simultaneously
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="./multi_annotation",
    rgb=True,                          # RGB images
    bounding_box_2d_tight=True,        # 2D detection boxes
    bounding_box_3d=True,              # 3D oriented boxes
    semantic_segmentation=True,        # Pixel-wise class labels
    instance_segmentation=True,        # Pixel-wise instance IDs
    distance_to_camera=True,           # Depth map
    distance_to_image_plane=True,      # Planar depth
    normals=True,                      # Surface normals
    motion_vectors=True                # Optical flow
)
writer.attach([camera])
```

## Creating a Custom Dataset for Humanoid Perception

This example generates training data for detecting objects a humanoid robot might manipulate:

```python
import omni.replicator.core as rep

# Define objects humanoid should detect
def create_manipulation_scene():
    # Ground plane with random texture
    floor = rep.create.plane(
        scale=10,
        semantics=[("class", "floor")]
    )
    with floor:
        rep.randomizer.texture(
            textures=["./textures/wood.jpg", "./textures/tile.jpg"]
        )

    # Table at humanoid waist height
    table = rep.create.cube(
        position=(1.0, 0, 0.75),
        scale=(1.0, 0.6, 0.05),
        semantics=[("class", "table")]
    )

    # Randomized target objects on table
    obj_types = ["cube", "sphere", "cylinder"]
    for i in range(3):  # 3 random objects
        obj = rep.create.from_usd(
            f"./assets/{rep.distribution.choice(obj_types)}.usd",
            position=rep.distribution.uniform(
                (0.5, -0.3, 0.80),  # Table surface bounds
                (1.5, 0.3, 0.80)
            ),
            semantics=[("class", "manipulable_object")]
        )
        with obj:
            # Random materials make model robust to appearance
            rep.randomizer.color(
                colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
            )

    # Humanoid eye-level camera (160cm height)
    camera = rep.create.camera(
        position=(0, 0, 1.6),
        rotation=rep.distribution.uniform((-10, -30, 0), (10, 30, 0))
    )

    return camera

rep.randomizer.register(create_manipulation_scene)

# Generate dataset with consistent format
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="./humanoid_manipulation_dataset",
    rgb=True,
    bounding_box_2d_tight=True,
    semantic_segmentation=True
)

camera = create_manipulation_scene()
writer.attach([camera])

# Generate 5000 training images
with rep.trigger.on_frame(num_frames=5000):
    rep.randomizer.create_manipulation_scene()

rep.orchestrator.run()
```

## Best Practices

1. **Match Real Sensors**: Configure camera resolution, FOV, and noise to match your physical robot's sensors.
2. **Sufficient Variation**: Generate at least 10x more synthetic data than you would collect manually.
3. **Validate Transfer**: Test trained models on small real-world validation sets to verify sim-to-real gap.
4. **Incremental Complexity**: Start with simple scenes, add complexity as models improve.

## Exercises

1. **Basic Randomization**: Create a dataset of 100 images with cubes of random colors and sizes at random positions.

2. **Lighting Study**: Generate 50 images of the same scene with only lighting randomized. Observe how this affects object appearance.

3. **Custom Objects**: Import a 3D model of an everyday object (cup, bottle) and generate a 1000-image detection dataset.

4. **Ground Truth Comparison**: Generate RGB + semantic segmentation pairs and visualize the segmentation masks overlaid on RGB images.

---

**Next**: [Week 9 - Isaac ROS Deployment](./week-9-isaac-ros.md)
