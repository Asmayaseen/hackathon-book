# ہفتہ 13: کیپ سٹون امپلیمنٹیشن - مکمل سسٹم انٹیگریشن

![کیپ سٹون امپلیمنٹیشن](/img/ai-16.png)

## قدم بہ قدم انٹیگریشن گائیڈ

یہ باب VLA کیپ سٹون سسٹم کی مکمل implementation فراہم کرتا ہے، جو voice recognition، LLM planning، visual grounding، navigation، manipulation، اور natural language feedback کو یکجا کرتا ہے۔ ہر component پچھلے modules پر بنتا ہے تاکہ ایک مکمل طور پر خودکار humanoid assistant تیار کیا جائے۔

## حصہ 1: Voice-to-Intent Pipeline

### Wake-Word Detection اور Command Capture

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
    مسلسل voice command recognition کے لیے ROS 2 node۔
    Wake-word detection اور Whisper transcription کو implement کرتا ہے۔
    """

    def __init__(self):
        super().__init__('voice_command_node')

        # Transcribed commands کے لیے Publisher
        self.command_pub = self.create_publisher(String, '/voice_commands', 10)

        # Speech recognition کے لیے Whisper model load کریں
        self.get_logger().info("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")

        # Audio configuration
        self.sample_rate = 16000
        self.wake_word = "hey robot"
        self.listening = False

        # Background recording کے لیے Audio queue
        self.audio_queue = queue.Queue()

        # Audio capture thread شروع کریں
        self.audio_thread = threading.Thread(target=self._audio_capture_loop, daemon=True)
        self.audio_thread.start()

        self.get_logger().info("Voice command system ready. Say 'Hey Robot' to activate.")

    def _audio_capture_loop(self):
        """
        مسلسل audio capture کریں اور wake-word detection کے لیے process کریں۔
        ROS callbacks کو block کرنے سے بچنے کے لیے background thread میں چلتا ہے۔
        """
        while True:
            # 3-سیکنڈ کے chunks record کریں
            audio = sd.rec(
                int(3 * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()

            # Audio کو transcribe کریں
            audio_flat = audio.flatten()
            result = self.whisper_model.transcribe(
                audio_flat,
                language='en',
                fp16=False  # CPU compatibility
            )

            transcription = result['text'].lower().strip()
            self.get_logger().debug(f"Heard: {transcription}")

            # Wake-word کے لیے check کریں
            if self.wake_word in transcription:
                self.get_logger().info("Wake-word detected! Listening for command...")
                self._capture_command()

    def _capture_command(self):
        """
        Wake-word کے بعد command کے لیے لمبا audio segment record کریں۔
        """
        # 5-سیکنڈ کی command record کریں
        self.get_logger().info("Recording command...")
        audio = sd.rec(
            int(5 * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()

        # Command کو transcribe کریں
        audio_flat = audio.flatten()
        result = self.whisper_model.transcribe(audio_flat, language='en', fp16=False)

        command = result['text'].strip()
        self.get_logger().info(f"Command received: {command}")

        # Planning system کو command publish کریں
        msg = String()
        msg.data = command
        self.command_pub.publish(msg)

def main():
    rclpy.init()
    node = VoiceCommandNode()
    rclpy.spin(node)
```

## حصہ 2: LLM Planning Integration

### ROS 2 کے ساتھ ReAct Task Executor

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
    LLM planning کو robot actions کے ساتھ integrate کرنے والا Main execution node۔
    Adaptive task execution کے لیے ReAct pattern کو implement کرتا ہے۔
    """

    def __init__(self):
        super().__init__('vla_executor')

        # Voice commands کو subscribe کریں
        self.cmd_sub = self.create_subscription(
            String,
            '/voice_commands',
            self.command_callback,
            10
        )

        # Visual grounding کے لیے camera feed کو subscribe کریں
        self.image_sub = self.create_subscription(
            Image,
            '/camera/rgb/image_raw',
            self.image_callback,
            10
        )

        # Robot control کے لیے Publishers
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
        """Visual grounding کے لیے تازہ ترین camera image store کریں۔"""
        self.current_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')

    def command_callback(self, msg):
        """
        Voice command وصول کریں اور ReAct loop استعمال کرتے ہوئے execute کریں۔

        Args:
            msg: Natural language command پر مشتمل String message
        """
        command = msg.data
        self.get_logger().info(f"Executing command: {command}")

        # GPT-4 کے ساتھ ابتدائی plan بنائیں
        plan = self._generate_plan(command)

        # ReAct loop کے ساتھ plan execute کریں
        success = self._execute_react_loop(command, plan)

        if success:
            self._speak("Task completed successfully!")
        else:
            self._speak("I encountered a problem and couldn't complete the task.")

    def _generate_plan(self, goal: str) -> List[Dict]:
        """
        Goal کو action sequence میں decompose کرنے کے لیے GPT-4 استعمال کریں۔

        Returns:
            'type', 'parameters' کے ساتھ action dictionaries کی List
        """
        system_prompt = """آپ ایک humanoid robot کے لیے task planner ہیں۔
        ان actions کا استعمال کرتے ہوئے step-by-step plans بنائیں:

        - navigate(location): Location پر جائیں
        - locate(object_description): Camera استعمال کر کے object تلاش کریں
        - approach(object): Manipulation کے لیے object کے قریب جائیں
        - grasp(object): Object اٹھائیں
        - place(object, location): Object رکھیں
        - check(condition): Environment state کی تصدیق کریں

        JSON array واپس کریں: [{"action": "type", "params": {...}}, ...]
        """

        user_prompt = f"""Goal: {goal}

        موجودہ state:
        - Robot کی location: {self.world_state['robot_location']}
        - ہاتھ میں object: {self.world_state['held_object']}

        Action plan بنائیں:
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        # JSON plan کو parse کریں
        plan_text = response.choices[0].message.content
        try:
            # Response سے JSON نکالیں
            start = plan_text.find('[')
            end = plan_text.rfind(']') + 1
            plan = json.loads(plan_text[start:end])
            return plan
        except json.JSONDecodeError:
            self.get_logger().error("Failed to parse plan from LLM")
            return []

    def _execute_react_loop(self, goal: str, initial_plan: List[Dict]) -> bool:
        """
        Observations کی بنیاد پر adaptive replanning کے ساتھ plan execute کریں۔

        Args:
            goal: اصل user goal
            initial_plan: LLM سے ابتدائی action sequence

        Returns:
            bool: اگر goal حاصل ہو تو True
        """
        plan = initial_plan
        step = 0
        max_steps = 20

        while step < max_steps:
            if not plan:
                self.get_logger().info("Plan complete!")
                return True

            # اگلا action حاصل کریں
            action = plan[0]
            self.get_logger().info(f"Step {step}: {action}")

            # Action execute کریں اور observation حاصل کریں
            success, observation = self._execute_action(action)

            # Execution history کو update کریں
            self.execution_history.append({
                "step": step,
                "action": action,
                "success": success,
                "observation": observation
            })

            if success:
                # مکمل شدہ action کو plan سے ہٹائیں
                plan = plan[1:]
                self._speak(f"Completed: {action['action']}")
            else:
                # ناکامی پر replan کریں
                self.get_logger().warn(f"Action failed: {observation}")
                self._speak(f"Hmm, {observation}. Let me try a different approach.")

                # موجودہ state سے نیا plan بنائیں
                plan = self._replan(goal, observation)

                if not plan:
                    self.get_logger().error("Unable to replan. Task failed.")
                    return False

            step += 1

        self.get_logger().warn("Max steps reached without completion.")
        return False

    def _execute_action(self, action: Dict) -> Tuple[bool, str]:
        """
        ایک action execute کریں اور نتیجہ واپس کریں۔

        Returns:
            (success, observation): Execution کا نتیجہ اور observation
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
            return False, f"نامعلوم action type: {action_type}"

    def _navigate(self, location: str) -> Tuple[bool, str]:
        """Nav2 استعمال کر کے location پر جائیں۔"""
        self.get_logger().info(f"Navigating to {location}...")

        # حقیقی implementation میں: nav goal publish کریں اور نتیجہ کا انتظار کریں
        # مظاہرے کے لیے Mock success
        self.world_state['robot_location'] = location
        return True, f"{location} پر پہنچ گئے"

    def _locate_object(self, description: str) -> Tuple[bool, str]:
        """
        Camera view میں object تلاش کرنے کے لیے CLIP استعمال کریں۔

        Returns:
            (success, observation): ملا یا نہیں اور location کی تفصیل
        """
        if self.current_image is None:
            return False, "کوئی camera image دستیاب نہیں"

        # CLIP visual grounding استعمال کریں (ہفتہ 12 سے)
        # مظاہرے کے لیے آسان بنایا گیا
        from PIL import Image as PILImage
        import clip
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)

        # Image کو convert کریں
        pil_image = PILImage.fromarray(self.current_image)
        image_input = preprocess(pil_image).unsqueeze(0).to(device)

        # Object کے لیے تلاش کریں
        text_input = clip.tokenize([description, "empty scene"]).to(device)

        with torch.no_grad():
            image_features = model.encode_image(image_input)
            text_features = model.encode_text(text_input)

            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            similarity = (image_features @ text_features.T).squeeze(0)
            probs = similarity.softmax(dim=0)

        # Confidence کے ساتھ object کا پتہ لگایا گیا ہے یا نہیں check کریں
        if probs[0] > 0.7:
            # World state میں store کریں
            self.world_state['known_objects'][description] = {
                "location": self.world_state['robot_location'],
                "confidence": float(probs[0])
            }
            return True, f"{description} ملا confidence {probs[0]:.2f} کے ساتھ"
        else:
            return False, f"View میں {description} نہیں مل سکا"

    def _grasp_object(self, object_name: str) -> Tuple[bool, str]:
        """MoveIt2 استعمال کر کے grasp execute کریں۔"""
        self.get_logger().info(f"Grasping {object_name}...")

        # Manipulation controller کو grasp command publish کریں
        msg = String()
        msg.data = f"grasp:{object_name}"
        self.grasp_pub.publish(msg)

        # Mock success
        self.world_state['held_object'] = object_name
        return True, f"{object_name} کامیابی سے پکڑا گیا"

    def _place_object(self, location: str) -> Tuple[bool, str]:
        """ہاتھ میں موجود object کو location پر رکھیں۔"""
        if self.world_state['held_object'] is None:
            return False, "کوئی object ہاتھ میں نہیں"

        object_name = self.world_state['held_object']
        self.get_logger().info(f"Placing {object_name} at {location}...")

        # Place command publish کریں
        msg = String()
        msg.data = f"place:{location}"
        self.grasp_pub.publish(msg)

        self.world_state['held_object'] = None
        return True, f"{object_name} کو {location} پر رکھ دیا گیا"

    def _approach_object(self, object_name: str) -> Tuple[bool, str]:
        """Manipulation کے لیے object کے قریب جائیں۔"""
        if object_name not in self.world_state['known_objects']:
            return False, f"{object_name} کی location نامعلوم"

        # Object کی location پر navigate کریں
        obj_info = self.world_state['known_objects'][object_name]
        return True, f"{object_name} کے قریب پہنچ گئے"

    def _check_condition(self, condition: str) -> Tuple[bool, str]:
        """Vision/sensors استعمال کر کے environmental condition کی تصدیق کریں۔"""
        # Visual question answering کے لیے GPT-4V استعمال کریں
        # مظاہرے کے لیے آسان بنایا گیا
        return True, f"چیک کیا گیا: {condition}"

    def _replan(self, goal: str, failure_reason: str) -> List[Dict]:
        """
        ناکامی کی observation استعمال کر کے ناکامی کے بعد نیا plan بنائیں۔
        """
        prompt = f"""اصل goal: {goal}

        پچھلا plan ناکام ہو گیا کیونکہ: {failure_reason}

        Execution history:
        {json.dumps(self.execution_history[-3:], indent=2)}

        موجودہ state:
        {json.dumps(self.world_state, indent=2)}

        متبادل plan بطور JSON array بنائیں:
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        # نیا plan parse کریں
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
        TTS کے ذریعے speech output بنائیں۔
        """
        self.get_logger().info(f"Speaking: {text}")

        # TTS node کو publish کریں
        msg = String()
        msg.data = text
        self.speech_pub.publish(msg)

def main():
    rclpy.init()
    node = VLAExecutorNode()
    rclpy.spin(node)
```

## حصہ 3: Text-to-Speech Feedback Node

```python
import pyttsx3

class TTSNode(Node):
    """
    Natural language feedback کے لیے Text-to-Speech node۔
    """

    def __init__(self):
        super().__init__('tts_node')

        # Speech requests کو subscribe کریں
        self.subscription = self.create_subscription(
            String,
            '/tts_output',
            self.speak_callback,
            10
        )

        # TTS engine شروع کریں
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # الفاظ فی منٹ
        self.engine.setProperty('volume', 0.9)

        self.get_logger().info("TTS system ready.")

    def speak_callback(self, msg):
        """Text کو speech میں تبدیل کریں۔"""
        text = msg.data
        self.get_logger().info(f"Speaking: {text}")

        # Speech کو synthesize کریں (non-blocking)
        self.engine.say(text)
        self.engine.runAndWait()

def main():
    rclpy.init()
    node = TTSNode()
    rclpy.spin(node)
```

## حصہ 4: مکمل سسٹم کے لیے Launch File

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

        # Camera driver (اصل camera node سے تبدیل کریں)
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

## مکمل سسٹم چلانا

```bash
# ٹرمینل 1: بنیادی robot systems شروع کریں (simulation یا hardware)
ros2 launch your_robot_description robot.launch.py

# ٹرمینل 2: VLA capstone system شروع کریں
ros2 launch vla_capstone vla_capstone.launch.py

# ٹرمینل 3: Execution کو monitor کریں
ros2 topic echo /voice_commands
ros2 topic echo /tts_output

# ٹرمینل 4: Visualization
rviz2 -d vla_capstone.rviz
```

## سسٹم کی جانچ

### ٹیسٹ 1: سادہ Fetch Task
**کمانڈ**: "Hey robot, bring me the red mug from the table."

**متوقع رویہ**:
1. سسٹم تصدیق کرتا ہے: "Navigating to table..."
2. CLIP استعمال کر کے سرخ mug کا پتہ لگاتا ہے
3. قریب جاتا ہے اور mug پکڑتا ہے
4. واپس آتا ہے: "Here is your red mug."

### ٹیسٹ 2: کثیر مرحلہ Task
**کمانڈ**: "Clear the desk by moving all mugs to the dish rack."

**متوقع رویہ**:
1. Desk پر جاتا ہے
2. بار بار mugs کا پتہ لگاتا ہے
3. ہر mug کے لیے: پکڑنا → dish rack پر جانا → رکھنا
4. تصدیق کرتا ہے: "Desk cleared. Moved 3 mugs to dish rack."

### ٹیسٹ 3: Adaptive Replanning
**کمانڈ**: "Get the laptop from the bedroom."

**متوقع رویہ**:
1. Bedroom میں جاتا ہے
2. اگر laptop نہیں ملتا: "I don't see a laptop in the bedroom. Should I check another room?"
3. صارف: "Try the living room."
4. Replan کرتا ہے اور living room میں تلاش کرتا ہے

## Optimization اور Debugging

**Performance Tuning**:
- تیز تر planning کے لیے `gpt-3.5-turbo` استعمال کریں (GPT-4 سے 3x speedup)
- معلوم objects کے لیے CLIP embeddings cache کریں
- Blocking سے بچنے کے لیے الگ thread میں perception چلائیں

**عام مسائل**:
- **Whisper latency**: `tiny` یا `base` model استعمال کریں؛ distil-whisper پر غور کریں
- **CLIP false positives**: Confidence threshold 0.8+ تک بڑھائیں
- **Plan failures**: System prompt میں مزید few-shot examples شامل کریں
- **TTS blocking**: الگ process میں چلائیں یا async synthesis استعمال کریں

## خلاصہ

اب آپ نے speech recognition، LLM planning، visual grounding، اور robot control کو یکجا کرنے والا ایک مکمل Vision-Language-Action سسٹم بنا لیا ہے۔ یہ embodied AI میں موجودہ جدید ترین صورتحال کی نمائندگی کرتا ہے، جو ظاہر کرتا ہے کہ کس طرح foundation models (GPT-4، CLIP، Whisper) کو حقیقی دنیا کی robotic applications کے لیے ترتیب دیا جا سکتا ہے۔

**اگلے اقدامات**:
- حقیقی humanoid platform پر deploy کریں
- مزید پیچیدہ error recovery شامل کریں (human-in-the-loop requests)
- Memory persistence کو implement کریں (sessions کے درمیان object locations یاد رکھیں)
- جدید manipulation کو یکجا کریں (dexterous grasping، tool use)
- کثیر robot تعاون تک توسیع کریں

Module 4 مکمل کرنے پر مبارکباد! اب آپ conversational AI صلاحیتوں کے ساتھ اگلی نسل کے خودکار humanoid robots بنانے کے لیے لیس ہیں۔
