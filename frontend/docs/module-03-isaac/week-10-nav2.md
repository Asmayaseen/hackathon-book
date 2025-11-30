# Week 10: Navigation with Nav2

![Navigation with Nav2](/img/ai-11.png)

## Introduction to Nav2

Nav2 (Navigation2) is the ROS 2 navigation stack that enables autonomous robot movement. Originally designed for wheeled robots, Nav2 can be adapted for **bipedal humanoid navigation** with appropriate configuration.

## Nav2 Architecture

Nav2 consists of modular components (servers) that work together:

1. **Map Server**: Provides occupancy grid map (free space vs. obstacles)
2. **AMCL**: Adaptive Monte Carlo Localization for pose estimation
3. **Planner Server**: Computes global path from start to goal
4. **Controller Server**: Generates velocity commands to follow the path
5. **Recovery Server**: Executes behaviors when navigation fails (spinning, backing up)
6. **Behavior Tree Navigator**: Orchestrates the above components

```python
# Conceptual Nav2 pipeline
def navigate_to_goal(goal_pose):
    # 1. Localize robot on map
    current_pose = amcl.get_pose()

    # 2. Plan global path
    global_path = planner.make_plan(current_pose, goal_pose)

    # 3. Follow path with local planning
    while not at_goal:
        local_plan = controller.compute_velocity_commands(global_path, current_pose)
        robot.execute_velocity(local_plan)

        # Handle obstacles
        if path_blocked:
            recovery.execute_recovery()
```

## Costmaps for Humanoid Navigation

Costmaps represent the environment as a grid where each cell has a cost (0 = free, 255 = obstacle). Humanoids require special considerations:

### Key Differences from Wheeled Robots

1. **Footprint Shape**: Rectangular footprint representing bipedal stance width
2. **Inflation Radius**: Smaller due to humanoid's ability to navigate tight spaces
3. **Height Clearance**: Must account for humanoid's tall vertical profile
4. **Dynamic Stability**: Cannot stop instantly - requires forward motion planning

### Humanoid Costmap Configuration

```yaml
# costmap_params.yaml - Configured for bipedal humanoid
global_costmap:
  global_frame: map
  robot_base_frame: base_link
  update_frequency: 5.0      # Hz - update global costmap
  publish_frequency: 2.0

  # Costmap size
  width: 20                  # 20 meter x 20 meter map
  height: 20
  resolution: 0.05           # 5cm grid cells

  # Humanoid footprint (30cm wide stance, 50cm long including step)
  footprint: [
    [0.25, 0.15],   # Front-right
    [0.25, -0.15],  # Front-left
    [-0.25, -0.15], # Back-left
    [-0.25, 0.15]   # Back-right
  ]

  plugins: ["static_layer", "obstacle_layer", "inflation_layer"]

  static_layer:
    plugin: "nav2_costmap_2d::StaticLayer"
    map_subscribe_transient_local: True

  obstacle_layer:
    plugin: "nav2_costmap_2d::ObstacleLayer"
    observation_sources: scan lidar

    # Use 2D lidar for ground-level obstacles
    scan:
      topic: /scan
      max_obstacle_height: 2.0  # Detect obstacles up to 2m (humanoid height)
      clearing_range: 5.0
      raytrace_range: 6.0

    # Use 3D lidar/camera for full environment perception
    lidar:
      topic: /points
      max_obstacle_height: 2.5
      min_obstacle_height: 0.1  # Ignore ground

  inflation_layer:
    plugin: "nav2_costmap_2d::InflationLayer"
    cost_scaling_factor: 3.0
    inflation_radius: 0.35  # Smaller than wheeled (humanoid agility)

# Local costmap for dynamic obstacle avoidance
local_costmap:
  global_frame: odom
  robot_base_frame: base_link
  update_frequency: 10.0     # Higher update rate for reactive navigation
  publish_frequency: 5.0

  width: 5                   # 5m x 5m local window
  height: 5
  resolution: 0.05

  footprint: [
    [0.25, 0.15],
    [0.25, -0.15],
    [-0.25, -0.15],
    [-0.25, 0.15]
  ]

  plugins: ["voxel_layer", "inflation_layer"]

  voxel_layer:
    plugin: "nav2_costmap_2d::VoxelLayer"
    enabled: True
    publish_voxel_map: True
    origin_z: 0.0
    z_resolution: 0.2        # 20cm vertical resolution
    z_voxels: 10             # 2m height (10 * 0.2m)
    max_obstacle_height: 2.0
    mark_threshold: 2        # Cells with 2+ hits marked as obstacle
```

## Path Planning Algorithms

Nav2 supports multiple global planners. Humanoids benefit from **Dijkstra** or **A*** for stable, predictable paths.

### Dijkstra vs. A*

```python
# Dijkstra: explores uniformly in all directions
def dijkstra(start, goal, costmap):
    visited = set()
    priority_queue = [(0, start)]  # (cost, node)

    while priority_queue:
        cost, current = heappop(priority_queue)
        if current == goal:
            return reconstruct_path(current)

        for neighbor in get_neighbors(current, costmap):
            new_cost = cost + costmap[neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                heappush(priority_queue, (new_cost, neighbor))

# A*: uses heuristic to guide search toward goal
def a_star(start, goal, costmap):
    visited = set()
    priority_queue = [(heuristic(start, goal), 0, start)]  # (f, g, node)

    while priority_queue:
        f, g, current = heappop(priority_queue)
        if current == goal:
            return reconstruct_path(current)

        for neighbor in get_neighbors(current, costmap):
            new_g = g + costmap[neighbor]
            new_f = new_g + heuristic(neighbor, goal)  # f = g + h
            if neighbor not in visited:
                visited.add(neighbor)
                heappush(priority_queue, (new_f, new_g, neighbor))

def heuristic(node, goal):
    # Euclidean distance as heuristic
    return sqrt((node.x - goal.x)**2 + (node.y - goal.y)**2)
```

### Planner Configuration

```yaml
# planner_server_params.yaml
planner_server:
  ros__parameters:
    expected_planner_frequency: 2.0  # Plan every 0.5s

    plugins: ["GridBased"]

    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"  # A* implementation
      tolerance: 0.1              # 10cm goal tolerance
      use_astar: True             # Use A* (False = Dijkstra)
      allow_unknown: False        # Don't plan through unexplored areas
      use_final_approach_orientation: True  # Orient toward goal
```

## Controller for Bipedal Motion

The **DWB (Dynamic Window Approach) controller** generates velocity commands that respect kinodynamic constraints.

### Bipedal-Specific Constraints

```yaml
# controller_params.yaml
controller_server:
  ros__parameters:
    controller_frequency: 20.0  # 20 Hz control loop

    plugins: ["FollowPath"]

    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"

      # Bipedal velocity limits (slower than wheeled robots)
      min_vel_x: 0.1            # Must maintain forward motion for stability
      max_vel_x: 0.5            # 0.5 m/s max walking speed
      min_vel_y: -0.2           # Limited lateral movement
      max_vel_y: 0.2
      max_vel_theta: 0.3        # 0.3 rad/s turning speed

      # Acceleration limits (gradual for balance)
      acc_lim_x: 0.3            # 0.3 m/s² (gentle acceleration)
      acc_lim_y: 0.2
      acc_lim_theta: 0.5
      decel_lim_x: -0.3         # Gentle deceleration

      # Trajectory scoring
      critics: [
        "RotateToGoal",
        "Oscillation",
        "BaseObstacle",
        "GoalAlign",
        "PathAlign",
        "PathDist",
        "GoalDist"
      ]

      # Critic weights (tune for humanoid behavior)
      PathAlign.scale: 32.0      # Strongly prefer following global path
      GoalAlign.scale: 24.0      # Orient toward goal
      PathDist.scale: 32.0
      GoalDist.scale: 24.0
      BaseObstacle.scale: 0.02   # Obstacle avoidance

      # Simulation parameters
      sim_time: 2.0              # Simulate trajectories 2 seconds ahead
      vx_samples: 10             # Sample 10 velocities per dimension
      vy_samples: 5
      vtheta_samples: 10

      # Trajectory constraints
      trajectory_generator_name: "dwb_plugins::StandardTrajectoryGenerator"
```

## Recovery Behaviors

When navigation fails, recovery behaviors attempt to get the robot unstuck.

### Humanoid-Safe Recovery Sequence

```yaml
# behavior_tree_params.yaml
bt_navigator:
  ros__parameters:
    plugin_lib_names:
      - nav2_compute_path_to_pose_action_bt_node
      - nav2_follow_path_action_bt_node
      - nav2_back_up_action_bt_node
      - nav2_spin_action_bt_node
      - nav2_wait_action_bt_node

    # Recovery behavior parameters
    global_frame: map
    robot_base_frame: base_link
    transform_tolerance: 0.1

    # Recovery sequence for humanoids (gentle, stable motions)
    default_nav_through_poses_bt_xml: ""
    default_nav_to_pose_bt_xml: ""

    # Spin recovery - rotate in place to clear sensors
    spin:
      simulate_ahead_time: 2.0
      max_rotational_vel: 0.2     # Slow rotation for stability
      min_rotational_vel: 0.1
      rotational_acc_lim: 0.3

    # Backup recovery - step backward
    backup:
      simulate_ahead_time: 2.0
      backup_dist: 0.3            # Small 30cm backup
      backup_speed: 0.1           # Slow, controlled
```

## Launching Nav2 for Humanoid

```python
# humanoid_nav2_launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_dir = get_package_share_directory('humanoid_navigation')

    return LaunchDescription([
        # Map server - load pre-built map
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[{
                'yaml_filename': os.path.join(pkg_dir, 'maps', 'office.yaml'),
                'use_sim_time': False
            }]
        ),

        # AMCL localization
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            parameters=[os.path.join(pkg_dir, 'config', 'amcl_params.yaml')]
        ),

        # Planner server
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            parameters=[os.path.join(pkg_dir, 'config', 'planner_params.yaml')]
        ),

        # Controller server
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            parameters=[os.path.join(pkg_dir, 'config', 'controller_params.yaml')]
        ),

        # Recovery server
        Node(
            package='nav2_recoveries',
            executable='recoveries_server',
            name='recoveries_server',
            parameters=[os.path.join(pkg_dir, 'config', 'recovery_params.yaml')]
        ),

        # Behavior tree navigator
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            parameters=[os.path.join(pkg_dir, 'config', 'bt_navigator_params.yaml')]
        ),

        # Lifecycle manager
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            parameters=[{
                'autostart': True,
                'node_names': [
                    'map_server',
                    'amcl',
                    'planner_server',
                    'controller_server',
                    'recoveries_server',
                    'bt_navigator'
                ]
            }]
        )
    ])
```

## Exercises

1. **Costmap Tuning**: Adjust footprint and inflation radius for your simulated humanoid. Observe effects on path planning.

2. **Algorithm Comparison**: Run navigation with Dijkstra and A* planners. Measure planning time and path length differences.

3. **Recovery Testing**: Place the robot in a tight corner and trigger recovery behaviors. Observe which sequence successfully escapes.

4. **Dynamic Obstacles**: Add moving obstacles to the environment and observe local planner's avoidance behavior.

---

**Next**: [Week 10 - Bipedal Locomotion](./week-10-bipedal-locomotion.md)
