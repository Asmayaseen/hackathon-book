# Week 3: ROS 2 Basics

![ROS 2 Basics](/img/ai-5.png)

## ROS 2 Architecture Overview

ROS 2 is built on a layered architecture that separates application logic from middleware concerns. Understanding this architecture is essential for building reliable humanoid robot systems.

### Core Components

**Nodes**: The fundamental building blocks of ROS 2 applications. Each node is an independent process responsible for a specific task—for example, one node might read IMU data for balance sensing, while another computes joint trajectories. Nodes communicate through the middleware layer, enabling distributed processing across multiple cores or machines.

**DDS Middleware**: ROS 2 uses Data Distribution Service (DDS) as its communication backbone, replacing ROS 1's custom TCPROS protocol. DDS is an industry-standard publish-subscribe middleware that provides Quality of Service (QoS) guarantees—crucial for real-time robotics. When a humanoid's balance controller publishes foot pressure data, DDS ensures this critical information reaches the gait planner with bounded latency, even under network congestion.

**Discovery Mechanism**: Unlike ROS 1's roscore master node (a single point of failure), ROS 2 uses DDS's automatic discovery. Nodes find each other dynamically on the network without centralized coordination. This peer-to-peer architecture improves reliability—if one node crashes, others continue operating.

**Communication Patterns**:
- **Topics**: Asynchronous publish-subscribe for streaming data (sensor readings, joint states)
- **Services**: Synchronous request-response for one-off queries (e.g., "compute inverse kinematics for this pose")
- **Actions**: Long-running tasks with feedback (e.g., "walk forward 2 meters" with periodic progress updates)

## Installation on Ubuntu 22.04

ROS 2 Humble Hawksbill is the Long-Term Support (LTS) release for Ubuntu 22.04, supported until 2027. Follow these steps for a complete installation.

### Step 1: Set Up Sources

```bash
# Ensure system is up to date
sudo apt update && sudo apt upgrade -y

# Install required tools
sudo apt install -y software-properties-common curl

# Add ROS 2 GPG key for package verification
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg

# Add ROS 2 repository to sources list
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

### Step 2: Install ROS 2 Packages

```bash
# Update package index after adding new repository
sudo apt update

# Install ROS 2 Humble desktop full (includes rviz, rqt tools, and demo packages)
sudo apt install -y ros-humble-desktop

# Install development tools for building packages
sudo apt install -y ros-dev-tools

# Install colcon build system (faster parallel builds compared to catkin)
sudo apt install -y python3-colcon-common-extensions
```

### Step 3: Environment Configuration

```bash
# Source ROS 2 setup script (needed in every new terminal)
source /opt/ros/humble/setup.bash

# Add to bashrc for automatic sourcing
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

# Verify installation by checking ROS version
printenv | grep ROS_DISTRO
# Should output: ROS_DISTRO=humble
```

## Creating Your First ROS 2 Workspace

A workspace is a directory containing ROS 2 packages. The recommended structure separates source code (`src/`) from build artifacts (`build/`, `install/`).

### Initialize Workspace

```bash
# Create workspace directory
mkdir -p ~/humanoid_ws/src
cd ~/humanoid_ws

# Initialize workspace (creates build and install directories)
colcon build
# This creates build/, install/, and log/ subdirectories

# Source the workspace overlay
source install/setup.bash
```

### Workspace Overlay Concept

ROS 2 uses an "overlay" system where your workspace extends the base ROS 2 installation (`/opt/ros/humble`). When you source `install/setup.bash`, packages in your workspace take precedence over system-installed packages. This allows you to develop custom versions of existing packages without modifying system files.

### Creating a Package

```bash
# Navigate to source directory
cd ~/humanoid_ws/src

# Create Python package for humanoid control
ros2 pkg create humanoid_control \
  --build-type ament_python \
  --dependencies rclpy std_msgs \
  --node-name joint_controller

# Package structure created:
# humanoid_control/
# ├── package.xml          # Package metadata and dependencies
# ├── setup.py             # Python build configuration
# ├── setup.cfg            # Installation paths
# └── humanoid_control/
#     └── joint_controller.py  # Auto-generated node template
```

### Build and Source

```bash
# Return to workspace root
cd ~/humanoid_ws

# Build all packages with symlink install (changes in Python scripts don't require rebuild)
colcon build --symlink-install

# Source the updated workspace
source install/setup.bash
```

## ROS 2 CLI Basics

The `ros2` command-line tool provides introspection and interaction capabilities essential for debugging robot systems.

### Node Management

```bash
# List all running nodes
ros2 node list

# Get detailed info about a specific node (topics, services, actions)
ros2 node info /joint_controller

# Run a node from a package
ros2 run humanoid_control joint_controller
```

### Topic Operations

```bash
# List all active topics
ros2 topic list

# Show message type for a topic
ros2 topic info /joint_states

# Monitor messages in real-time
ros2 topic echo /joint_states

# Publish a test message from command line
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.1}}"
```

### Interface Inspection

```bash
# List all message types available
ros2 interface list

# Show message definition (useful for understanding data structure)
ros2 interface show sensor_msgs/msg/JointState
# Output shows fields: header, name[], position[], velocity[], effort[]
```

## Next Steps

You now have a working ROS 2 installation and understand the basic architecture. In the next chapter, **Week 3: Nodes and Topics**, you will create Python nodes that communicate via topics to control a simulated robot. You'll implement a publisher that sends joint commands and a subscriber that monitors robot state—the foundation for all ROS 2 robot control.

### Practice Exercise

Before proceeding, verify your setup:

1. Open three terminals
2. In terminal 1: Run `ros2 run demo_nodes_cpp talker`
3. In terminal 2: Run `ros2 run demo_nodes_py listener`
4. In terminal 3: Run `ros2 topic list` and `ros2 topic echo /chatter`

You should see messages flowing from talker to listener. This confirms your ROS 2 installation is working correctly.
