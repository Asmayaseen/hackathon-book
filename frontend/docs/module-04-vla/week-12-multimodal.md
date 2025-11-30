# Week 12: Multimodal Vision-Language Fusion

![Multimodal Vision-Language Fusion](/img/ai-13.png)

## Vision and Language Integration

Multimodal models jointly process visual and textual data to ground language in physical perception. For robotics, this enables referring to objects by natural descriptions ("the mug with the red handle") rather than pre-defined IDs or bounding box coordinates. Vision-language fusion is essential for embodied AI agents operating in open-world environments with novel, unnamed objects.

### Why Multimodal Models?

**Zero-Shot Object Recognition**: Traditional object detectors require training on labeled datasets. Multimodal models leverage language descriptions to recognize new categories without retraining—a humanoid encountering "quinoa" for the first time can identify it via text-image similarity.

**Spatial Reasoning**: Language models encode spatial relationships ("left of", "behind") but lack visual grounding. Vision-language models learn to map these linguistic concepts to pixel coordinates.

**Disambiguation**: In scenes with multiple similar objects ("the red mug on the left"), visual grounding resolves which instance matches the description.

## CLIP for Visual Grounding

**CLIP (Contrastive Language-Image Pre-training)** learns a shared embedding space for images and text by training on 400 million image-caption pairs scraped from the internet. Given an image and multiple text descriptions, CLIP computes similarity scores to determine the best match.

### Installation and Basic Usage

```python
# Install CLIP from OpenAI's official repository
import subprocess
subprocess.run(["pip", "install", "git+https://github.com/openai/CLIP.git", "pillow", "torch"])

import torch
import clip
from PIL import Image
import numpy as np

# Load pre-trained CLIP model
# Options: RN50, RN101, ViT-B/32, ViT-L/14 (larger = more accurate but slower)
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def ground_object_in_image(image_path: str, text_queries: list) -> dict:
    """
    Find which text description best matches the image.

    Args:
        image_path: Path to image file
        text_queries: List of text descriptions to compare

    Returns:
        dict: {
            'best_match': str,
            'scores': dict mapping query to similarity score
        }
    """
    # Load and preprocess image
    image = Image.open(image_path)
    image_input = preprocess(image).unsqueeze(0).to(device)

    # Tokenize text queries
    text_inputs = clip.tokenize(text_queries).to(device)

    # Compute embeddings
    with torch.no_grad():
        image_features = model.encode_image(image_input)  # Shape: [1, 512]
        text_features = model.encode_text(text_inputs)    # Shape: [N, 512]

        # Normalize features to unit vectors
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        # Compute cosine similarity (dot product of unit vectors)
        similarity = (image_features @ text_features.T).squeeze(0)  # Shape: [N]

        # Convert to probabilities using softmax
        probabilities = similarity.softmax(dim=0).cpu().numpy()

    # Create results dictionary
    scores = {query: float(prob) for query, prob in zip(text_queries, probabilities)}
    best_match = text_queries[probabilities.argmax()]

    return {
        'best_match': best_match,
        'scores': scores
    }

# Example: Object classification in kitchen scene
queries = [
    "a red coffee mug",
    "a white plate",
    "a stainless steel fork",
    "a glass of water"
]

result = ground_object_in_image("kitchen_counter.jpg", queries)
print(f"Best match: {result['best_match']}")
print("\nAll scores:")
for query, score in result['scores'].items():
    print(f"  {query}: {score:.3f}")

# Output:
# Best match: a red coffee mug
# All scores:
#   a red coffee mug: 0.782
#   a white plate: 0.124
#   a stainless steel fork: 0.061
#   a glass of water: 0.033
```

## Referring Expressions for Object Selection

**Referring expressions** uniquely identify objects using attributes (color, shape), spatial relations (left, behind), and functional descriptions (for drinking). Unlike simple object detection, this requires compositional reasoning.

### Spatial Grounding with CLIP

```python
import cv2
from typing import List, Tuple

def detect_objects_with_clip(
    image_path: str,
    object_descriptions: List[str],
    grid_size: int = 8
) -> List[Tuple[str, int, int, float]]:
    """
    Localize objects in image using sliding window CLIP scoring.

    Args:
        image_path: Input image
        object_descriptions: List of text descriptions to search for
        grid_size: Divide image into grid_size x grid_size regions

    Returns:
        List of (description, x, y, score) for detected objects
    """
    # Load image
    image = Image.open(image_path)
    img_width, img_height = image.size

    # Calculate region dimensions
    region_width = img_width // grid_size
    region_height = img_height // grid_size

    detections = []

    for desc in object_descriptions:
        best_score = 0
        best_position = (0, 0)

        # Slide over grid regions
        for i in range(grid_size):
            for j in range(grid_size):
                # Extract region
                left = j * region_width
                top = i * region_height
                right = left + region_width
                bottom = top + region_height

                region = image.crop((left, top, right, bottom))
                region_input = preprocess(region).unsqueeze(0).to(device)

                # Compute CLIP score for this region
                text_input = clip.tokenize([desc]).to(device)

                with torch.no_grad():
                    image_features = model.encode_image(region_input)
                    text_features = model.encode_text(text_input)

                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    text_features /= text_features.norm(dim=-1, keepdim=True)

                    score = (image_features @ text_features.T).item()

                # Track highest scoring region for this object
                if score > best_score:
                    best_score = score
                    best_position = (left + region_width // 2, top + region_height // 2)

        detections.append((desc, best_position[0], best_position[1], best_score))

    return detections

# Example: Locate multiple objects
objects = ["red mug", "laptop computer", "potted plant"]
detections = detect_objects_with_clip("desk_scene.jpg", objects, grid_size=6)

for obj, x, y, score in detections:
    print(f"{obj}: position ({x}, {y}), confidence {score:.3f}")

# Visualize results
image = cv2.imread("desk_scene.jpg")
for obj, x, y, score in detections:
    cv2.circle(image, (x, y), 10, (0, 255, 0), -1)
    cv2.putText(image, obj, (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

cv2.imwrite("detected_objects.jpg", image)
```

## Visual Question Answering (VQA)

**Visual Question Answering** combines image understanding with language comprehension to answer open-ended questions about visual scenes. For humanoid robots, VQA enables situational awareness: "Is the door open?", "How many people are in the room?", "What color is the object on the table?"

### VQA with GPT-4V (Vision)

```python
import base64
import requests

def answer_visual_question(image_path: str, question: str) -> str:
    """
    Use GPT-4V to answer questions about an image.

    Args:
        image_path: Path to image file
        question: Natural language question

    Returns:
        str: Answer from GPT-4V
    """
    # Encode image to base64 for API transmission
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }

    # Construct multimodal prompt
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    # Send API request
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    # Extract answer
    result = response.json()
    answer = result['choices'][0]['message']['content']
    return answer

# Example: Scene understanding queries
questions = [
    "How many mugs are on the table?",
    "What color is the leftmost mug?",
    "Is there a laptop visible in the image?",
    "Describe the spatial arrangement of objects on the desk."
]

for q in questions:
    answer = answer_visual_question("desk_scene.jpg", q)
    print(f"Q: {q}")
    print(f"A: {answer}\n")

# Output:
# Q: How many mugs are on the table?
# A: There are three mugs visible on the table.
#
# Q: What color is the leftmost mug?
# A: The leftmost mug is red with a white handle.
```

## Integrating Vision-Language with Robot Control

Combine CLIP grounding with ROS 2 action servers for closed-loop manipulation:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point

class VisionLanguageGrasping(Node):
    """
    ROS 2 node that uses CLIP to locate objects and commands robot to grasp.
    """

    def __init__(self):
        super().__init__('vision_language_grasping')

        # Subscribe to camera images
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publisher for grasp target positions
        self.grasp_pub = self.create_publisher(Point, '/grasp_target', 10)

        self.current_image = None

    def image_callback(self, msg):
        """Store latest camera image."""
        # Convert ROS Image message to PIL Image
        self.current_image = self.ros_to_pil_image(msg)

    def grasp_object_by_description(self, description: str):
        """
        Find object matching description and publish grasp target.

        Args:
            description: Text description (e.g., "the blue screwdriver")
        """
        if self.current_image is None:
            self.get_logger().warn("No camera image available")
            return

        # Use CLIP to locate object
        detections = detect_objects_with_clip(
            self.current_image,
            [description],
            grid_size=8
        )

        if detections:
            desc, x, y, score = detections[0]
            self.get_logger().info(
                f"Found '{desc}' at pixel ({x}, {y}) with confidence {score:.2f}"
            )

            # Convert pixel coordinates to 3D point (requires camera calibration)
            grasp_point = self.pixel_to_3d(x, y)

            # Publish grasp target for manipulation controller
            self.grasp_pub.publish(grasp_point)

    def pixel_to_3d(self, x: int, y: int) -> Point:
        """
        Convert 2D pixel to 3D point using depth sensor and camera intrinsics.
        (Simplified; real implementation requires camera_info and depth_image)
        """
        point = Point()
        point.x = float(x) * 0.001  # Mock conversion
        point.y = float(y) * 0.001
        point.z = 0.5  # Assume fixed depth
        return point

# Example usage in ROS 2 context
def main():
    rclpy.init()
    node = VisionLanguageGrasping()

    # Command robot to grasp object
    node.grasp_object_by_description("the red coffee mug")

    rclpy.spin(node)
```

## Practice Exercise

Build a visual search system:
1. Capture image from robot's camera
2. User provides text query: "Find the green bottle"
3. Use CLIP to locate object and compute bounding box
4. Navigate robot to face object (pan camera or move base)
5. Verify object is within manipulation workspace

Extend with **attribute reasoning**: Handle queries like "the larger of the two mugs" (requires size comparison) or "the mug closest to the edge" (spatial reasoning).

## Next Steps

You've connected language to vision for object grounding. In **Week 12: Gesture Recognition**, you'll add human pose tracking using MediaPipe, enabling robots to interpret pointing gestures and body language for natural human-robot interaction.
