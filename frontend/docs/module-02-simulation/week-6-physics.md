# Week 6: Physics Configuration for Humanoid Robots

![Physics Engines Comparison](/img/modules/module-02/physics-engines.svg)
*Figure 2.1: Comparison of physics engines - ODE, Bullet, and PhysX with their respective pros and cons for humanoid simulation*

## Gravity and World Parameters

Humanoid robots are highly sensitive to gravity settings. Earth's gravity (9.81 m/s²) must be accurately modeled for realistic locomotion.

```xml
<!-- Configure gravity in world file -->
<world name="humanoid_world">
  <gravity>0 0 -9.81</gravity> <!-- Standard Earth gravity (Z-axis down) -->

  <!-- For testing on other planets -->
  <!-- Moon: 0 0 -1.62 -->
  <!-- Mars: 0 0 -3.71 -->

  <physics name="precise_physics" type="bullet">
    <max_step_size>0.001</max_step_size> <!-- 1ms for stability -->
    <real_time_factor>1.0</real_time_factor>

    <!-- Solver parameters for contact resolution -->
    <bullet>
      <solver>
        <type>sequential_impulse</type>
        <iters>50</iters> <!-- More iterations = more accurate contacts -->
        <sor>1.3</sor> <!-- Successive Over-Relaxation factor -->
      </solver>
      <constraints>
        <cfm>0.0</cfm> <!-- Constraint Force Mixing (softness) -->
        <erp>0.2</erp> <!-- Error Reduction Parameter (0-1) -->
        <contact_surface_layer>0.001</contact_surface_layer>
        <split_impulse>true</split_impulse> <!-- Prevents sinking into ground -->
      </constraints>
    </bullet>
  </physics>
</world>
```

**Key Parameters**:
- **ERP (Error Reduction Parameter)**: Controls how quickly interpenetrations are resolved. Too high (&gt;0.5) causes oscillations; too low (&lt;0.1) allows sinking. **0.2 is a good starting point for humanoids**.
- **CFM (Constraint Force Mixing)**: Adds softness to contacts. 0.0 = perfectly rigid. Increase to 1e-5 for compliant feet.

## Collision Geometry and Contact Forces

Humanoid foot-ground contact requires careful collision tuning.

```xml
<!-- Humanoid foot with realistic collision properties -->
<link name="right_foot">
  <pose>0 0 0.1 0 0 0</pose>
  <inertial>
    <mass>1.2</mass> <!-- Foot mass: 1.2 kg -->
    <inertia>
      <ixx>0.002</ixx> <ixy>0</ixy> <ixz>0</ixz>
      <iyy>0.003</iyy> <iyz>0</iyz> <izz>0.001</izz>
    </inertia>
  </inertial>

  <collision name="foot_collision">
    <geometry>
      <!-- Use box for simplified contact (faster) -->
      <box><size>0.2 0.1 0.05</size></box> <!-- Length Width Height -->
    </geometry>

    <surface>
      <contact>
        <!-- Contact stiffness and damping -->
        <ode>
          <kp>1e6</kp> <!-- Stiffness: 1 million N/m (rigid ground) -->
          <kd>100</kd>  <!-- Damping: prevents bouncing -->
          <max_vel>0.01</max_vel> <!-- Limit penetration correction speed -->
          <min_depth>0.001</min_depth> <!-- Minimum contact depth -->
        </ode>
      </contact>

      <friction>
        <ode>
          <mu>1.2</mu>  <!-- Friction coefficient (rubber on concrete) -->
          <mu2>1.0</mu2> <!-- Orthogonal friction (anisotropic) -->
          <fdir1>1 0 0</fdir1> <!-- Primary friction direction (forward) -->
          <slip1>0.0</slip1> <!-- No slip in primary direction -->
          <slip2>0.01</slip2> <!-- Slight lateral slip allowed -->
        </ode>
      </friction>
    </surface>
  </collision>

  <visual name="foot_visual">
    <geometry>
      <box><size>0.2 0.1 0.05</size></box>
    </geometry>
    <material>
      <ambient>0.3 0.3 0.3 1</ambient> <!-- Dark gray foot -->
    </material>
  </visual>
</link>
```

## Friction Coefficients: Material Reference

| Material Pair | μ (Friction Coefficient) | Use Case |
|---------------|--------------------------|----------|
| Rubber on Dry Concrete | 1.0 - 1.2 | Outdoor humanoid feet |
| Rubber on Wet Concrete | 0.7 - 0.9 | Rainy conditions |
| Plastic on Wood | 0.3 - 0.5 | Indoor wheeled robots |
| Metal on Metal | 0.15 - 0.25 | Joint interfaces (low friction) |
| Soft Rubber (compliant) | 1.5 - 2.0 | High-traction grippers |

**Simulation Tip**: Start with μ=1.0 for foot-ground contact. Increase to 1.2-1.5 if the robot slips during push recovery. Decrease to 0.7-0.8 for slippery surfaces (ice, wet floors).

## Rigid Body Dynamics and Stability

Humanoid stability depends on accurate inertia tensors. Incorrect values cause unrealistic rotation or tipping.

**Calculating Inertia for Simple Shapes**:

```python
# Python utility for common shapes
import numpy as np

def box_inertia(mass, width, depth, height):
    """
    Calculate inertia tensor for a box.
    Args:
        mass: kg
        width: x-dimension (m)
        depth: y-dimension (m)
        height: z-dimension (m)
    Returns:
        dict with ixx, iyy, izz
    """
    ixx = (mass / 12.0) * (depth**2 + height**2)
    iyy = (mass / 12.0) * (width**2 + height**2)
    izz = (mass / 12.0) * (width**2 + depth**2)
    return {'ixx': ixx, 'iyy': iyy, 'izz': izz}

def cylinder_inertia(mass, radius, length):
    """
    Calculate inertia for a cylinder (along Z-axis).
    Args:
        mass: kg
        radius: m
        length: m (height of cylinder)
    Returns:
        dict with ixx, iyy, izz
    """
    ixx = iyy = (mass / 12.0) * (3 * radius**2 + length**2)
    izz = 0.5 * mass * radius**2
    return {'ixx': ixx, 'iyy': iyy, 'izz': izz}

# Example: Humanoid torso (30cm x 40cm x 60cm, 15kg)
torso_inertia = box_inertia(15.0, 0.3, 0.4, 0.6)
print(f"Torso Inertia: {torso_inertia}")
# Output: {'ixx': 0.5, 'iyy': 0.5625, 'izz': 0.3125}
```

**Common Mistake**: Using uniform inertia (all diagonal elements equal) for non-cubic shapes. This causes unrealistic wobbling.

## Stability Testing: Zero Moment Point (ZMP)

A humanoid is statically stable when the **Zero Moment Point (ZMP)** stays within the support polygon (footprint).

```python
# ROS2 node snippet to monitor ZMP (requires force-torque sensors on feet)
import rclpy
from geometry_msgs.msg import WrenchStamped

class ZMPMonitor:
    def __init__(self):
        self.left_foot_force = None
        self.right_foot_force = None

    def foot_callback(self, msg, foot_name):
        # Extract vertical force (Z-axis)
        fz = msg.wrench.force.z
        if foot_name == 'left':
            self.left_foot_force = fz
        else:
            self.right_foot_force = fz

    def calculate_zmp(self):
        # Simplified ZMP calculation (assumes feet are 0.3m apart)
        if self.left_foot_force and self.right_foot_force:
            total_force = self.left_foot_force + self.right_foot_force
            zmp_y = (0.3 * self.right_foot_force) / total_force
            print(f"ZMP lateral position: {zmp_y:.3f} m")
            # Stable if 0 < zmp_y < 0.3 (between feet)
            return 0 < zmp_y < 0.3
```

**Exercise**: Create a simple two-legged robot in Gazebo. Apply a lateral force (push) to the torso using the `ign service` command. Measure the maximum force before the robot tips over. Compare different friction coefficients (μ=0.5 vs μ=1.5).

---

**Next**: [Week 7 - Sensor Simulation](./week-7-sensors.md) - LiDAR, depth cameras, IMUs, and noise modeling.
