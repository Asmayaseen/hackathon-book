# ہفتہ 12: انسان-روبوٹ انٹرایکشن کے لئے گیسچر ریکوگنیشن

![Gesture Recognition](/img/ai-14.png)

## MediaPipe کے ساتھ ہینڈ گیسچر ڈیٹیکشن

**MediaPipe** گوگل کا اوپن سورس فریم ورک ہے ریل ٹائم ادراک پائپ لائنز کے لئے، ہینڈ ٹریکنگ، پوز ایسٹیمیشن، چہرہ ڈیٹیکشن، اور ہولسٹک بڑی ٹریکنگ کے لئے پری ٹرینڈ ماڈلز فراہم کرتا ہے۔ ہیومنوائڈ روبوٹکس کے لئے، ہینڈ گیسچر ریکوگنیشن غیر زبانی مواصلت کو فعال کرتا ہے—اشیاء کی طرف اشارہ کرنا، سٹاپ/جاؤ کے اشارے، یا مینوپولیشن ٹریجکٹریز کا مظاہرہ کرنا۔

### روبوٹکس کے لئے MediaPipe کیوں؟

**ریل ٹائم کارکردگی**: MediaPipe CPU پر 30+ FPS اور GPU پر 60+ FPS حاصل کرتا ہے، جواب دہ انسان-روبوٹ انٹرایکشن کے لئے مناسب بغیر خصوصی ہارڈ ویئر کے۔

**کراس پلیٹ فارم**: Linux، Windows، موبائل ڈیوائسز، اور ایمبیڈڈ سسٹمز (Raspberry Pi، Jetson Nano) پر چلتا ہے، مختلف روبوٹ پلیٹ فارمزم پر اتارنے کو فعال کرتا ہے۔

**پری ٹرینڈ ماڈلز**: MediaPipe کا ہینڈ ٹریکر ہر ہاتھ کے 21 3D لینڈ مارکس (انگلی کے سرے، کنکلز، کلائی) کی شناخت کرتا ہے بغیر کسٹم تربیت کے—کوئی ڈیٹا سیٹ اینوٹیشن کی ضرورت نہیں۔

**ملٹی ہینڈ سپورٹ**: ایک وقت میں متعدد ہاتھوں کو ڈیٹیکٹ اور ٹریک کرتا ہے، بائیں/دائیں ہاتھ کو الگ کرتا ہے اور فریمزم کے درمیان شناخت برقرار رکھتا ہے۔

### انسٹالیشن اور بنیادی ہینڈ ٹریکنگ

```python
# ویژوئلائزیشن کے لئے MediaPipe اور OpenCV انسٹال کریں
import subprocess
subprocess.run(["pip", "install", "mediapipe", "opencv-python", "numpy"])

import cv2
import mediapipe as mp
import numpy as np

# MediaPipe ہینڈ ٹریکنگ کا ابتدائی کریں
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def track_hands_in_video(video_source=0):
    """
    ویب کیمرہ یا ویڈیو فائل سے ریل ٹائم ہینڈ ٹریکنگ۔

    Args:
        video_source: کیمرہ انڈیکس (0 ڈیفالٹ ویب کیمرہ کے لئے) یا ویڈیو فائل کا راستہ
    """
    # ہینڈ ڈیٹیکٹر کنفیگر کریں
    # max_num_hands: ڈیٹیکٹ کرنے کے لئے زیادہ سے زیادہ ہاتھ (زیادہ تر روبوٹکس ٹاسکس کے لئے 1-2)
    # min_detection_confidence: ابتدائی ہینڈ ڈیٹیکشن کے لئے تھریش ہولڈ (0.0-1.0)
    # min_tracking_confidence: لینڈ مارک ٹریکنگ کے لئے تھریش ہولڈ (0.0-1.0)
    hands = mp_hands.Hands(
        static_image_mode=False,  # ویڈیو سٹریم کے لئے غلط (ٹریکنگ کو فعال کرتا ہے)
        max_num_hands=2,
        min_detection_confidence=0.7,  # زیادہ = کم جھوٹے مثبت
        min_tracking_confidence=0.5
    )

    cap = cv2.VideoCapture(video_source)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # BGR کو RGB میں تبدیل کریں (MediaPipe RGB کی توقع کرتا ہے)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # فریم کو ہینڈز ڈیٹیکٹ کرنے کے لئے پروسیس کریں
        results = hands.process(frame_rgb)

        # فریم پر ہینڈ لینڈ مارکس ڈرائیں
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 21 لینڈ مارکس اور کنکشنز ڈرائیں
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

        # تشریح شدہ فریم ڈسپلے کریں
        cv2.imshow('Hand Tracking', frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

# ہینڈ ٹریکر چلائیں
track_hands_in_video()
```

## گیسچر کمانڈ میپنگ

ہینڈ پوزز کو روبوٹ کمانڈز میں میپ کریں لینڈ مارک کنفیگریشن کا تجزیہ کر کے:

```python
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class HandGesture:
    """شناخت شدہ گیسچر کی نمائندگی کرتا ہے یقین کے اسکور کے ساتھ۔"""
    name: str
    confidence: float
    parameters: Dict  # اضافی معلومات (مثلاً اشارہ کی سمت)

class GestureRecognizer:
    """
    MediaPipe لینڈ مارکس سے ہینڈ گیسچر کلاسیفائی کریں۔
    گیسچر کو روبوٹ کمانڈز میں میپ کریں۔
    """

    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # کمانڈ گیسچر کے لئے ایک ہاتھ
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

    def recognize_gesture(self, frame: np.ndarray) -> Optional[HandGesture]:
        """
        امیج فریم میں گیسچر ڈیٹیکٹ اور کلاسیفائی کریں۔

        Args:
            frame: کیمرہ سے BGR امیج
        Returns:
            HandGesture آبجیکٹ یا None اگر کوئی گیسچر ڈیٹیکٹ نہ ہو
        """
        # فریم کو پروسیس کریں
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if not results.multi_hand_landmarks:
            return None

        # پہلا ڈیٹیکٹ کردہ ہاتھ کا تجزیہ کریں
        landmarks = results.multi_hand_landmarks[0]

        # لینڈ مارکس کو numpy ارے میں تبدیل کریں آسان کمپیوٹیشن کے لئے
        # ہر لینڈ مارک کے پاس x، y، z کوآرڈینیٹس ہیں ([0، 1] میں نارملائز)
        points = np.array([
            [lm.x, lm.y, lm.z]
            for lm in landmarks.landmark
        ])

        # لینڈ مارک کنفیگریشن کے مطابق گیسچر کلاسیفائی کریں
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
        تھممز اپ گیسچر ڈیٹیکٹ کریں۔
        معیار: تھمب ٹپ MCP جوائنٹ کے اوپر، دیگر انگلیاں مڑی ہوئیں۔
        """
        # لینڈ مارک انڈیکس (MediaPipe ہینڈ لینڈ مارک ڈائیگرام دیکھیں)
        thumb_tip = points[4]
        thumb_mcp = points[2]
        index_tip = points[8]
        index_pip = points[6]

        # تھمب اوپر کی طرف بڑھا ہوا
        thumb_extended = thumb_tip[1] < thumb_mcp[1]  # y اوپر کی طرف کم ہوتا ہے
        # دیگر انگلیاں مڑی ہوئیں (ٹپ PIP جوائنٹ کے نیچے)
        fingers_curled = all([
            points[8][1] > points[6][1],   # انڈیکس
            points[12][1] > points[10][1],  # مڈل
            points[16][1] > points[14][1],  # رنگ
            points[20][1] > points[18][1]   # پنکی
        ])

        return thumb_extended and fingers_curled

    def _is_pointing(self, points: np.ndarray) -> bool:
        """
        اشارہ کرنے کا گیسچر ڈیٹیکٹ کریں۔
        معیار: انڈیکس فنگر بڑھا ہوا، دیگر انگلیاں مڑی ہوئیں۔
        """
        # انڈیکس فنگر بڑھا ہوا
        index_extended = points[8][1] < points[6][1]  # ٹپ PIP کے اوپر

        # دیگر انگلیاں مڑی ہوئیں
        other_curled = all([
            points[12][1] > points[10][1],  # مڈل
            points[16][1] > points[14][1],  # رنگ
            points[20][1] > points[18][1]   # پنکی
        ])

        return index_extended and other_curled

    def _is_open_palm(self, points: np.ndarray) -> bool:
        """
        کھلا ہاتھ ڈیٹیکٹ کریں (سٹاپ سگنل)۔
        معیار: سبھی انگلیاں بڑھی ہوئیں اور پھیلی ہوئیں۔
        """
        # سبھی فنگر ٹپ ان کے مطابق MCP جوائنٹس کے اوپر
        fingers_extended = all([
            points[4][1] < points[2][1],    # تھمب
            points[8][1] < points[5][1],    # انڈیکس
            points[12][1] < points[9][1],   # مڈل
            points[16][1] < points[13][1],  # رنگ
            points[20][1] < points[17][1]   # پنکی
        ])

        return fingers_extended

    def _is_closed_fist(self, points: np.ndarray) -> bool:
        """
        بند مٹھی ڈیٹیکٹ کریں (گریب کمانڈ)۔
        معیار: سبھی انگلیاں MCP جوائنٹس کے نیچے مڑی ہوئیں۔
        """
        all_curled = all([
            points[8][1] > points[5][1],    # انڈیکس
            points[12][1] > points[9][1],   # مڈل
            points[16][1] > points[13][1],  # رنگ
            points[20][1] > points[17][1]   # پنکی
        ])

        return all_curled

    def _is_peace_sign(self, points: np.ndarray) -> bool:
        """
        پیس سائن ڈیٹیکٹ کریں (انڈیکس + مڈل بڑھا ہوا)۔
        """
        index_extended = points[8][1] < points[6][1]
        middle_extended = points[12][1] < points[10][1]
        ring_curled = points[16][1] > points[14][1]
        pinky_curled = points[20][1] > points[18][1]

        return index_extended and middle_extended and ring_curled and pinky_curled

    def _get_pointing_direction(self, points: np.ndarray) -> str:
        """
        انڈیکس فنگر کے اورینٹیشن سے اشارہ کی سمت کا حساب لگائیں۔

        Returns:
            سمت سٹرنگ: "left"، "right"، "up"، "down"، "forward"
        """
        # انڈیکس MCP سے ٹپ تک ویکٹر
        mcp = points[5]
        tip = points[8]
        vector = tip - mcp

        # بنیادی جزو کا تجزیہ
        if abs(vector[0]) > abs(vector[1]):
            return "right" if vector[0] > 0 else "left"
        else:
            return "down" if vector[1] > 0 else "up"

# مثال: ریل ٹائم گیسچر ریکوگنیشن
recognizer = GestureRecognizer()
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    gesture = recognizer.recognize_gesture(frame)

    if gesture and gesture.confidence > 0.8:
        # شناخت شدہ گیسچر ڈسپلے کریں
        text = f"{gesture.name} ({gesture.confidence:.2f})"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)

        # گیسچر کے مطابق روبوٹ کمانڈ انجام دیں
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

## انسان-روبوٹ انٹرایکشن کے لئے پوز ایسٹیمیشن

**پوز ایسٹیمیشن** فل بڑی لینڈ مارکس (33 پوائنٹس بشمول کندھے، کہنیاں، کمر، گھٹنے) کو ٹریک کرتا ہے تاکہ انسانی سرگرمی اور سپیشل پوزیشننگ کو سمجھا جا سکے۔ تعاونی روبوٹکس کے لئے، یہ فعال کرتا ہے:

- **قیاسی ڈیٹیکشن**: روبوٹ بازو کو روکیں اگر انسان ورک سپیس میں داخل ہو جائے
- **سرگرمی کی پہچان**: کھڑے، بیٹھے، چلتے کے درمیان فرق کریں سیاقی وارنیس کے برتاؤ کے لئے
- **گیسچر ڈیموسٹریشن**: انسانی بازو کی حرکات کی نقل کر کے مینوپولیشن ٹاسکس سیکھیں

### فل بڑی پوز ٹریکنگ

```python
mp_pose = mp.solutions.pose

def track_human_pose(video_source=0):
    """
    سیفٹی مانیٹرنگ اور نقل سیکھنے کے لئے انسانی بڑی کا پوز ٹریک کریں۔

    Args:
        video_source: کیمرہ انڈیکس یا ویڈیو فائل
    """
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,  # 0=لائٹ، 1=مکمل، 2=بھاری (زیادہ = زیادہ درست)
        smooth_landmarks=True,  # ویڈیو کے لئے ٹیمپورل سموتھنگ
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
            # پوز سکلیٹن ڈرائیں
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )

            # تجزیہ کے لئے کلیدی جوائنٹ پوزیشنز نکالیں
            landmarks = results.pose_landmarks.landmark
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

            # مثال: چیک کریں کہ کیا ہاتھ اٹھائے ہوئے ہیں (y < 0.5)
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

# پوز ٹریکر چلائیں
track_human_pose()
```

## گیسچر کا ROS 2 کے ساتھ انضمام

گیسچر ریکوگنیشن کو روبوٹ کنٹرول سے جوڑیں:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class GestureControlNode(Node):
    """
    ROS 2 نوڈ جو ہینڈ گیسچر کے مطابق روبوٹ کمانڈز شائع کرتا ہے۔
    """

    def __init__(self):
        super().__init__('gesture_control')

        # گیسچر بیسڈ کمانڈز کے لئے پبلشر
        self.cmd_pub = self.create_publisher(String, '/gesture_commands', 10)

        # مسلسل گیسچر ریکوگنیشن کے لئے ٹائمر
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10 Hz

        self.recognizer = GestureRecognizer()
        self.cap = cv2.VideoCapture(0)

        self.last_gesture = None
        self.gesture_stable_count = 0
        self.STABILITY_THRESHOLD = 5  # تصدیق کے لئے 5 مسلسل فریم کی ضرورت ہے

    def timer_callback(self):
        """کیمرہ فریم پروسیس کریں اور گیسچر کمانڈز شائع کریں۔"""
        success, frame = self.cap.read()
        if not success:
            return

        gesture = self.recognizer.recognize_gesture(frame)

        if gesture and gesture.confidence > 0.85:
            # جھوٹے ٹرگر سے بچنے کے لئے گیسچر کی استحکام کی ضرورت ہے
            if gesture.name == self.last_gesture:
                self.gesture_stable_count += 1
            else:
                self.gesture_stable_count = 0
                self.last_gesture = gesture.name

            # گیسچر مستحکم ہونے پر کمانڈ شائع کریں
            if self.gesture_stable_count >= self.STABILITY_THRESHOLD:
                msg = String()
                msg.data = f"{gesture.name}:{gesture.parameters}"
                self.cmd_pub.publish(msg)

                self.get_logger().info(f"Published gesture command: {gesture.name}")

                # دوہرائی کمانڈز سے بچنے کے لئے ری سیٹ کریں
                self.gesture_stable_count = 0

def main():
    rclpy.init()
    node = GestureControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

## مشق ورزش

گیسچر کنٹرولڈ نیوی گیشن سسٹم تیار کریں:
1. اشارہ کرنے کی سمت ڈیٹیکشن لاگو کریں (8 سمتیں: N، NE، E، SE، S، SW، W، NW)
2. گیسچر کو نیوی گیشن کمانڈز میں میپ کریں:
   - اشارہ → متعین سمت میں نیوی گیٹ کریں
   - کھلا ہاتھ → روکیں
   - بند مٹھی → ہوم پوزیشن پر واپس جائیں
3. گیسچر کی تصدیق شامل کریں: کمانڈ انجام دینے سے پہلے 1 سیکنڈ کا ہولڈ درکار ہے
4. سیفٹی چیکس لاگو کریں: اگر انسان قیاسی حد میں داخل ہو جائے تو روبوٹ کو روکیں (پوز ایسٹیمیشن استعمال کریں)

## اگلے اقدامات

آپ نے ملٹی موڈل ادراک مکمل کر لیا ہے (آواز، ویژن، گیسچر). **ہفتہ 13: کیپسٹون پروجیکٹ** میں، آپ تمام اجزاء کو ایک خودکار ہیومنوائڈ سسٹم میں ضم کریں گے جس میں گفتگو کا AI، ویژوئل جڑاؤ، اور موافق ٹاسک انجام دہی شامل ہو گی۔