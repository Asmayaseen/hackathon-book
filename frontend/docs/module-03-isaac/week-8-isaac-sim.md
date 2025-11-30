# Week 8: Isaac Sim Fundamentals

![Isaac Sim](/img/ai-9.png)

## Introduction to Isaac Sim

Isaac Sim is NVIDIA's robotics simulation platform built on the Omniverse framework. Unlike traditional simulators, Isaac Sim provides **photorealistic rendering** using RTX ray tracing, enabling synthetic data generation that closely matches real-world sensor outputs.

## Installation and Setup

### System Requirements
- **GPU**: RTX 2060 or higher (8GB+ VRAM recommended)
- **OS**: Ubuntu 20.04/22.04 or Windows 10/11
- **RAM**: 32GB minimum for complex scenes
- **Storage**: 50GB for Isaac Sim + asset libraries

### Installation Steps

```bash
# Download NVIDIA Omniverse Launcher
wget https://install.launcher.omniverse.nvidia.com/installers/omniverse-launcher-linux.AppImage

# Make executable and launch
chmod +x omniverse-launcher-linux.AppImage
./omniverse-launcher-linux.AppImage

# From Omniverse Launcher, install:
# 1. Nucleus (local asset server)
# 2. Isaac Sim 2023.1.1 or later
```

### Verifying Installation

```python
# Test Isaac Sim Python API
from omni.isaac.kit import SimulationApp

# Initialize simulation with specific configuration
simulation_app = SimulationApp({
    "headless": False,  # Set True for server/cloud environments
    "width": 1920,      # Viewport resolution
    "height": 1080
})

from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid

# Create a simple physics test
world = World()
# Add a cube that will fall due to gravity
cube = DynamicCuboid(
    prim_path="/World/Cube",
    position=[0, 0, 2.0],  # 2 meters above ground
    size=0.5,               # 50cm cube
    color=[1.0, 0.0, 0.0]  # Red
)
world.reset()

# Run simulation for 120 frames (2 seconds at 60 FPS)
for i in range(120):
    world.step(render=True)  # Physics step + render

simulation_app.close()
```

## Understanding the Omniverse Foundation

### Universal Scene Description (USD)

Isaac Sim uses Pixar's USD format as its foundation. USD is a **scene description framework** that enables:
- **Layered composition** - Non-destructive editing by stacking changes
- **Time-sampled data** - Animations and dynamic properties stored efficiently
- **Collaboration** - Multiple users editing different aspects simultaneously

```python
from pxr import Usd, UsdGeom, Gf

# Create a USD stage (container for 3D content)
stage = Usd.Stage.CreateNew("robot_scene.usd")

# Define a transform (position/rotation in 3D space)
xform = UsdGeom.Xform.Define(stage, "/World/Robot")
xform.AddTranslateOp().Set(Gf.Vec3d(1.0, 0.0, 0.5))  # Position (x, y, z)

# Add a cube mesh representing robot body
cube = UsdGeom.Cube.Define(stage, "/World/Robot/Body")
cube.GetSizeAttr().Set(0.3)  # 30cm cube

# Save the stage to disk
stage.GetRootLayer().Save()
print("USD scene saved to robot_scene.usd")
```

## RTX Ray Tracing for Photorealism

Isaac Sim leverages NVIDIA RTX GPUs for **path-traced rendering**, simulating light physics to produce realistic images:

### Key Rendering Features

1. **Global Illumination** - Light bounces realistically off surfaces
2. **Reflections and Refractions** - Metallic surfaces and glass render accurately
3. **Accurate Shadows** - Soft shadows matching real-world lighting conditions

```python
import omni.replicator.core as rep

# Configure RTX ray tracing parameters
rep.settings.set_render_rtx_realtime()  # Real-time RTX mode

# Set samples per pixel (higher = better quality, slower render)
rep.settings.set_rtx_subframes(4)  # 4 samples/pixel balance

# Enable denoising for cleaner output
rep.settings.carb_settings("/rtx/post/dlss/execMode", 1)
```

### Why Photorealism Matters

For **sim-to-real transfer**, synthetic training data must match real sensor outputs. RTX rendering produces:
- **Realistic lighting** matching warehouse/factory environments
- **Material properties** (metal, plastic, fabric) that affect perception
- **Sensor noise simulation** for cameras and depth sensors

## Creating Your First Simulation

### Loading a Humanoid Robot

```python
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.stage import add_reference_to_stage

# Initialize world with physics
world = World(stage_units_in_meters=1.0)

# Get NVIDIA asset server path
assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise Exception("Could not find Isaac Sim assets folder")

# Load Carter robot (wheeled robot for testing)
robot_usd_path = assets_root_path + "/Isaac/Robots/Carter/carter_v1.usd"
add_reference_to_stage(
    usd_path=robot_usd_path,
    prim_path="/World/Carter"  # Where to place in scene hierarchy
)

world.reset()

# Run interactive simulation (press STOP in UI to exit)
while simulation_app.is_running():
    world.step(render=True)

simulation_app.close()
```

## Exercises

1. **Scene Construction**: Create a USD scene with a ground plane, three colored cubes at different heights, and a directional light source.

2. **Physics Exploration**: Modify the cube dropping example to create a Newton's Cradle with 5 spheres. Observe energy conservation in the simulation.

3. **RTX Comparison**: Render the same scene with and without RTX enabled. Compare visual quality and rendering time.

4. **Robot Loading**: Load the Franka Emika Panda robot from Isaac assets and position it at (0, 0, 1.0).

---

**Next**: [Week 8 - Synthetic Data Generation](./week-8-synthetic-data.md)
