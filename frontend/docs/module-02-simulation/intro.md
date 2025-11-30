# Module 2: Gazebo & Unity Simulation

![Simulation Introduction](/img/ai-7.png)

## Why Simulation Matters for Physical AI

Simulation is the cornerstone of modern robotics development, especially for humanoid robots. Training a physical robot through trial-and-error is expensive, time-consuming, and potentially dangerous. A single wrong movement could damage motors, break sensors, or cause the robot to fall. Simulation environments allow us to:

- **Accelerate Development**: Test thousands of scenarios in parallel without hardware limitations
- **Reduce Costs**: Avoid physical damage to expensive robotic platforms ($50k-$500k per unit)
- **Enable Safe Learning**: Train reinforcement learning policies without risk of injury
- **Reproducible Experiments**: Control every environmental variable for consistent testing

## The Sim-to-Real Gap

The **sim-to-real gap** refers to performance degradation when transferring policies from simulation to physical hardware. Key challenges include:

1. **Physics Approximation**: Simulators use simplified contact models and friction coefficients
2. **Sensor Noise**: Real sensors have latency, drift, and environmental interference
3. **Actuator Dynamics**: Motors exhibit backlash, compliance, and thermal effects not modeled in simulation
4. **Environmental Variability**: Real-world lighting, terrain irregularities, and air resistance differ from simulation

**Mitigation Strategies**: Domain randomization (varying physics parameters), realistic sensor noise injection, system identification (measuring real robot parameters), and sim-to-real transfer techniques (like [RMA](https://arxiv.org/abs/2107.04034) - Rapid Motor Adaptation).

## Gazebo vs Unity: Choosing Your Simulator

| Feature | Gazebo (Classic/Ignition) | Unity with Robotics Hub |
|---------|---------------------------|-------------------------|
| **Primary Use** | ROS2 integration, robotic research | Game development, high-fidelity graphics |
| **Physics Engine** | ODE, Bullet, DART, Simbody | NVIDIA PhysX, Havok |
| **Rendering** | OGRE (adequate) | High-quality real-time rendering |
| **Learning Curve** | Moderate (XML-based SDF) | Steeper (C# scripting, Unity Editor) |
| **ROS2 Integration** | Native support | Via Unity Robotics Hub (TCP bridge) |
| **Best For** | Navigation, manipulation, sensor testing | Photorealistic sim-to-real, VR training |

**Rule of Thumb**: Use **Gazebo** for ROS2-centric development and traditional robotics workflows. Use **Unity** when visual fidelity matters (computer vision tasks, sim-to-real transfer for vision-based policies, or human-robot interaction studies).

## Learning Outcomes

By the end of this module, you will be able to:

1. **Configure Simulation Environments**: Set up Gazebo and Unity for humanoid robot testing
2. **Model Physics Accurately**: Tune collision parameters, friction, and contact forces for realistic behavior
3. **Simulate Sensor Suites**: Integrate LiDAR, depth cameras, IMUs, and force-torque sensors
4. **Build Custom Worlds**: Design environments that challenge locomotion and manipulation policies
5. **Bridge Sim-to-Real**: Apply domain randomization and identify sources of simulation bias

## Module Structure

- **Week 6**: Gazebo fundamentals, physics engines, and sensor simulation
- **Week 7**: Unity Robotics Hub, environment design, and sim-to-real best practices

**Prerequisites**: Familiarity with ROS2 (Module 1), basic Python/C# programming, and 3D coordinate systems.

---

**Next Chapter**: [Week 6 - Gazebo Basics](./week-6-gazebo-basics.md) - Installation, SDF models, and world file creation.
