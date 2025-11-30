# Week 7: Building Custom Simulation Worlds

## Why Custom Environments Matter

Generic flat-ground simulations fail to expose real-world challenges:

- **Terrain Variability**: Slopes, stairs, uneven surfaces test balance controllers
- **Obstacles**: Narrow passages, dynamic objects validate collision avoidance
- **Lighting Conditions**: Shadows, reflections affect vision-based policies
- **Domain Randomization**: Varying physics/visuals improves sim-to-real transfer

**Goal**: Create environments that challenge your robot and mirror deployment scenarios.

## Gazebo: Building Procedural Terrains

### Heightmap Terrains (DEM Data)

**Heightmaps** use grayscale images to define terrain elevation (white=high, black=low).

```xml
<!-- world_with_terrain.sdf -->
<sdf version="1.8">
  <world name="outdoor_terrain">
    <physics type="bullet">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <!-- Heightmap terrain from image -->
    <model name="terrain">
      <static>true</static>
      <link name="terrain_link">
        <collision name="terrain_collision">
          <geometry>
            <heightmap>
              <uri>file://terrain_heightmap.png</uri> <!-- 512x512 grayscale PNG -->
              <size>100 100 10</size> <!-- Width Depth MaxHeight (meters) -->
              <pos>0 0 0</pos>
            </heightmap>
          </geometry>
          <surface>
            <friction>
              <ode><mu>0.8</mu></ode> <!-- Dirt/grass friction -->
            </friction>
          </surface>
        </collision>

        <visual name="terrain_visual">
          <geometry>
            <heightmap>
              <uri>file://terrain_heightmap.png</uri>
              <size>100 100 10</size>
              <texture>
                <diffuse>file://grass_texture.jpg</diffuse>
                <normal>file://grass_normal.jpg</normal> <!-- Normal map for detail -->
                <size>10</size> <!-- Texture repeat every 10m -->
              </texture>
            </heightmap>
          </geometry>
        </visual>
      </link>
    </model>

    <!-- Dynamic lighting (sun moves over time) -->
    <light name="sun" type="directional">
      <pose>0 0 100 0 0 0</pose>
      <diffuse>0.9 0.9 0.7 1</diffuse> <!-- Warm daylight -->
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction> <!-- Angled sunlight -->
      <cast_shadows>true</cast_shadows> <!-- Realistic shadows -->
    </light>
  </world>
</sdf>
```

**Generate Heightmap with Python**:

```python
import numpy as np
from PIL import Image

def generate_hilly_terrain(width=512, height=512, num_hills=20):
    """
    Create procedural hills using Gaussian blobs.
    Args:
        width, height: Image dimensions
        num_hills: Number of random hills
    Returns:
        PIL Image (grayscale heightmap)
    """
    terrain = np.zeros((height, width), dtype=np.float32)

    for _ in range(num_hills):
        # Random hill center
        cx = np.random.randint(0, width)
        cy = np.random.randint(0, height)

        # Random hill size and height
        sigma = np.random.randint(20, 80)  # Width of hill
        amplitude = np.random.uniform(0.3, 1.0)  # Height (0-1 scale)

        # Create Gaussian hill
        y, x = np.ogrid[:height, :width]
        hill = amplitude * np.exp(-((x - cx)**2 + (y - cy)**2) / (2 * sigma**2))
        terrain += hill

    # Normalize to 0-255 (PNG grayscale range)
    terrain = (terrain / terrain.max() * 255).astype(np.uint8)

    # Save as PNG
    img = Image.fromarray(terrain, mode='L')
    img.save('terrain_heightmap.png')
    print("Heightmap saved: terrain_heightmap.png")

# Generate terrain
generate_hilly_terrain()
```

### Obstacles and Dynamic Objects

```xml
<!-- Add dynamic obstacles (boxes that can be pushed) -->
<model name="obstacle_box_1">
  <pose>5 3 0.5 0 0 0</pose>
  <link name="box_link">
    <inertial>
      <mass>20.0</mass> <!-- 20kg box (heavy enough to challenge robot) -->
      <inertia><ixx>0.67</ixx><iyy>0.67</iyy><izz>0.67</izz></inertia>
    </inertial>
    <collision name="box_collision">
      <geometry>
        <box><size>1.0 1.0 1.0</size></box>
      </geometry>
      <surface>
        <friction><ode><mu>0.5</mu></ode></friction> <!-- Cardboard on ground -->
      </surface>
    </collision>
    <visual name="box_visual">
      <geometry><box><size>1.0 1.0 1.0</size></box></geometry>
      <material>
        <ambient>0.7 0.5 0.3 1</ambient> <!-- Brown cardboard color -->
      </material>
    </visual>
  </link>
</model>

<!-- Narrow doorway (0.8m wide - tight for humanoid) -->
<model name="doorway">
  <static>true</static>
  <pose>10 0 0 0 0 0</pose>

  <link name="left_wall">
    <pose>0 -2 1 0 0 0</pose>
    <collision name="wall_collision">
      <geometry><box><size>0.2 4 2</size></box></geometry>
    </collision>
    <visual name="wall_visual">
      <geometry><box><size>0.2 4 2</size></box></geometry>
    </visual>
  </link>

  <link name="right_wall">
    <pose>0 2 1 0 0 0</pose>
    <collision name="wall_collision">
      <geometry><box><size>0.2 4 2</size></box></geometry>
    </collision>
    <visual name="wall_visual">
      <geometry><box><size>0.2 4 2</size></box></geometry>
    </visual>
  </link>
</model>
```

## Unity: Realistic Indoor/Outdoor Scenes

### Terrain Creation in Unity

1. **Terrain GameObject**: `GameObject → 3D Object → Terrain`
2. **Sculpt with Brushes**:
   - **Raise/Lower**: Create hills and valleys
   - **Smooth**: Reduce sharp edges (important for stable foot contact)
   - **Paint Textures**: Grass, dirt, gravel (multiple layers)

**Programmatic Terrain Generation (C#)**:

```csharp
using UnityEngine;

public class ProceduralTerrain : MonoBehaviour
{
    public int resolution = 513; // Terrain resolution (power of 2 + 1)
    public float scale = 20f;    // Perlin noise scale (larger = smoother hills)
    public float heightMultiplier = 10f; // Max terrain height

    void Start()
    {
        Terrain terrain = GetComponent<Terrain>();
        TerrainData terrainData = terrain.terrainData;

        // Set terrain size
        terrainData.heightmapResolution = resolution;
        terrainData.size = new Vector3(100, 20, 100); // Width, Height, Depth

        // Generate height values using Perlin noise
        float[,] heights = new float[resolution, resolution];

        for (int y = 0; y < resolution; y++)
        {
            for (int x = 0; x < resolution; x++)
            {
                // Perlin noise coordinates
                float xCoord = (float)x / resolution * scale;
                float yCoord = (float)y / resolution * scale;

                // Sample noise (0-1 range)
                float height = Mathf.PerlinNoise(xCoord, yCoord);
                heights[y, x] = height; // Unity uses [y, x] indexing
            }
        }

        // Apply heights to terrain
        terrainData.SetHeights(0, 0, heights);

        Debug.Log("Procedural terrain generated!");
    }
}
```

**Attach Script**: Add to Terrain GameObject, press Play to generate.

### Stairs and Multi-Level Structures

```csharp
// Procedurally generate stairs (testing locomotion policies)
public class StairGenerator : MonoBehaviour
{
    public int numSteps = 10;
    public float stepWidth = 1.0f;
    public float stepDepth = 0.3f;
    public float stepHeight = 0.15f; // 15cm rise (standard building code)

    void Start()
    {
        for (int i = 0; i < numSteps; i++)
        {
            // Create step GameObject
            GameObject step = GameObject.CreatePrimitive(PrimitiveType.Cube);
            step.transform.parent = transform;

            // Position step
            step.transform.position = new Vector3(
                0,
                i * stepHeight,
                i * stepDepth
            );

            // Scale to step dimensions
            step.transform.localScale = new Vector3(stepWidth, stepHeight, stepDepth);

            // Add friction (wood stairs)
            var collider = step.GetComponent<BoxCollider>();
            var material = new PhysicMaterial("StairMaterial");
            material.dynamicFriction = 0.6f;
            material.staticFriction = 0.7f;
            collider.material = material;
        }
    }
}
```

### Lighting for Realistic Sim-to-Real

**Key Principle**: Train vision policies under **varied lighting** to avoid overfitting to simulation conditions.

```csharp
// Random lighting controller (domain randomization)
public class LightingRandomizer : MonoBehaviour
{
    public Light directionalLight; // Assign main sun light

    void OnEpisodeBegin() // Called when RL episode resets
    {
        // Randomize sun angle (simulates different times of day)
        float randomAngleX = Random.Range(30f, 70f); // Morning to afternoon
        float randomAngleY = Random.Range(-30f, 30f); // East/West variation
        directionalLight.transform.rotation = Quaternion.Euler(randomAngleX, randomAngleY, 0);

        // Randomize light intensity
        directionalLight.intensity = Random.Range(0.6f, 1.2f);

        // Randomize color temperature (warm/cool lighting)
        float colorTemp = Random.Range(0.8f, 1.0f);
        directionalLight.color = new Color(1f, colorTemp, colorTemp * 0.9f);
    }
}
```

**Additional Randomization**:
- **Skybox**: Rotate to change sun position
- **Fog**: Add atmospheric scattering (outdoor scenes)
- **Shadows**: Toggle quality (soft vs hard shadows)

## Domain Randomization Best Practices

**Physics Randomization** (per episode):

```python
# Gazebo plugin to randomize physics (pseudo-code)
import random

class PhysicsRandomizer:
    def on_episode_reset(self):
        # Randomize gravity (±5%)
        gravity = 9.81 * random.uniform(0.95, 1.05)

        # Randomize ground friction (0.6 - 1.4)
        friction = random.uniform(0.6, 1.4)

        # Randomize link masses (±10%)
        for link in robot.links:
            original_mass = link.mass
            link.mass = original_mass * random.uniform(0.9, 1.1)

        # Randomize joint damping (±20%)
        for joint in robot.joints:
            joint.damping *= random.uniform(0.8, 1.2)
```

**Visual Randomization**:
- Material colors (RGB channels ±30%)
- Texture scales (0.5x - 2x)
- Object sizes (±15%)
- Camera exposure (±20%)

**Sensor Randomization**:
- LiDAR noise stddev: 1-5cm
- Camera latency: 10-50ms
- IMU bias drift: ±0.1 m/s²

## Testing Checklist for Custom Worlds

Before training policies, verify:

- [ ] Robot spawns in stable pose (not sinking/floating)
- [ ] Collision geometry matches visual (no invisible walls)
- [ ] Friction values are realistic (robot doesn't slip excessively)
- [ ] Lighting doesn't cause rendering artifacts (shadow acne, z-fighting)
- [ ] Domain randomization ranges don't break physics (e.g., negative mass)
- [ ] Sensors receive data at expected rates (check topic frequencies)
- [ ] Performance: Simulation runs at ≥0.5x real-time speed

**Exercise**: Create a Gazebo world with:
1. Heightmap terrain (at least 3 hills)
2. Staircase (8-10 steps, 15cm rise)
3. 3 dynamic boxes (obstacles)
4. Narrow corridor (0.9m wide)

Spawn a humanoid robot and manually control it (keyboard teleop) to navigate the environment. Document which obstacles cause the robot to fall or get stuck.

---

**Module 2 Summary**: You've learned to simulate humanoid robots in Gazebo and Unity, configure realistic physics, model sensors with noise, and build challenging environments. **Next Module**: [Isaac Sim & Gym](../module-03-isaac/intro.md) - GPU-accelerated simulation for massive parallel training.
