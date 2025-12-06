# 🛠️ Model XML Tool

**Skill ID:** `Skill_ModelXMLTool_v1.0`
**Goal:** To generate validated URDF/SDF XML code for robot models (Gazebo/ROS 2).

## 💻 Core Function Signature
`generate_robot_model_xml(robot_name: str, components: list, format: str = 'URDF') -> str`

## ⚙️ Function Description
Accepts component list and returns ROS 2/Gazebo compliant XML code.

## 🔑 Usage Context
Used by the **BOM_Configurator** and **Chapter_Composer** agents.