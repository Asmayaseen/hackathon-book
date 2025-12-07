# ہفتہ 12: ملٹی موڈل وژن-زبان فیوژن

![Multimodal Vision-Language Fusion](/img/ai-13.png)

## وژن اور زبان کا انضمام

ملٹی موڈل ماڈلز ویژوئل اور ٹیکسٹ ڈیٹا کو مشترکہ طور پر پروسیس کرتے ہیں تاکہ زبان کو جسمانی ادراک میں جڑ سکے۔ روبوٹکس کے لئے، یہ اشیاء کو قدرتی تفصیلات ("لال ہینڈل والا مگ") کے ذریعے پہچاننے کی اجازت دیتا ہے بجائے از پہلے تیار کردہ ID یا باؤنڈنگ باکس کوآرڈینیٹس کے۔ وژن-زبان فیوژن ایمبیڈڈ AI ایجنٹس کے لئے ضروری ہے جو کھلی دنیا کے ماحول میں کام کرتے ہیں جہاں نئی، نامعلوم اشیاء ہوں۔

### ملٹی موڈل ماڈلز کیوں؟

**صفر-شاٹ اشیاء کی پہچان**: روایتی اشیاء کے ڈیٹیکٹرز کو لیبل شدہ ڈیٹا سیٹس پر تربیت کی ضرورت ہوتی ہے۔ ملٹی موڈل ماڈلز زبانی تفصیلات کو استعمال کرتے ہیں تاکہ بغیر دوبارہ تربیت کے نئی اقسام کو پہچان سکیں—ایک ہیومنوائڈ جو "کوئنوا" کو پہلی بار دیکھتا ہے وہ ٹیکسٹ-امیج کی مماثلت کے ذریعے اسے پہچان سکتا ہے۔

**سپیشل ریزننگ**: زبانی ماڈلز سپیشل ریلیشن شپس ("بائیں طرف"، "پیچھے") کو کوڈ کرتے ہیں لیکن ویژوئل جڑاؤ کا فقدان ہوتا ہے۔ وژن-زبان ماڈلز سیکھتے ہیں کہ ان لینگوئسٹک تصورات کو پکسل کوآرڈینیٹس میں میپ کریں۔

**وضاحت**: منظر میں متعدد مماثل اشیاء کے ساتھ ("بائیں طرف والا لال مگ")، ویژوئل جڑاؤ یہ حل کرتا ہے کہ کون سا واقعہ تفصیل سے مماثل ہے۔

## ویژوئل جڑاؤ کے لئے CLIP

**CLIP (کنٹراسٹو لینگویج-امیج پری ٹریننگ)** امیج اور ٹیکسٹ کے لئے ایک مشترکہ ایمبیڈنگ سپیس سیکھتا ہے 400 ملین امیج-کیپشن جوڑے پر تربیت کر کے جو انٹرنیٹ سے کھرچے گئے تھے۔ ایک امیج اور متعدد ٹیکسٹ تفصیلات دیے جانے پر، CLIP میل کھانے کے لئے مماثلت سکورز کا حساب لگاتا ہے۔

### انسٹالیشن اور بنیادی استعمال

```python
# OpenAI کی سرکاری ریپوزٹری سے CLIP انسٹال کریں
import subprocess
subprocess.run(["pip", "install", "git+https://github.com/openai/CLIP.git", "pillow", "torch"])

import torch
import clip
from PIL import Image
import numpy as np

# پری ٹرینڈ CLIP ماڈل لوڈ کریں
# اختیارات: RN50، RN101، ViT-B/32، ViT-L/14 (بڑا = زیادہ درست لیکن سست)
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def ground_object_in_image(image_path: str, text_queries: list) -> dict:
    """
    معلوم کریں کہ کون سی ٹیکسٹ تفصیل امیج سے بہترین مماثلت رکھتی ہے۔

    Args:
        image_path: امیج فائل کا راستہ
        text_queries: موازنہ کے لئے ٹیکسٹ تفصیلات کی فہرست
    Returns:
        dict: {
            'best_match': str,
            'scores': dict query کو مماثلت سکور میں میپ کرتا ہے
        }
    """
    # امیج لوڈ اور پری پروسیس کریں
    image = Image.open(image_path)
    image_input = preprocess(image).unsqueeze(0).to(device)

    # ٹیکسٹ کویریز ٹوکنائز کریں
    text_inputs = clip.tokenize(text_queries).to(device)

    # ایمبیڈنگز کا حساب لگائیں
    with torch.no_grad():
        image_features = model.encode_image(image_input)  # Shape: [1, 512]
        text_features = model.encode_text(text_inputs)    # Shape: [N, 512]

        # فیچرز کو یونٹ ویکٹرز میں نارملائز کریں
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        # کوسائنز مماثلت کا حساب لگائیں (یونٹ ویکٹرز کا ڈاٹ پروڈکٹ)
        similarity = (image_features @ text_features.T).squeeze(0)  # Shape: [N]

        # سافٹ میکس کا استعمال کرتے ہوئے امکانات میں تبدیل کریں
        probabilities = similarity.softmax(dim=0).cpu().numpy()

    # نتائج کا ڈکشنری تیار کریں
    scores = {query: float(prob) for query, prob in zip(text_queries, probabilities)}
    best_match = text_queries[probabilities.argmax()]

    return {
        'best_match': best_match,
        'scores': scores
    }

# مثال: کچن منظر میں اشیاء کی تصنیف
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

## اشیاء کے انتخاب کے لئے ریفرنگ ایکسپریشنز

**ریفرنگ ایکسپریشنز** اوصاف (رنگ، شکل)، سپیشل ریلیشنز (بائیں، پیچھے)، اور فنکشنل تفصیلات (پینے کے لئے) کا استعمال کرتے ہوئے اشیاء کی منفرد پہچان کرتے ہیں۔ سادہ اشیاء کے ڈیٹیکشن کے مقابلے، اس کو کمپوزیشنل ریزننگ کی ضرورت ہوتی ہے۔

### CLIP کے ساتھ سپیشل جڑاؤ

```python
import cv2
from typing import List, Tuple

def detect_objects_with_clip(
    image_path: str,
    object_descriptions: List[str],
    grid_size: int = 8
) -> List[Tuple[str, int, int, float]]:
    """
    سلائیڈنگ ونڈو CLIP اسکورنگ کا استعمال کرتے ہوئے امیج میں اشیاء کو لوکلائز کریں۔

    Args:
        image_path: ان پٹ امیج
        object_descriptions: تلاش کرنے کے لئے ٹیکسٹ تفصیلات کی فہرست
        grid_size: امیج کو grid_size x grid_size علاقوں میں تقسیم کریں
    Returns:
        (description, x, y, score) کی فہرست تیار کی گئی اشیاء کے لئے
    """
    # امیج لوڈ کریں
    image = Image.open(image_path)
    img_width, img_height = image.size

    # علاقہ کے ابعاد کا حساب لگائیں
    region_width = img_width // grid_size
    region_height = img_height // grid_size

    detections = []

    for desc in object_descriptions:
        best_score = 0
        best_position = (0, 0)

        # گرڈ علاقوں پر سلائیڈ کریں
        for i in range(grid_size):
            for j in range(grid_size):
                # علاقہ نکالیں
                left = j * region_width
                top = i * region_height
                right = left + region_width
                bottom = top + region_height

                region = image.crop((left, top, right, bottom))
                region_input = preprocess(region).unsqueeze(0).to(device)

                # اس علاقے کے لئے CLIP سکور کا حساب لگائیں
                text_input = clip.tokenize([desc]).to(device)

                with torch.no_grad():
                    image_features = model.encode_image(region_input)
                    text_features = model.encode_text(text_input)

                    image_features /= image_features.norm(dim=-1, keepdim=True)
                    text_features /= text_features.norm(dim=-1, keepdim=True)

                    score = (image_features @ text_features.T).item()

                # اس شے کے لئے سب سے زیادہ اسکور والے علاقے کو ٹریک کریں
                if score > best_score:
                    best_score = score
                    best_position = (left + region_width // 2, top + region_height // 2)

        detections.append((desc, best_position[0], best_position[1], best_score))

    return detections

# مثال: متعدد اشیاء کو لوکیٹ کریں
objects = ["red mug", "laptop computer", "potted plant"]
detections = detect_objects_with_clip("desk_scene.jpg", objects, grid_size=6)

for obj, x, y, score in detections:
    print(f"{obj}: position ({x}, {y}), confidence {score:.3f}")

# نتائج کو وژوئلائز کریں
image = cv2.imread("desk_scene.jpg")
for obj, x, y, score in detections:
    cv2.circle(image, (x, y), 10, (0, 255, 0), -1)
    cv2.putText(image, obj, (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

cv2.imwrite("detected_objects.jpg", image)
```

## ویژوئل کوئسچن اینسرنگ (VQA)

**ویژوئل کوئسچن اینسرنگ** امیج کی سمجھ کو زبانی تفہیم کے ساتھ جوڑتی ہے تاکہ ویژوئل مناظر کے بارے میں کھلے اختتام والے سوالات کے جوابات دیے جا سکیں۔ ہیومنوائڈ روبوٹس کے لئے، VQA سیچوئیشنل وارنیس کو فعال کرتا ہے: "کیا دروازہ کھلا ہے؟"، "کمرے میں کتنے لوگ ہیں؟"، "میز پر موجود شے کا رنگ کیا ہے؟"

### GPT-4V (وژن) کے ساتھ VQA

```python
import base64
import requests

def answer_visual_question(image_path: str, question: str) -> str:
    """
    GPT-4V کا استعمال کرتے ہوئے امیج کے بارے میں سوالات کے جوابات دیں۔

    Args:
        image_path: امیج فائل کا راستہ
        question: قدرتی زبان کا سوال
    Returns:
        str: GPT-4V سے جواب
    """
    # API ٹرانسمیشن کے لئے امیج کو بیس64 میں انکوڈ کریں
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }

    # ملٹی موڈل پرومپٹ تیار کریں
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

    # API درخواست بھیجیں
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    # جواب نکالیں
    result = response.json()
    answer = result['choices'][0]['message']['content']
    return answer

# مثال: منظر کی سمجھ کے لئے سوالات
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

## وژن-زبان کا روبوٹ کنٹرول کے ساتھ انضمام

CLIP جڑاؤ کو ROS 2 ایکشن سرورز کے ساتھ بند لوپ مینوپولیشن کے لئے جوڑیں:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point

class VisionLanguageGrasping(Node):
    """
    ROS 2 نوڈ جو CLIP کا استعمال کرتا ہے اشیاء کو تلاش کرنے اور روبوٹ کو گریسنگ کے لئے کمانڈ دینے کے لئے۔
    """

    def __init__(self):
        super().__init__('vision_language_grasping')

        # کیمرہ امیجز کے لئے سبسکرائب کریں
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # گریس ٹارگیٹ پوزیشنز کے لئے پبلشر
        self.grasp_pub = self.create_publisher(Point, '/grasp_target', 10)

        self.current_image = None

    def image_callback(self, msg):
        """تازہ ترین کیمرہ امیج اسٹور کریں۔"""
        # ROS امیج میسج کو PIL امیج میں تبدیل کریں
        self.current_image = self.ros_to_pil_image(msg)

    def grasp_object_by_description(self, description: str):
        """
        تفصیل سے مماثل شے تلاش کریں اور گریس ٹارگیٹ شائع کریں۔

        Args:
            description: ٹیکسٹ تفصیل (مثلاً "the blue screwdriver")
        """
        if self.current_image is None:
            self.get_logger().warn("No camera image available")
            return

        # شے تلاش کرنے کے لئے CLIP کا استعمال کریں
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

            # پکسل کوآرڈینیٹس کو 3D پوائنٹ میں تبدیل کریں (کیمرہ کیلیبریشن کی ضرورت ہے)
            grasp_point = self.pixel_to_3d(x, y)

            # مینوپولیشن کنٹرولر کے لئے گریس ٹارگیٹ شائع کریں
            self.grasp_pub.publish(grasp_point)

    def pixel_to_3d(self, x: int, y: int) -> Point:
        """
        2D پکسل کو 3D پوائنٹ میں تبدیل کریں ڈیپتھ سینسر اور کیمرہ انٹرنسکس کا استعمال کرتے ہوئے۔
        (سادہ؛ حقیقی امپلیمنٹیشن کو camera_info اور depth_image کی ضرورت ہے)
        """
        point = Point()
        point.x = float(x) * 0.001  # نمونہ تبدیلی
        point.y = float(y) * 0.001
        point.z = 0.5  # فکسڈ ڈیپتھ کا فرض کریں
        return point

# ROS 2 کے سیاق میں مثال کا استعمال
def main():
    rclpy.init()
    node = VisionLanguageGrasping()

    # روبوٹ کو شے گریسنگ کے لئے کمانڈ دیں
    node.grasp_object_by_description("the red coffee mug")

    rclpy.spin(node)
```

## مشق ورزش

ویژوئل سرچ سسٹم تیار کریں:
1. روبوٹ کے کیمرہ سے امیج کیپچر کریں
2. صارف ٹیکسٹ کویری فراہم کرتا ہے: "گرین بوتل تلاش کریں"
3. CLIP کا استعمال کرتے ہوئے شے تلاش کریں اور باؤنڈنگ باکس کا حساب لگائیں
4. روبوٹ کو شے کا سامنا کرنے کے لئے نیوی گیٹ کریں (کیمرہ پین یا بیس منتقل کریں)
5. تصدیق کریں کہ شے مینوپولیشن ورک سپیس میں ہے

**خصوصیت ریزننگ** کے ساتھ بڑھائیں: "دو مگوں میں سے بڑا" (سائز کا موازنہ کی ضرورت ہے) یا "کنارے کے قریب ترین مگ" (سپیشل ریزننگ) جیسے سوالات کو سنبھالیں۔

## اگلے اقدامات

آپ نے اشیاء کی جڑاؤ کے لئے زبان کو وژن سے جوڑ دیا ہے۔ **ہفتہ 12: گیسچر ریکوگنیشن** میں، آپ MediaPipe کا استعمال کرتے ہوئے انسانی پوز ٹریکنگ شامل کریں گے، روبوٹس کو اشاروں اور بدن کی زبان کی تشریح کرنے کی اجازت دیں گے قدرتی انسان-روبوٹ انٹرایکشن کے لئے۔