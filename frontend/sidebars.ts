import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: ROS 2 Fundamentals',
      collapsed: false,
      items: [
        'module-01-ros2/intro',
        'module-01-ros2/week-3-basics',
        'module-01-ros2/week-3-nodes-topics',
        'module-01-ros2/week-4-services-actions',
        'module-01-ros2/week-5-urdf',
        'module-01-ros2/week-5-control',
        'module-01-ros2/week-5-complete-urdf',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Gazebo & Unity Simulation',
      collapsed: false,
      items: [
        'module-02-simulation/intro',
        'module-02-simulation/week-6-gazebo-basics',
        'module-02-simulation/week-6-physics',
        'module-02-simulation/week-7-sensors',
        'module-02-simulation/week-7-unity',
        'module-02-simulation/week-7-worlds',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: NVIDIA Isaac Platform',
      collapsed: false,
      items: [
        'module-03-isaac/intro',
        'module-03-isaac/week-8-isaac-sim',
        'module-03-isaac/week-8-synthetic-data',
        'module-03-isaac/week-9-isaac-ros',
        'module-03-isaac/week-9-perception',
        'module-03-isaac/week-10-nav2',
        'module-03-isaac/week-10-bipedal-locomotion',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      collapsed: false,
      items: [
        'module-04-vla/intro',
        'module-04-vla/week-11-voice-to-action',
        'module-04-vla/week-11-llm-planning',
        'module-04-vla/week-12-multimodal',
        'module-04-vla/week-12-gesture-recognition',
        'module-04-vla/week-13-capstone-intro',
        'module-04-vla/week-13-capstone-implementation',
      ],
    },
  ],
};

export default sidebars;
