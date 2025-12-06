# 🛠️ Action Sequencer

**Skill ID:** `Skill_ActionSequencer_v1.0`
**Goal:** To simulate the Cognitive Planning logic by breaking down a high-level goal into a sequence of actionable, low-level robot commands.

## 💻 Core Function Signature
`plan_robot_action_sequence(high_level_goal: str, robot_capabilities: list) -> list`

## ⚙️ Function Description
Takes a complex user instruction and outputs a clean, logical sequence of executable robot commands.

## 🔑 Usage Context
Used by the **Chapter_Composer** agent for the VLA module example.