# Week 13: Capstone Implementation - Complete System Integration

![Capstone Implementation](/img/ai-16.png)

## Step-by-Step Integration Guide

This chapter provides a complete implementation of the VLA capstone system, integrating voice recognition, LLM planning, visual grounding, navigation, manipulation, and natural language feedback. Each component builds on previous modules to create a fully autonomous humanoid assistant.

## Part 1: Voice-to-Intent Pipeline

### Wake-Word Detection and Command Capture

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import whisper
import sounddevice as sd
import numpy as np
import threading
import queue

class VoiceCommandNode(Node):
    """
    ROS 2 node for continuous voice command recognition.
    Implements wake-word detection and Whisper transcription.
    """

    def __init__(self):
        super().__init__('voice_command_node')

        # Publisher for transcribed commands
        self.command_pub = self.create_publisher(String, '/voice_commands', 10)

        # Load Whisper model for speech recognition
        self.get_logger().info("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")

        # Audio configuration
        self.sample_rate = 16000
        self.wake_word = "hey robot"
        self.listening = False

        # Audio queue for background recording
        self.audio_queue = queue.Queue()

        # Start audio capture thread
        self.audio_thread = threading.Thread(target=self._audio_capture_loop, daemon=True)
        self.audio_thread.start()

        self.get_logger().info("Voice command system ready. Say 'Hey Robot' to activate.")

    def _audio_capture_loop(self):
        """
        Continuously capture audio and process for wake-word detection.
        Runs in background thread to avoid blocking ROS callbacks.
        """
        while True:
            # Record 3-second chunks
            audio = sd.rec(
                int(3 * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()

            # Transcribe audio
            audio_flat = audio.flatten()
            result = self.whisper_model.transcribe(
                audio_flat,
                language='en',
                fp16=False  # CPU compatibility
            )

            transcription = result['text'].lower().strip()
            self.get_logger().debug(f"Heard: {transcription}")

            # Check for wake-word
            if self.wake_word in transcription:
                self.get_logger().info("Wake-word detected! Listening for command...")
                self._capture_command()

    def _capture_command(self):
        """
        Record longer audio segment for command after wake-word.
        """
        # Record 5-second command
        self.get_logger().info("Recording command...")
        audio = sd.rec(
            int(5 * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()

        # Transcribe command
        audio_flat = audio.flatten()
        result = self.whisper_model.transcribe(audio_flat, language='en', fp16=False)

        command = result['text'].strip()
        self.get_logger().info(f"Command received: {command}")

        # Publish command to planning system
        msg = String()
        msg.data = command
        self.command_pub.publish(msg)

def main():
    rclpy.init()
    node = VoiceCommandNode()
    rclpy.spin(node)
```

## Part 2: LLM Planning Integration

### ReAct Task Executor with ROS 2

```python
import openai
import os
import json
from typing import Dict, List, Tuple
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge

openai.api_key = os.getenv("OPENAI_API_KEY")

class VLAExecutorNode(Node):
    """
    Main execution node integrating LLM planning with robot actions.
    Implements ReAct pattern for adaptive task execution.
    """

    def __init__(self):
        super().__init__('vla_executor')

        # Subscribe to voice commands
        self.cmd_sub = self.create_subscription(
            String,
            '/voice_commands',
            self.command_callback,
            10
        )

        # Subscribe to camera feed for visual grounding
        self.image_sub = self.create_subscription(
            Image,
            '/camera/rgb/image_raw',
            self.image_callback,
            10
        )

        # Publishers for robot control
        self.nav_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.grasp_pub = self.create_publisher(String, '/grasp_command', 10)
        self.speech_pub = self.create_publisher(String, '/tts_output', 10)

        # State tracking
        self.current_image = None
        self.bridge = CvBridge()
        self.world_state = {
            "robot_location": "living_room",
            "held_object": None,
            "known_objects": {}
        }

        self.execution_history = []
        self.get_logger().info("VLA Executor ready.")

    def image_callback(self, msg):
        """Store latest camera image for visual grounding."""
        self.current_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')

    def command_callback(self, msg):
        """
        Receive voice command and execute using ReAct loop.

        Args:
            msg: String message containing natural language command
        """
        command = msg.data
        self.get_logger().info(f"Executing command: {command}")

        # Generate initial plan with GPT-4
        plan = self._generate_plan(command)

        # Execute plan with ReAct loop
        success = self._execute_react_loop(command, plan)

        if success:
            self._speak("Task completed successfully!")
        else:
            self._speak("I encountered a problem and couldn't complete the task.")

    def _generate_plan(self, goal: str) -> List[Dict]:
        """
        Use GPT-4 to decompose goal into action sequence.

        Returns:
            List of action dictionaries with 'type', 'parameters'
        """
        system_prompt = """You are a task planner for a humanoid robot.
        Generate step-by-step plans using these actions:

        - navigate(location): Move to location
        - locate(object_description): Find object using camera
        - approach(object): Move close to object for manipulation
        - grasp(object): Pick up object
        - place(object, location): Put down object
        - check(condition): Verify environment state

        Return JSON array: [{"action": "type", "params": {...}}, ...]
        """

        user_prompt = f"""Goal: {goal}

        Current state:
        - Robot location: {self.world_state['robot_location']}
        - Held object: {self.world_state['held_object']}

        Generate action plan:
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        # Parse JSON plan
        plan_text = response.choices[0].message.content
        try:
            # Extract JSON from response
            start = plan_text.find('[')
            end = plan_text.rfind(']') + 1
            plan = json.loads(plan_text[start:end])
            return plan
        except json.JSONDecodeError:
            self.get_logger().error("Failed to parse plan from LLM")
            return []

    def _execute_react_loop(self, goal: str, initial_plan: List[Dict]) -> bool:
        """
        Execute plan with adaptive replanning based on observations.

        Args:
            goal: Original user goal
            initial_plan: Initial action sequence from LLM

        Returns:
            bool: True if goal achieved
        """
        plan = initial_plan
        step = 0
        max_steps = 20

        while step < max_steps:
            if not plan:
                self.get_logger().info("Plan complete!")
                return True

            # Get next action
            action = plan[0]
            self.get_logger().info(f"Step {step}: {action}")

            # Execute action and get observation
            success, observation = self._execute_action(action)

            # Update execution history
            self.execution_history.append({
                "step": step,
                "action": action,
                "success": success,
                "observation": observation
            })

            if success:
                # Remove completed action from plan
                plan = plan[1:]
                self._speak(f"Completed: {action['action']}")
            else:
                # Replan on failure
                self.get_logger().warn(f"Action failed: {observation}")
                self._speak(f"Hmm, {observation}. Let me try a different approach.")

                # Generate new plan from current state
                plan = self._replan(goal, observation)

                if not plan:
                    self.get_logger().error("Unable to replan. Task failed.")
                    return False

            step += 1

        self.get_logger().warn("Max steps reached without completion.")
        return False

    def _execute_action(self, action: Dict) -> Tuple[bool, str]:
        """
        Execute single action and return result.

        Returns:
            (success, observation): Execution result and observation
        """
        action_type = action['action']
        params = action.get('params', {})

        if action_type == 'navigate':
            return self._navigate(params['location'])

        elif action_type == 'locate':
            return self._locate_object(params['object_description'])

        elif action_type == 'approach':
            return self._approach_object(params['object'])

        elif action_type == 'grasp':
            return self._grasp_object(params['object'])

        elif action_type == 'place':
            return self._place_object(params['location'])

        elif action_type == 'check':
            return self._check_condition(params['condition'])

        else:
            return False, f"Unknown action type: {action_type}"

    def _navigate(self, location: str) -> Tuple[bool, str]:
        """Navigate to location using Nav2."""
        self.get_logger().info(f"Navigating to {location}...")

        # In real implementation: publish nav goal and wait for result
        # Mock success for demonstration
        self.world_state['robot_location'] = location
        return True, f"Arrived at {location}"

    def _locate_object(self, description: str) -> Tuple[bool, str]:
        """
        Use CLIP to find object in camera view.

        Returns:
            (success, observation): Whether found and location description
        """
        if self.current_image is None:
            return False, "No camera image available"

        # Use CLIP visual grounding (from Week 12)
        # Simplified for demonstration
        from PIL import Image as PILImage
        import clip
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)

        # Convert image
        pil_image = PILImage.fromarray(self.current_image)
        image_input = preprocess(pil_image).unsqueeze(0).to(device)

        # Search for object
        text_input = clip.tokenize([description, "empty scene"]).to(device)

        with torch.no_grad():
            image_features = model.encode_image(image_input)
            text_features = model.encode_text(text_input)

            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            similarity = (image_features @ text_features.T).squeeze(0)
            probs = similarity.softmax(dim=0)

        # Check if object detected with confidence
        if probs[0] > 0.7:
            # Store in world state
            self.world_state['known_objects'][description] = {
                "location": self.world_state['robot_location'],
                "confidence": float(probs[0])
            }
            return True, f"Found {description} with confidence {probs[0]:.2f}"
        else:
            return False, f"Could not find {description} in view"

    def _grasp_object(self, object_name: str) -> Tuple[bool, str]:
        """Execute grasp using MoveIt2."""
        self.get_logger().info(f"Grasping {object_name}...")

        # Publish grasp command to manipulation controller
        msg = String()
        msg.data = f"grasp:{object_name}"
        self.grasp_pub.publish(msg)

        # Mock success
        self.world_state['held_object'] = object_name
        return True, f"Successfully grasped {object_name}"

    def _place_object(self, location: str) -> Tuple[bool, str]:
        """Place held object at location."""
        if self.world_state['held_object'] is None:
            return False, "Not holding any object"

        object_name = self.world_state['held_object']
        self.get_logger().info(f"Placing {object_name} at {location}...")

        # Publish place command
        msg = String()
        msg.data = f"place:{location}"
        self.grasp_pub.publish(msg)

        self.world_state['held_object'] = None
        return True, f"Placed {object_name} at {location}"

    def _approach_object(self, object_name: str) -> Tuple[bool, str]:
        """Move close to object for manipulation."""
        if object_name not in self.world_state['known_objects']:
            return False, f"Location of {object_name} unknown"

        # Navigate to object location
        obj_info = self.world_state['known_objects'][object_name]
        return True, f"Approached {object_name}"

    def _check_condition(self, condition: str) -> Tuple[bool, str]:
        """Verify environmental condition using vision/sensors."""
        # Use GPT-4V for visual question answering
        # Simplified for demonstration
        return True, f"Checked: {condition}"

    def _replan(self, goal: str, failure_reason: str) -> List[Dict]:
        """
        Generate new plan after failure using failure observation.
        """
        prompt = f"""Original goal: {goal}

        Previous plan failed because: {failure_reason}

        Execution history:
        {json.dumps(self.execution_history[-3:], indent=2)}

        Current state:
        {json.dumps(self.world_state, indent=2)}

        Generate alternative plan as JSON array:
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        # Parse new plan
        plan_text = response.choices[0].message.content
        try:
            start = plan_text.find('[')
            end = plan_text.rfind(']') + 1
            new_plan = json.loads(plan_text[start:end])
            return new_plan
        except:
            return []

    def _speak(self, text: str):
        """
        Generate speech output via TTS.
        """
        self.get_logger().info(f"Speaking: {text}")

        # Publish to TTS node
        msg = String()
        msg.data = text
        self.speech_pub.publish(msg)

def main():
    rclpy.init()
    node = VLAExecutorNode()
    rclpy.spin(node)
```

## Part 3: Text-to-Speech Feedback Node

```python
import pyttsx3

class TTSNode(Node):
    """
    Text-to-Speech node for natural language feedback.
    """

    def __init__(self):
        super().__init__('tts_node')

        # Subscribe to speech requests
        self.subscription = self.create_subscription(
            String,
            '/tts_output',
            self.speak_callback,
            10
        )

        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Words per minute
        self.engine.setProperty('volume', 0.9)

        self.get_logger().info("TTS system ready.")

    def speak_callback(self, msg):
        """Convert text to speech."""
        text = msg.data
        self.get_logger().info(f"Speaking: {text}")

        # Synthesize speech (non-blocking)
        self.engine.say(text)
        self.engine.runAndWait()

def main():
    rclpy.init()
    node = TTSNode()
    rclpy.spin(node)
```

## Part 4: Launch File for Complete System

```python
# launch/vla_capstone.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Voice command node
        Node(
            package='vla_capstone',
            executable='voice_command_node',
            name='voice_command',
            output='screen'
        ),

        # VLA executor (planning + vision + control)
        Node(
            package='vla_capstone',
            executable='vla_executor_node',
            name='vla_executor',
            output='screen',
            parameters=[{
                'use_sim_time': False
            }]
        ),

        # Text-to-speech feedback
        Node(
            package='vla_capstone',
            executable='tts_node',
            name='tts',
            output='screen'
        ),

        # Camera driver (replace with actual camera node)
        Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            name='camera',
            parameters=[{
                'video_device': '/dev/video0',
                'framerate': 30.0,
                'image_width': 640,
                'image_height': 480
            }]
        )
    ])
```

## Running the Complete System

```bash
# Terminal 1: Launch core robot systems (simulation or hardware)
ros2 launch your_robot_description robot.launch.py

# Terminal 2: Launch VLA capstone system
ros2 launch vla_capstone vla_capstone.launch.py

# Terminal 3: Monitor execution
ros2 topic echo /voice_commands
ros2 topic echo /tts_output

# Terminal 4: Visualization
rviz2 -d vla_capstone.rviz
```

## Testing the System

### Test 1: Simple Fetch Task
**Command**: "Hey robot, bring me the red mug from the table."

**Expected Behavior**:
1. System confirms: "Navigating to table..."
2. Locates red mug using CLIP
3. Approaches and grasps mug
4. Returns: "Here is your red mug."

### Test 2: Multi-Step Task
**Command**: "Clear the desk by moving all mugs to the dish rack."

**Expected Behavior**:
1. Navigates to desk
2. Iteratively locates mugs
3. For each mug: grasp → navigate to dish rack → place
4. Confirms: "Desk cleared. Moved 3 mugs to dish rack."

### Test 3: Adaptive Replanning
**Command**: "Get the laptop from the bedroom."

**Expected Behavior**:
1. Navigates to bedroom
2. If laptop not found: "I don't see a laptop in the bedroom. Should I check another room?"
3. User: "Try the living room."
4. Replans and searches living room

## Optimization and Debugging

**Performance Tuning**:
- Use `gpt-3.5-turbo` for faster planning (3x speedup over GPT-4)
- Cache CLIP embeddings for known objects
- Run perception in separate thread to avoid blocking

**Common Issues**:
- **Whisper latency**: Use `tiny` or `base` model; consider distil-whisper
- **CLIP false positives**: Increase confidence threshold to 0.8+
- **Plan failures**: Add more few-shot examples to system prompt
- **TTS blocking**: Run in separate process or use async synthesis

## Conclusion

You have now built a complete Vision-Language-Action system integrating speech recognition, LLM planning, visual grounding, and robot control. This represents the current state-of-the-art in embodied AI, demonstrating how foundation models (GPT-4, CLIP, Whisper) can be orchestrated for real-world robotic applications.

**Next Steps**:
- Deploy on physical humanoid platform
- Add more sophisticated error recovery (human-in-the-loop requests)
- Implement memory persistence (remember object locations across sessions)
- Integrate advanced manipulation (dexterous grasping, tool use)
- Extend to multi-robot collaboration

Congratulations on completing Module 4! You are now equipped to build next-generation autonomous humanoid robots with conversational AI capabilities.
