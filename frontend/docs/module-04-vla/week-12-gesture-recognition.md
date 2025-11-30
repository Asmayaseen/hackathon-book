# Week 12: Gesture Recognition for Human-Robot Interaction

![Gesture Recognition](/img/ai-14.png)

## Hand Gesture Detection with MediaPipe

**MediaPipe** is Google's open-source framework for real-time perception pipelines, offering pre-trained models for hand tracking, pose estimation, face detection, and holistic body tracking. For humanoid robotics, hand gesture recognition enables non-verbal communication—pointing to objects, signaling stop/go, or demonstrating manipulation trajectories.

### Why MediaPipe for Robotics?

**Real-Time Performance**: MediaPipe achieves 30+ FPS on CPU and 60+ FPS on GPU, suitable for responsive human-robot interaction without specialized hardware.

**Cross-Platform**: Runs on Linux, Windows, mobile devices, and embedded systems (Raspberry Pi, Jetson Nano), enabling deployment on diverse robot platforms.

**Pre-Trained Models**: MediaPipe's hand tracker identifies 21 3D landmarks per hand (fingertips, knuckles, wrist) without custom training—no dataset annotation required.

**Multi-Hand Support**: Detects and tracks multiple hands simultaneously, distinguishing left/right hand and maintaining identity across frames.

### Installation and Basic Hand Tracking

```python
# Install MediaPipe and OpenCV for visualization
import subprocess
subprocess.run(["pip", "install", "mediapipe", "opencv-python", "numpy"])

import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def track_hands_in_video(video_source=0):
    """
    Real-time hand tracking from webcam or video file.

    Args:
        video_source: Camera index (0 for default webcam) or video file path
    """
    # Configure hand detector
    # max_num_hands: Maximum hands to detect (1-2 for most robotics tasks)
    # min_detection_confidence: Threshold for initial hand detection (0.0-1.0)
    # min_tracking_confidence: Threshold for landmark tracking (0.0-1.0)
    hands = mp_hands.Hands(
        static_image_mode=False,  # False for video stream (enables tracking)
        max_num_hands=2,
        min_detection_confidence=0.7,  # Higher = fewer false positives
        min_tracking_confidence=0.5
    )

    cap = cv2.VideoCapture(video_source)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Convert BGR to RGB (MediaPipe expects RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame to detect hands
        results = hands.process(frame_rgb)

        # Draw hand landmarks on frame
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw 21 landmarks and connections
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

        # Display annotated frame
        cv2.imshow('Hand Tracking', frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

# Run hand tracker
track_hands_in_video()
```

## Gesture Command Mapping

Map hand poses to robot commands by analyzing landmark configurations:

```python
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class HandGesture:
    """Represents a recognized gesture with confidence score."""
    name: str
    confidence: float
    parameters: Dict  # Additional info (e.g., pointing direction)

class GestureRecognizer:
    """
    Classify hand gestures from MediaPipe landmarks.
    Maps gestures to robot commands.
    """

    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Single hand for command gestures
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

    def recognize_gesture(self, frame: np.ndarray) -> Optional[HandGesture]:
        """
        Detect and classify gesture in image frame.

        Args:
            frame: BGR image from camera

        Returns:
            HandGesture object or None if no gesture detected
        """
        # Process frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if not results.multi_hand_landmarks:
            return None

        # Analyze first detected hand
        landmarks = results.multi_hand_landmarks[0]

        # Convert landmarks to numpy array for easier computation
        # Each landmark has x, y, z coordinates (normalized to [0, 1])
        points = np.array([
            [lm.x, lm.y, lm.z]
            for lm in landmarks.landmark
        ])

        # Classify gesture based on landmark configuration
        if self._is_thumbs_up(points):
            return HandGesture("thumbs_up", 0.95, {})
        elif self._is_pointing(points):
            direction = self._get_pointing_direction(points)
            return HandGesture("pointing", 0.90, {"direction": direction})
        elif self._is_open_palm(points):
            return HandGesture("stop", 0.92, {})
        elif self._is_closed_fist(points):
            return HandGesture("grab", 0.88, {})
        elif self._is_peace_sign(points):
            return HandGesture("peace", 0.85, {})

        return HandGesture("unknown", 0.5, {})

    def _is_thumbs_up(self, points: np.ndarray) -> bool:
        """
        Detect thumbs-up gesture.
        Criteria: Thumb tip above MCP joint, other fingers curled.
        """
        # Landmark indices (see MediaPipe hand landmark diagram)
        thumb_tip = points[4]
        thumb_mcp = points[2]
        index_tip = points[8]
        index_pip = points[6]

        # Thumb extended upward
        thumb_extended = thumb_tip[1] < thumb_mcp[1]  # y decreases upward

        # Other fingers curled (tip below PIP joint)
        fingers_curled = all([
            points[8][1] > points[6][1],   # Index
            points[12][1] > points[10][1],  # Middle
            points[16][1] > points[14][1],  # Ring
            points[20][1] > points[18][1]   # Pinky
        ])

        return thumb_extended and fingers_curled

    def _is_pointing(self, points: np.ndarray) -> bool:
        """
        Detect pointing gesture.
        Criteria: Index finger extended, other fingers curled.
        """
        # Index finger extended
        index_extended = points[8][1] < points[6][1]  # Tip above PIP

        # Other fingers curled
        other_curled = all([
            points[12][1] > points[10][1],  # Middle
            points[16][1] > points[14][1],  # Ring
            points[20][1] > points[18][1]   # Pinky
        ])

        return index_extended and other_curled

    def _is_open_palm(self, points: np.ndarray) -> bool:
        """
        Detect open palm (stop signal).
        Criteria: All fingers extended and spread.
        """
        # All fingertips above their respective MCP joints
        fingers_extended = all([
            points[4][1] < points[2][1],    # Thumb
            points[8][1] < points[5][1],    # Index
            points[12][1] < points[9][1],   # Middle
            points[16][1] < points[13][1],  # Ring
            points[20][1] < points[17][1]   # Pinky
        ])

        return fingers_extended

    def _is_closed_fist(self, points: np.ndarray) -> bool:
        """
        Detect closed fist (grab command).
        Criteria: All fingers curled below MCP joints.
        """
        all_curled = all([
            points[8][1] > points[5][1],    # Index
            points[12][1] > points[9][1],   # Middle
            points[16][1] > points[13][1],  # Ring
            points[20][1] > points[17][1]   # Pinky
        ])

        return all_curled

    def _is_peace_sign(self, points: np.ndarray) -> bool:
        """
        Detect peace sign (index + middle extended).
        """
        index_extended = points[8][1] < points[6][1]
        middle_extended = points[12][1] < points[10][1]
        ring_curled = points[16][1] > points[14][1]
        pinky_curled = points[20][1] > points[18][1]

        return index_extended and middle_extended and ring_curled and pinky_curled

    def _get_pointing_direction(self, points: np.ndarray) -> str:
        """
        Compute pointing direction from index finger orientation.

        Returns:
            Direction string: "left", "right", "up", "down", "forward"
        """
        # Vector from index MCP to tip
        mcp = points[5]
        tip = points[8]
        vector = tip - mcp

        # Analyze primary component
        if abs(vector[0]) > abs(vector[1]):
            return "right" if vector[0] > 0 else "left"
        else:
            return "down" if vector[1] > 0 else "up"

# Example: Real-time gesture recognition
recognizer = GestureRecognizer()
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    gesture = recognizer.recognize_gesture(frame)

    if gesture and gesture.confidence > 0.8:
        # Display recognized gesture
        text = f"{gesture.name} ({gesture.confidence:.2f})"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)

        # Execute robot command based on gesture
        if gesture.name == "pointing":
            print(f"Robot: Navigate {gesture.parameters['direction']}")
        elif gesture.name == "grab":
            print("Robot: Execute grasp")
        elif gesture.name == "stop":
            print("Robot: Emergency stop")

    cv2.imshow('Gesture Recognition', frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## Pose Estimation for Human-Robot Interaction

**Pose estimation** tracks full-body landmarks (33 points including shoulders, elbows, hips, knees) to understand human activity and spatial positioning. For collaborative robotics, this enables:

- **Proximity Detection**: Stop robot arm if human enters workspace
- **Activity Recognition**: Distinguish standing, sitting, walking for context-aware behavior
- **Gesture Demonstration**: Learn manipulation tasks by imitating human arm movements

### Full-Body Pose Tracking

```python
mp_pose = mp.solutions.pose

def track_human_pose(video_source=0):
    """
    Track human body pose for safety monitoring and imitation learning.

    Args:
        video_source: Camera index or video file
    """
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,  # 0=lite, 1=full, 2=heavy (higher = more accurate)
        smooth_landmarks=True,  # Temporal smoothing for video
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    cap = cv2.VideoCapture(video_source)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            # Draw pose skeleton
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )

            # Extract key joint positions for analysis
            landmarks = results.pose_landmarks.landmark
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

            # Example: Detect if hands are raised (y < 0.5)
            hands_raised = (left_wrist.y < 0.5 and right_wrist.y < 0.5)

            if hands_raised:
                cv2.putText(frame, "Hands Raised - Robot Paused", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Pose Tracking', frame)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pose.close()

# Run pose tracker
track_human_pose()
```

## Integrating Gestures with ROS 2

Connect gesture recognition to robot control:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class GestureControlNode(Node):
    """
    ROS 2 node that publishes robot commands based on hand gestures.
    """

    def __init__(self):
        super().__init__('gesture_control')

        # Publisher for gesture-based commands
        self.cmd_pub = self.create_publisher(String, '/gesture_commands', 10)

        # Timer for periodic gesture recognition
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10 Hz

        self.recognizer = GestureRecognizer()
        self.cap = cv2.VideoCapture(0)

        self.last_gesture = None
        self.gesture_stable_count = 0
        self.STABILITY_THRESHOLD = 5  # Require 5 consecutive frames for confirmation

    def timer_callback(self):
        """Process camera frame and publish gesture commands."""
        success, frame = self.cap.read()
        if not success:
            return

        gesture = self.recognizer.recognize_gesture(frame)

        if gesture and gesture.confidence > 0.85:
            # Require gesture stability to avoid false triggers
            if gesture.name == self.last_gesture:
                self.gesture_stable_count += 1
            else:
                self.gesture_stable_count = 0
                self.last_gesture = gesture.name

            # Publish command if gesture is stable
            if self.gesture_stable_count >= self.STABILITY_THRESHOLD:
                msg = String()
                msg.data = f"{gesture.name}:{gesture.parameters}"
                self.cmd_pub.publish(msg)

                self.get_logger().info(f"Published gesture command: {gesture.name}")

                # Reset to avoid repeated commands
                self.gesture_stable_count = 0

def main():
    rclpy.init()
    node = GestureControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

## Practice Exercise

Build a gesture-controlled navigation system:
1. Implement pointing direction detection (8 directions: N, NE, E, SE, S, SW, W, NW)
2. Map gestures to navigation commands:
   - Point → Navigate in indicated direction
   - Open palm → Stop
   - Closed fist → Return to home position
3. Add gesture confirmation: Require 1-second hold before executing command
4. Implement safety checks: Stop robot if human enters proximity (use pose estimation)

## Next Steps

You've completed multimodal perception (voice, vision, gestures). In **Week 13: Capstone Project**, you'll integrate all components into an autonomous humanoid system with conversational AI, visual grounding, and adaptive task execution.
