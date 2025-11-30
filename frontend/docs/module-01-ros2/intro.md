# Module 1: ROS 2 Fundamentals

## Overview

Welcome to Module 1 of the Physical AI & Humanoid Robotics textbook. This module provides a comprehensive foundation in Robot Operating System 2 (ROS 2), the industry-standard middleware framework for modern robotics development. You will learn the essential concepts, tools, and patterns needed to build robust control systems for humanoid robots.

ROS 2 represents a complete redesign of the original ROS framework, incorporating lessons learned from a decade of robotics development. It addresses critical limitations of ROS 1—including real-time performance, security, and multi-robot communication—making it the preferred choice for production robotics systems, from research humanoids to industrial collaborative robots.

## Learning Outcomes

By the end of this module, you will be able to:

1. **Master ROS 2 Architecture**: Understand the publish-subscribe communication model, service-based interactions, and the Data Distribution Service (DDS) middleware that powers ROS 2's distributed computing capabilities.

![ROS 2 Architecture](/img/modules/module-01/ros2-architecture.svg)
*Figure 1.1: ROS 2 Architecture - Layered structure showing DDS middleware, client libraries (rclcpp/rclpy), and application nodes communicating via topics*

2. **Build Robot Control Systems**: Create modular ROS 2 nodes in Python that control humanoid robot joints, process sensor data, and coordinate complex multi-degree-of-freedom movements.

3. **Model Humanoid Robots**: Design accurate robot descriptions using URDF (Unified Robot Description Format) and Xacro, defining kinematic chains, collision geometries, and visual representations for simulation and control.

4. **Implement Control Strategies**: Deploy the ros2_control framework to manage position, velocity, and effort controllers for humanoid joints, implementing feedback loops essential for stable bipedal locomotion.

5. **Integrate Simulation and Hardware**: Develop code that seamlessly transitions between simulated humanoid models and physical hardware through standardized hardware abstraction interfaces.

## Prerequisites

To succeed in this module, you should have:

- **Programming Skills**: Intermediate Python proficiency (functions, classes, object-oriented programming)
- **Linux Fundamentals**: Basic terminal navigation, file permissions, package management with apt
- **Mathematics**: Understanding of 3D coordinate systems, rotation matrices, and basic linear algebra
- **Robotics Concepts**: Familiarity with robot joints, degrees of freedom, and forward kinematics (helpful but not required)

## Why ROS 2 for Humanoid Robotics?

Humanoid robots present unique challenges that make ROS 2 particularly well-suited:

**Real-Time Performance**: Humanoid balance control requires deterministic, low-latency communication. ROS 2's DDS middleware provides Quality of Service (QoS) policies for reliable real-time data delivery—critical when a humanoid must react to disturbances within milliseconds to avoid falling.

**Distributed Computing**: A humanoid robot's computational workload spans perception (vision, depth sensing), planning (motion trajectories), and control (joint servos). ROS 2's native support for distributed nodes allows these processes to run across multiple processors or even separate computers, maximizing performance.

**Hardware Abstraction**: The ros2_control framework provides a unified interface for diverse actuators—whether you're using high-torque servo motors, linear actuators for telescoping joints, or compliant actuators for safe human-robot interaction. This abstraction enables code reuse across different humanoid platforms.

**Safety and Security**: Modern humanoid robots operate in human environments, requiring secure communication channels and predictable failure modes. ROS 2 includes DDS security plugins, type-safe message passing, and lifecycle management for graceful node shutdown—essential for collaborative robotics.

**Industry Adoption**: Leading humanoid robotics companies (Boston Dynamics' Atlas team, Agility Robotics, Tesla's Optimus program) leverage ROS 2 for development and testing. Learning ROS 2 prepares you for professional robotics development.

## Module Structure

This module follows a progressive learning path over 3 weeks:

**Week 3: Core Concepts**
- ROS 2 architecture and installation
- Creating and managing nodes
- Topic-based communication with publishers and subscribers

**Week 4: Advanced Communication**
- Service-based request-response patterns
- Action servers for long-running tasks (e.g., "walk to location")
- Dynamic parameter configuration

**Week 5: Robot Modeling and Control**
- URDF modeling for humanoid kinematics
- ros2_control framework implementation
- Complete working humanoid robot example

Each chapter includes hands-on code examples with detailed inline comments, practical exercises, and troubleshooting guidance. By Week 5, you will have built a complete simulated humanoid robot that responds to control commands.

## Getting Started

Ensure you have access to:
- A computer running Ubuntu 22.04 LTS (native installation or virtual machine)
- At least 4GB RAM and 20GB free disk space
- Sudo privileges for package installation
- A code editor (VS Code recommended with ROS extensions)

Ready to begin? Proceed to **Week 3: ROS 2 Basics** to install your development environment and create your first ROS 2 workspace.
