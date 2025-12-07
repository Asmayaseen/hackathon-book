# ہفتہ 10: Nav2 کے ساتھ نیوی گیشن

![Navigation with Nav2](/img/ai-11.png)

## Nav2 کا تعارف

Nav2 (نیوی گیشن2) ROS 2 نیوی گیشن اسٹیک ہے جو خودکار روبوٹ حرکت کو فعال بناتا ہے۔ اصل میں وہیلڈ روبوٹس کے لئے ڈیزائن کیا گیا، Nav2 کو مناسب کنفیگریشن کے ساتھ **بائی پیڈل ہیومنوائڈ نیوی گیشن** کے لئے ایڈجسٹ کیا جا سکتا ہے۔

## Nav2 آرکیٹیکچر

Nav2 ماڈیولر کمپونینٹس (سرورز) پر مشتمل ہے جو مل کر کام کرتے ہیں:

1. **میپ سرور**: اوقوپنسی گرڈ میپ فراہم کرتا ہے (مفت سپیس بمقابلہ رکاوٹیں)
2. **AMCL**: پوز ایسٹیمیشن کے لئے ایڈاپٹیو مونٹی کارلو لوکلائزیشن
3. **پلینر سرور**: شروع سے گول تک گلوبل پاتھ کا حساب لگاتا ہے
4. **کنٹرولر سرور**: پاتھ کو فالو کرنے کے لئے رفتار کمانڈز تیار کرتا ہے
5. **ریکوری سرور**: جب نیوی گیشن ناکام ہو جاتا ہے تو برتاؤ انجام دیتا ہے (اسپننگ، بیکنگ اپ)
6. **بریویئر ٹری نیوی گیٹر**: اوپر کے کمپونینٹس کو مربوط کرتا ہے

```python
# تصوراتی Nav2 پائپ لائن
def navigate_to_goal(goal_pose):
    # 1. میپ پر روبوٹ کو لوکلائز کریں
    current_pose = amcl.get_pose()

    # 2. گلوبل پاتھ کی منصوبہ بندی کریں
    global_path = planner.make_plan(current_pose, goal_pose)

    # 3. مقامی منصوبہ بندی کے ساتھ پاتھ فالو کریں
    while not at_goal:
        local_plan = controller.compute_velocity_commands(global_path, current_pose)
        robot.execute_velocity(local_plan)

        # رکاوٹوں کا سامنا کریں
        if path_blocked:
            recovery.execute_recovery()
```

## ہیومنوائڈ نیوی گیشن کے لئے کوسٹ میپس

کوسٹ میپس ماحول کو ایک گرڈ کے طور پر ظاہر کرتی ہیں جہاں ہر سیل کا ایک کوسٹ ہوتا ہے (0 = مفت، 255 = رکاوٹ). ہیومنوائڈز کو خصوصی غور کی ضرورت ہوتی ہے:

### وہیلڈ روبوٹس سے کلیدی فرق

1. **فُٹ پرینٹ شیپ**: بائی پیڈل اسٹینس چوڑائی کی نمائندگی کرنے والا مستطیل فُٹ پرینٹ
2. **انفلیشن ریڈیس**: چھوٹا کیونکہ ہیومنوائڈ ٹائٹ سپیسز میں نیوی گیٹ کرنے کے قابل ہے
3. **اونچائی کلئرنس**: ہیومنوائڈ کے طویل عمودی پروفائل کا خیال رکھنا چاہیے
4. **ڈائنامک اسٹیبلٹی**: فوراً روک نہیں سکتا - فارورڈ موشن کی منصوبہ بندی کی ضرورت ہے

### ہیومنوائڈ کوسٹ میپ کنفیگریشن

```yaml
# costmap_params.yaml - بائی پیڈل ہیومنوائڈ کے لئے کنفیگر کیا گیا
global_costmap:
  global_frame: map
  robot_base_frame: base_link
  update_frequency: 5.0      # Hz - گلوبل کوسٹ میپ اپ ڈیٹ کریں
  publish_frequency: 2.0

  # کوسٹ میپ سائز
  width: 20                  # 20 میٹر x 20 میٹر میپ
  height: 20
  resolution: 0.05           # 5cm گرڈ سیلز

  # ہیومنوائڈ فُٹ پرینٹ (30cm چوڑا اسٹینس، 50cm لمبا اسٹیپ سمیت)
  footprint: [
    [0.25, 0.15],   # فرنٹ-رائٹ
    [0.25, -0.15],  # فرنٹ-لیفٹ
    [-0.25, -0.15], # بیک-لیفٹ
    [-0.25, 0.15]   # بیک-رائٹ
  ]

  plugins: ["static_layer", "obstacle_layer", "inflation_layer"]

  static_layer:
    plugin: "nav2_costmap_2d::StaticLayer"
    map_subscribe_transient_local: True

  obstacle_layer:
    plugin: "nav2_costmap_2d::ObstacleLayer"
    observation_sources: scan lidar

    # گراؤنڈ لیول رکاوٹوں کے لئے 2D lidar استعمال کریں
    scan:
      topic: /scan
      max_obstacle_height: 2.0  # 2m تک رکاوٹیں ڈیٹیکٹ کریں (ہیومنوائڈ اونچائی)
      clearing_range: 5.0
      raytrace_range: 6.0

    # مکمل ماحول ادراک کے لئے 3D lidar/camera استعمال کریں
    lidar:
      topic: /points
      max_obstacle_height: 2.5
      min_obstacle_height: 0.1  # زمین کو نظر انداز کریں

  inflation_layer:
    plugin: "nav2_costmap_2d::InflationLayer"
    cost_scaling_factor: 3.0
    inflation_radius: 0.35  # چھوٹا وہیلڈ سے (ہیومنوائڈ ایگلٹی)

# ڈائنامک رکاوٹ ایوائڈنس کے لئے مقامی کوسٹ میپ
local_costmap:
  global_frame: odom
  robot_base_frame: base_link
  update_frequency: 10.0     # ری ایکٹیو نیوی گیشن کے لئے زیادہ اپ ڈیٹ کی شرح
  publish_frequency: 5.0

  width: 5                   # 5m x 5m مقامی ونڈو
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
    z_resolution: 0.2        # 20cm عمودی ریزولوشن
    z_voxels: 10             # 2m اونچائی (10 * 0.2m)
    max_obstacle_height: 2.0
    mark_threshold: 2        # 2+ ہٹس والے سیلز کو رکاوٹ کے طور پر نشان زد کریں
```

## پاتھ پلاننگ الگوری دھم

Nav2 متعدد گلوبل پلینرز کی حمایت کرتا ہے۔ ہیومنوائڈز کو مستحکم، قابل پیش گوئی پاتھس کے لئے **Dijkstra** یا **A*** سے فائدہ ہوتا ہے۔

### Dijkstra بمقابلہ A*

```python
# Dijkstra: تمام سمت میں یکساں طور پر تلاش کرتا ہے
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

# A*: گول کی طرف تلاش کو ہدایت کرنے کے لئے ہیورسٹک استعمال کرتا ہے
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
    # ہیورسٹک کے طور پر یوکلڈین فاصلہ
    return sqrt((node.x - goal.x)**2 + (node.y - goal.y)**2)
```

### پلینر کنفیگریشن

```yaml
# planner_server_params.yaml
planner_server:
  ros__parameters:
    expected_planner_frequency: 2.0  # 0.5s میں منصوبہ بندی کریں

    plugins: ["GridBased"]

    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"  # A* امپلیمنٹیشن
      tolerance: 0.1              # 10cm گول ٹالرنس
      use_astar: True             # A* استعمال کریں (False = Dijkstra)
      allow_unknown: False        # ان ایکسپلور کردہ علاقوں کے ذریعے منصوبہ نہ بنائیں
      use_final_approach_orientation: True  # گول کی طرف اورینٹ کریں
```

## بائی پیڈل موشن کے لئے کنٹرولر

**DWB (ڈائنامک ونڈو ایپروچ) کنٹرولر** کنوموڈینامک کنٹرینٹس کا احترام کرتے ہوئے رفتار کمانڈز تیار کرتا ہے۔

### بائی پیڈل مخصوص کنٹرینٹس

```yaml
# controller_params.yaml
controller_server:
  ros__parameters:
    controller_frequency: 20.0  # 20 Hz کنٹرول لوپ

    plugins: ["FollowPath"]

    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"

      # بائی پیڈل رفتار کی حدیں (وہیلڈ روبوٹس سے سست)
      min_vel_x: 0.1            # استحکام کے لئے فارورڈ موشن برقرار رکھیں
      max_vel_x: 0.5            # 0.5 m/s زیادہ سے زیادہ چلنے کی رفتار
      min_vel_y: -0.2           # محدود لیٹرل موشن
      max_vel_y: 0.2
      max_vel_theta: 0.3        # 0.3 rad/s گھومنے کی رفتار

      # ایکسیلریشن کی حدیں (تولان کے لئے معتدل)
      acc_lim_x: 0.3            # 0.3 m/s² (نرم ایکسیلریشن)
      acc_lim_y: 0.2
      acc_lim_theta: 0.5
      decel_lim_x: -0.3         # نرم ڈی سیلریشن

      # ٹریجکٹری اسکورنگ
      critics: [
        "RotateToGoal",
        "Oscillation",
        "BaseObstacle",
        "GoalAlign",
        "PathAlign",
        "PathDist",
        "GoalDist"
      ]

      # کریٹک کے وزن (ہیومنوائڈ برتاؤ کے لئے ٹیون کریں)
      PathAlign.scale: 32.0      # گلوبل پاتھ کو فالو کرنے کی تاکید کریں
      GoalAlign.scale: 24.0      # گول کی طرف اورینٹ کریں
      PathDist.scale: 32.0
      GoalDist.scale: 24.0
      BaseObstacle.scale: 0.02   # رکاوٹ ایوائڈنس

      # سیمولیشن پیرامیٹرز
      sim_time: 2.0              # ٹریجکٹریز 2 سیکنڈ آگے سیمولیٹ کریں
      vx_samples: 10             # ہر طول و عرض میں 10 رفتاریں نمونہ لیں
      vy_samples: 5
      vtheta_samples: 10

      # ٹریجکٹری کنٹرینٹس
      trajectory_generator_name: "dwb_plugins::StandardTrajectoryGenerator"
```

## ریکوری برتاؤ

جب نیوی گیشن ناکام ہو جاتا ہے، ریکوری برتاؤ روبوٹ کو اٹکنے سے نکالنے کی کوشش کرتے ہیں۔

### ہیومنوائڈ محفوظ ریکوری ترتیب

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

    # ریکوری برتاؤ پیرامیٹرز
    global_frame: map
    robot_base_frame: base_link
    transform_tolerance: 0.1

    # ہیومنوائڈ کے لئے ریکوری ترتیب (نرم، مستحکم موشنز)
    default_nav_through_poses_bt_xml: ""
    default_nav_to_pose_bt_xml: ""

    # اسپن ریکوری - سینسرز کو صاف کرنے کے لئے جگہ پر گھومیں
    spin:
      simulate_ahead_time: 2.0
      max_rotational_vel: 0.2     # استحکام کے لئے سست گھومنا
      min_rotational_vel: 0.1
      rotational_acc_lim: 0.3

    # بیک اپ ریکوری - پیچھے کی طرف قدم
    backup:
      simulate_ahead_time: 2.0
      backup_dist: 0.3            # چھوٹا 30cm بیک اپ
      backup_speed: 0.1           # سست، کنٹرولڈ
```

## ہیومنوائڈ کے لئے Nav2 لانچ کرنا

```python
# humanoid_nav2_launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_dir = get_package_share_directory('humanoid_navigation')

    return LaunchDescription([
        # میپ سرور - پہلے سے تیار میپ لوڈ کریں
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[{
                'yaml_filename': os.path.join(pkg_dir, 'maps', 'office.yaml'),
                'use_sim_time': False
            }]
        ),

        # AMCL لوکلائزیشن
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            parameters=[os.path.join(pkg_dir, 'config', 'amcl_params.yaml')]
        ),

        # پلینر سرور
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            parameters=[os.path.join(pkg_dir, 'config', 'planner_params.yaml')]
        ),

        # کنٹرولر سرور
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            parameters=[os.path.join(pkg_dir, 'config', 'controller_params.yaml')]
        ),

        # ریکوری سرور
        Node(
            package='nav2_recoveries',
            executable='recoveries_server',
            name='recoveries_server',
            parameters=[os.path.join(pkg_dir, 'config', 'recovery_params.yaml')]
        ),

        # بیہیویئر ٹری نیوی گیٹر
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            parameters=[os.path.join(pkg_dir, 'config', 'bt_navigator_params.yaml')]
        ),

        # لائف سائیکل مینیجر
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

## ورزشیں

1. **کوسٹ میپ ٹیوننگ**: اپنے سیمولیٹڈ ہیومنوائڈ کے لئے فُٹ پرینٹ اور انفلیشن ریڈیس ایڈجسٹ کریں۔ پاتھ پلاننگ پر اثرات دیکھیں۔

2. **الگوری دھم موازنہ**: Dijkstra اور A* پلینرز کے ساتھ نیوی گیشن چلائیں۔ منصوبہ بندی کا وقت اور پاتھ لمبائی کے فرق کا پیمائش کریں۔

3. **ریکوری ٹیسٹنگ**: روبوٹ کو تنگ کونے میں رکھیں اور ریکوری برتاؤ متحرک کریں۔ دیکھیں کہ کون سی ترتیب کامیابی سے نکل جاتی ہے۔

4. **ڈائنامک رکاوٹیں**: ماحول میں متحرک رکاوٹیں شامل کریں اور دیکھیں کہ مقامی پلینر کا ایوائڈنس برتاؤ کیسا ہے۔

---

**اگلا**: [ہفتہ 10 - بائی پیڈل لوکوموشن](./week-10-bipedal-locomotion.md)