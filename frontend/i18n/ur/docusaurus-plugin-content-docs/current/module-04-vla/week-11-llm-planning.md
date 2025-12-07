# ہفتہ 11: LLM بیسڈ ٹاسک منصوبہ بندی

## روبوٹ ٹاسک منصوبہ بندی کے لئے GPT-4 کا استعمال

بڑے زبان کے ماڈلز انٹرنیٹ سکیل ٹیکسٹ ڈیٹا سے سیکھی گئی کامنز اسنس ریزننگ کو استعمال کرتے ہوئے اعلیٰ سطح کے اہداف کو انجام دہی کے قابل ذیلی ٹاسکس میں تقسیم کرنے میں ماہر ہیں۔ روبوٹکس کے لئے، اس کا مطلب غیر واضح ہدایات جیسے "ناشتہ تیار کریں" کو مخصوص ایکشن سیکوئنس میں تبدیل کرنا ہے: کچن کی طرف جائیں، فریج کھولیں، انڈے نکالیں، فریج بند کریں، اسٹو کی طرف جائیں، وغیرہ۔

### منصوبہ بندی کے لئے LLMs کیوں؟

**جنرلائزیشن**: روایتی پلینرز (PDDL، ہائیرارچیکل ٹاسک نیٹ ورکس) کو دستی طور پر لکھے گئے ڈومین ماڈلز کی ضرورت ہوتی ہے۔ LLMs مختلف ٹیکسٹ—ریسیپس، ہدایاتی مینولز، کیسے کریں گائیڈز—سے ٹاسک کی سٹرکچر کو ضمنی طور پر سیکھ لیتے ہیں، نئے ٹاسکس کے لئے صفر-شاٹ منصوبہ بندی کو فعال کرتے ہیں۔

**سیاقی ریزننگ**: LLMs ضمنی پابندیوں کا اندازہ لگاتے ہیں۔ "کافی بنائیں" دیے جانے پر، وہ جان لیتے ہیں کہ کافی بنانے کی کوشش سے پہلے پانی دستیاب ہے یا نہیں، کوڈ میں صریح شرائط کے بغیر۔

**قدرتی زبان کا انٹرفیس**: صارف فارمیل سپیسیفکیشنز کے بجائے فری فارم زبان میں اہداف فراہم کرتے ہیں۔ "میز کو کھانے کے لئے تیار کرنے میں مدد کریں" `set_table(num_plates=4, silverware=True)` سے زیادہ محسوس ہوتا ہے۔

**ناکامی سے بازیافت**: جب منصوبے ناکام ہوتے ہیں، LLMs ناکامی کی وضاحت کے مطابق دوبارہ منصوبہ بندی کرتے ہیں، کلاسیکل پلینرز میں نایاب موافق برتاؤ کا مظاہرہ کرتے ہیں۔

### بنیادی ٹاسک ڈیکوم پوزیشن

```python
import openai
import os
from typing import List, Dict

openai.api_key = os.getenv("OPENAI_API_KEY")

def plan_task(goal: str, context: str = "") -> List[str]:
    """
    روبوٹ کا ہدف حاصل کرنے کے لئے قدم بہ قدم منصوبہ تیار کریں۔

    Args:
        goal: اعلیٰ سطح کا ہدف (مثلاً "لیونگ روم صاف کریں")
        context: ماحولیاتی حالت (مثلاً "ویکیوم کپڑے میں ہے، کچرا بین بھرا ہوا ہے")
    Returns:
        انجام دہی کی ترتیب میں ایکشن اسٹیپس کی فہرست
    """
    # سسٹم پرومپٹ روبوٹ کی ایکشن سپیس اور پابندیوں کی وضاحت کرتا ہے
    system_prompt = """آپ ہیومنوائڈ روبوٹ کے لئے ٹاسک پلینر ہیں۔
    صارف کے اہداف کو دستیاب ایکشنز کا استعمال کرتے ہوئے ترتیب وار اسٹیپس میں تقسیم کریں۔

    دستیاب ایکشنز:
    - navigate(location): مخصوص جگہ پر جائیں
    - pick(object): روبوٹ کے سامنے کا شے اٹھائیں
    - place(object, location): پکڑی ہوئی شے کو جگہ پر رکھیں
    - open(object): دروازہ/دروازہ/برتن کھولیں
    - close(object): دروازہ/دروازہ/برتن بند کریں
    - activate(device): ایپلائنس/سوئچ چالو کریں
    - deactivate(device): ایپلائنس/سوئچ بند کریں

    پابندیاں:
    - روبوٹ ایک وقت میں ایک شے ہی پکڑ سکتا ہے (نئی شے اٹھانے سے پہلے رکھ دیں)
    - نیوی گیشن کو صاف راستے کی ضرورت ہوتی ہے (بند دروازے کے ذریعے نہیں چل سکتا)
    - شے کو رسائی میں ہونا چاہیے (نہ دکھائی دینے پر پہلے جائیں)

    اسٹیپس کی نمبر شدہ فہرست دیں۔ مختصر رہیں۔
    """

    # منصوبہ کو مطلع کرنے کے لئے ماحولیاتی سیاق و سباق شامل کریں
    user_prompt = f"""Goal: {goal}

    Current environment: {context if context else "Unknown state"}

    Generate action plan:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,  # مسلسل منصوبہ بندی کے لئے کم درجہ حرارت
        max_tokens=300
    )

    # نمبر شدہ فہرست کو اسٹیپس میں پارس کریں
    plan_text = response.choices[0].message.content
    steps = [
        line.strip()
        for line in plan_text.split('\n')
        if line.strip() and line.strip()[0].isdigit()
    ]
    return steps

# مثال: ہوم اسسٹنس ٹاسک
goal = "Prepare a cup of coffee"
context = "You are in the living room. Coffee maker is in the kitchen."

plan = plan_task(goal, context)
for i, step in enumerate(plan, 1):
    print(f"{i}. {step}")

# Output:
# 1. navigate(kitchen)
# 2. open(cabinet) to access coffee grounds
# 3. pick(coffee_grounds)
# 4. place(coffee_grounds, coffee_maker)
# 5. close(cabinet)
# 6. activate(coffee_maker)
# 7. pick(mug)
# 8. place(mug, coffee_maker)
```

## ReAct پیٹرن: ریزننگ + ایکٹنگ

**ReAct** (Reasoning and Acting) پیٹرن تھوڑا سا تیار کرنا اور ایکشن انجام دینا کو متبادل کرتا ہے، LLMs کو حقیقی وقت کی فیڈ بیک کے مطابق منصوبوں کو موافق طور پر ایڈجسٹ کرنے کی اجازت دیتا ہے۔ اوپن لوپ منصوبہ بندی (پورا منصوبہ ابھی تیار کرنا) کے مقابلے، ReAct ہر قدم پر بند لوپ ریزننگ کرتا ہے۔

### ReAct آرکیٹیکچر

```
Observation → Thought → Action → Observation → Thought → Action → ...
```

**Observation**: سینسرز سے موجودہ دنیا کی حالت (اشیاء کی پوزیشنز، دروازے کی حالت، بیٹری کی سطح)
**Thought**: اگلے کیا کرنا ہے اس کے بارے میں LLM تیار کردہ ریزننگ
**Action**: انجام دہی کے قابل روبوٹ کمانڈ
**Loop**: ہدف حاصل ہونے تک یا ناکامی کا پتہ چلنے تک دہرائیں

### امپلیمنٹیشن

```python
import json
from typing import Tuple, Optional

class ReActAgent:
    """
    موافق روبوٹ ٹاسک انجام دہی کے لئے ReAct ایجنٹ۔
    LLM ریزننگ کو ماحولیاتی فیڈ بیک کے ساتھ جوڑتا ہے۔
    """

    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.history = []  # (thought, action, observation) ٹوپلز ٹریک کریں

    def run(self, goal: str, get_observation_fn) -> bool:
        """
        ReAct لوپ کا استعمال کرتے ہوئے ہدف انجام دیں۔

        Args:
            goal: ٹاسک کا ہدف
            get_observation_fn: کال ایبل موجودہ دنیا کی حالت واپس کرتا ہے
        Returns:
            bool: صحیح اگر ہدف حاصل ہو گیا، غلط اگر ناکام ہو گیا
        """
        observation = get_observation_fn()
        self.history = []

        for step in range(self.max_steps):
            # LLM سے تھوڑا اور ایکشن تیار کریں
            thought, action = self._reason(goal, observation)
            self.history.append((thought, action, observation))

            print(f"\n--- Step {step + 1} ---")
            print(f"Observation: {observation}")
            print(f"Thought: {thought}")
            print(f"Action: {action}")

            # ٹاسک مکمل ہونے یا ناکامی کی جانچ کریں
            if action == "DONE":
                print("Goal achieved!")
                return True
            if action == "FAIL":
                print(f"Task failed: {thought}")
                return False

            # ایکشن انجام دیں اور نئی ملاحظہ حاصل کریں
            observation = self._execute_action(action, get_observation_fn)

        print("Max steps reached without completion.")
        return False

    def _reason(self, goal: str, observation: str) -> Tuple[str, str]:
        """
        ریزننگ اور اگلا ایکشن تیار کریں۔

        Returns:
            (thought, action): ریزننگ سٹرنگ اور ایکشن کمانڈ
        """
        # سیاق کے لئے مکمل تاریخ کے ساتھ پرومپٹ بنائیں
        history_text = "\n".join([
            f"Thought: {t}\nAction: {a}\nObservation: {o}"
            for t, a, o in self.history
        ])

        prompt = f"""You are controlling a humanoid robot. Use step-by-step reasoning.

Goal: {goal}

Previous steps:
{history_text if history_text else "None (this is the first step)"}

Current observation: {observation}

Think about what to do next. Format your response as:
Thought: [your reasoning]
Action: [command]

Use 'DONE' action when goal is achieved, 'FAIL' if impossible.
Available actions: navigate(loc), pick(obj), place(obj, loc), open(obj), close(obj), check(obj).
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=150
        )

        # جواب سے تھوڑا اور ایکشن پارس کریں
        text = response.choices[0].message.content
        lines = text.strip().split('\n')

        thought = ""
        action = ""
        for line in lines:
            if line.startswith("Thought:"):
                thought = line.replace("Thought:", "").strip()
            elif line.startswith("Action:"):
                action = line.replace("Action:", "").strip()

        return thought, action

    def _execute_action(self, action: str, get_observation_fn) -> str:
        """
        ایکشن کمانڈ انجام دیں (نمونہ امپلیمنٹیشن).
        حقیقی سسٹم میں، یہ ROS 2 ایکشن سرورز کو کال کرتا ہے۔
        """
        # ایکشن انجام دینا سیمولیٹ کریں (اصل روبوٹ انٹرفیس کے ساتھ تبدیل کریں)
        print(f"Executing: {action}")

        # ایکشن کے بعد اپ ڈیٹ کردہ ملاحظہ واپس کریں
        # پیداوار میں: سینسرز/ادراک سسٹم کو کویری کریں
        return get_observation_fn()

# نمونہ استعمال مOCK ماحول کے ساتھ
def mock_get_observation():
    """
    نمونہ سینسر ریڈنگ (اصل ادراک سسٹم کے ساتھ تبدیل کریں).
    حقیقی سسٹم میں: اشیاء کا ڈیٹیکٹر، SLAM میپ، جوائنٹ اسٹیٹس کو کویری کریں۔
    """
    # ایجنٹ کے ایکشنز کے مطابق تبدیل ہوتی ملاحظات سیمولیٹ کریں
    observations = [
        "You are in living room. Coffee maker visible in kitchen.",
        "You are in kitchen. Coffee maker is on counter. Mug is in cabinet.",
        "Cabinet is open. Mug is visible.",
        "You are holding mug. Coffee maker has finished brewing.",
        "Mug is placed under coffee maker spout."
    ]
    # ملاحظات کے ذریعے چکر (سادہ؛ حقیقی سسٹم سینسرز کو کویری کرتا ہے)
    return observations[len(agent.history) % len(observations)]

# ReAct ایجنٹ چلائیں
agent = ReActAgent(max_steps=8)
success = agent.run(
    goal="Serve a cup of coffee",
    get_observation_fn=mock_get_observation
)
```

## روبوٹس کے لئے چین آف تھوٹ

**چین آف تھوٹ (CoT)** پرومنگ انٹرمیڈیٹ ریزننگ اسٹیپس کو نکالتا ہے، LLM کارکردگی کو پیچیدہ ٹاسکس پر بہتر بناتا ہے۔ روبوٹکس کے لئے، CoT سپیسیو ٹیمپورل ریزننگ کو ڈیکوم پوز کرنے میں مدد دیتا ہے:

### مینوپولیشن منصوبہ بندی کے لئے CoT

```python
def plan_grasp_with_cot(object_name: str, scene_description: str) -> Dict:
    """
    چین آف تھوٹ ریزننگ کا استعمال کرتے ہوئے گریس منصوبہ تیار کریں۔

    Args:
        object_name: گریسنگ کے لئے ہدف کی شے
        scene_description: ویژوئل منظر کا لے آؤٹ
    Returns:
        dict: گریس سٹریٹجی ایپروچ ویکٹر، رابطے کے پوائنٹس کے ساتھ
    """
    prompt = f"""You are planning a grasp for a humanoid robot arm.

Object: {object_name}
Scene: {scene_description}

Think step-by-step:
1. What is the object's shape and likely material?
2. What grasp type is appropriate (pinch, power, lateral)?
3. From which direction should the robot approach?
4. What are potential failure modes (slipping, collision)?

Then output JSON grasp plan:
{{
    "grasp_type": "pinch | power | lateral",
    "approach_direction": "top | side | front",
    "contact_points": ["finger1_location", "finger2_location"],
    "expected_force": "low | medium | high"
}}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    # جواب سے JSON نکالیں
    text = response.choices[0].message.content
    # جواب میں JSON بلاک تلاش کریں
    start = text.find('{')
    end = text.rfind('}') + 1
    if start != -1 and end > start:
        grasp_plan = json.loads(text[start:end])
        return grasp_plan

    return {"error": "Failed to generate grasp plan"}

# مثال: گریس منصوبہ بندی
result = plan_grasp_with_cot(
    object_name="wine glass",
    scene_description="Wine glass on table, stem visible, surrounded by plates"
)
print(json.dumps(result, indent=2))
```

## پرومنٹ انجینئرنگ بہترین طریقے

**سسٹم کا کردار**: روبوٹ کی صلاحیتوں اور پابندیوں کی واضح وضاحت کریں
**چند شاٹ مثالیں**: 2-3 مماثل ٹاسکس کے لئے مثالیں منصوبے فراہم کریں
**آؤٹ پٹ فارمیٹ**: قابل اعتماد پارسنگ کے لئے سٹرکچرڈ آؤٹ پٹ (JSON، نمبر شدہ فہرستیں) مخصوص کریں
**سیاق و سباق کی ونڈو**: حالیہ ملاحظات (آخری 5 اسٹیپس) شامل کریں لیکن ٹوکن کی حد میں رہنے کے لئے پرانی تاریخ کو کاٹ دیں
**خرابی کا انتظام**: جب کافی معلومات نہ ہوں تو LLM کو "UNCERTAIN" آؤٹ پٹ کرنے کے لئے پرومنٹ کریں؛ وضاحت کے لئے انسان کو کویری کریں

### مشق ورزش

ReAct ایجنٹ امپلیمنٹ کریں جو:
1. اعلیٰ سطح کا ہدف لیتا ہے: "4 افراد کے لئے کھانے کی میز تیار کریں"
2. اشیاء کے مقامات کے لئے نمونہ ماحول کو کویری کرتا ہے
3. منصوبے موافق طور پر تیار کرتا ہے (اگر پلیٹس دستیاب نہ ہوں، متبادل جگہ آزمائیں)
4. ناکامیوں کو باعزت طور پر سنبھالتا ہے (اگر شے بہت بھاری ہو، انسانی مدد کی درخواست کریں)

**ری فلیکشن** کے ساتھ بڑھائیں: ناکام کوشش کے بعد، ناکامی کا تجزیہ کرنے اور متبادل حکمت عملی تجویز کرنے کے لئے LLM کو پرومنٹ کریں۔

## اگلے اقدامات

آپ نے ترتیب وار ٹاسک انجام دہی کے لئے LLM بیسڈ منصوبہ بندی امپلیمنٹ کی ہے۔ **ہفتہ 12: ملٹی موڈل انضمام** میں، آپ CLIP کا استعمال کرتے ہوئے زبان کی سمجھ کو ویژوئل ادراک سے جوڑیں گے، روبوٹس کو "لال شے" جیسے کمانڈز کو مخصوص منظر اداروں میں جڑنے کی اجازت دیں گے۔