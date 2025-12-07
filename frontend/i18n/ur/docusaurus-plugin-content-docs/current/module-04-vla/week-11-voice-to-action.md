# ہفتہ 11: وائس ٹو ایکشن پائپ لائن

![Voice-to-Action Pipeline](/img/ai-12.png)

## OpenAI وہیسپر کے ساتھ اسپیچ ریکوگنیشن

OpenAI وہیسپر ایک جدید خودکار اسپیچ ریکوگنیشن (ASR) سسٹم ہے جسے 680,000 گھنٹے کے متعدد زبانوں کے ڈیٹا پر تربیت دی گئی ہے۔ روایتی ASR ماڈلز کے مقابلے جن کو کسٹم ویک ورڈ ڈیٹیکشن اور زبان کے مطابق تربیت کی ضرورت ہوتی ہے، وہیسپر 99 زبانوں میں صفر-شاٹ ٹرانسکرپشن فراہم کرتا ہے جو شور ماحول میں مستحکم کارکردگی کے ساتھ ہیومنوائڈ روبوٹس کے لئے ضروری ہے جو گھروں، فیکٹریوں، اور عوامی مقامات پر کام کرتے ہیں۔

### روبوٹکس کے لئے وہیسپر کیوں؟

**شور میں مستحکم**: وہیسپر کی تربیت میں متنوع ایکوسٹک کنڈیشنز شامل تھیں (پس منظر کی موسیقی، اوور لیپنگ اسپیچ، مشینری نوائس). ایک ہیومنوائڈ جو کچن میں کام کر رہا ہو وہ چلنے والے ڈش واشرز اور گفتگو کے اوپر کمانڈز کو ٹرانسکرائیب کر سکتا ہے۔

**متعدد زبانوں کی حمایت**: عالمی اتارنے کے لئے متعدد زبانوں کے انٹرفیس کی ضرورت ہوتی ہے۔ وہیسپر کوڈ سوئچنگ (ایک جملے کے اندر زبانوں کو ملانا) کو سنبھالتا ہے جو متعدد زبانوں والے گھروں میں عام ہے۔

**کوئی فائن ٹیوننگ کی ضرورت نہیں**: ڈومین کے مطابق ASR ماڈلز کے مقابلے، وہیسپر روبوٹکس کی ویکیبیولری ("گریس فلپس سکریو ڈرائیور کو تھامیں") کو کسٹم تربیت کے بغیر عام کر لیتا ہے۔

### انسٹالیشن اور سیٹ اپ

```python
# وہیسپر اور انحصار انسٹال کریں
# آڈیو پروسیسنگ کے لئے ffmpeg کی ضرورت ہے: sudo apt install ffmpeg
import subprocess
subprocess.run(["pip", "install", "openai-whisper", "sounddevice", "numpy"])

import whisper
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

# وہیسپر ماڈل لوڈ کریں (اختیارات: tiny، base، small، medium، large)
# کاروبار: بڑے ماڈل = بہتر درستگی لیکن سست انفرس
# ریل ٹائم روبوٹکس کے لئے: 'base' (74M پیرامیٹرز) GPU پر <0.5s لیٹنسی حاصل کرتا ہے
model = whisper.load_model("base")  # پہلی رن پر ~140MB ڈاؤن لوڈ کرتا ہے

def record_audio(duration=5, sample_rate=16000):
    """
    مائیکروفون سے مخصوص مدت کے لئے آڈیو ریکارڈ کریں۔

    Args:
        duration: سیکنڈ میں ریکارڈنگ کی لمبائی
        sample_rate: Hz (16kHz وہیسپر کی مقامی شرح ہے، ریسیمپلنگ سے بچتا ہے)
    Returns:
        numpy ارے: [-1, 1] کے رینج میں آڈیو سیمپلز
    """
    print(f"{duration} سیکنڈ کے لئے ریکارڈنگ...")
    # ڈیفالٹ مائیکروفون سے ریکارڈ کریں (مخصوص مائیکروفون کے لئے ڈیوائس انڈیکس سیٹ کریں)
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,  # مونو آڈیو
        dtype='float32'
    )
    sd.wait()  # ریکارڈنگ مکمل ہونے تک بلاک کریں
    print("ریکارڈنگ مکمل ہو گئی۔")
    return audio.flatten()

def transcribe_audio(audio_array):
    """
    وہیسپر کا استعمال کرتے ہوئے آڈیو کو ٹیکسٹ میں ٹرانسکرائیب کریں۔

    Args:
        audio_array: NumPy ارے آڈیو سیمپلز کا
    Returns:
        dict: ٹرانسکرپشن کا نتیجہ 'text'، 'language'، 'segments' کے ساتھ
    """
    # وہیسپر float32 آڈیو کی توقع کرتا ہے جو [-1, 1] میں نارملائز ہو
    result = model.transcribe(
        audio_array,
        language='en',  # خود کار پتہ لگانے کے لئے None سیٹ کریں (لیٹنسی شامل کرتا ہے)
        task='transcribe',  # متبادل: انگریزی کے علاوہ کو انگریزی میں ترجمہ کرنے کے لئے 'translate'
        fp16=True  # GPU پر 2x رفتار کے لئے ہاف پریشنشن فعال کریں
    )
    return result

# مثال کا استعمال: ریکارڈ اور ٹرانسکرائیب کریں
audio = record_audio(duration=5)
result = transcribe_audio(audio)
print(f"ٹرانسکرپشن: {result['text']}")
# آؤٹ پٹ کی مثال: "روبوٹ، لال مگ کو اٹھاؤ اور اسے ٹیبل پر رکھو۔"
```

## کمانڈ پارسنگ اور انٹینٹ کلاسیفکیشن

خام ٹرانسکرپشنز کو سٹرکچرڈ روبوٹ کمانڈز میں پارس کرنے کی ضرورت ہوتی ہے۔ ہم **انٹینٹ** (کیا ایکشن)، **اینٹیٹیز** (ہدف اشیاء)، اور **پیرامیٹرز** (مقامات، مقداریں) نکالتے ہیں۔

### رول بیسڈ پارسنگ

محدود ویکیبیولری کے لئے (ویئر ہاؤس روبوٹس جن کے پاس فکسڈ کمانڈز ہیں)، رول بیسڈ پارسنگ کافی ہے:

```python
import re
from typing import Dict, List, Optional

class CommandParser:
    """
    قدرتی زبان کو سٹرکچرڈ روبوٹ کمانڈز میں پارس کریں۔
    ایکشن وریبز اور اشیاء کے حوالوں کے ساتھ امپیریٹو جملوں کو سنبھالتا ہے۔
    """

    # ایکشن ویکیبیولری کی وضاحت سمنونم کے ساتھ
    ACTION_VERBS = {
        'pick': ['pick', 'grab', 'grasp', 'take', 'lift'],
        'place': ['place', 'put', 'set', 'drop', 'position'],
        'navigate': ['go', 'move', 'walk', 'navigate', 'travel'],
        'open': ['open'],
        'close': ['close', 'shut']
    }

    # مقام نکالنے کے لئے سپیشل پریپوزیشنز
    LOCATIONS = ['on', 'in', 'under', 'next to', 'above', 'below', 'near']

    def __init__(self):
        # کارکردگی کے لئے regex پیٹرن کمپائل کریں
        self.action_pattern = self._build_action_pattern()

    def _build_action_pattern(self) -> re.Pattern:
        """کوئی بھی ایکشن وریب میچ کرنے والے regex تیار کریں۔"""
        all_verbs = [v for synonyms in self.ACTION_VERBS.values() for v in synonyms]
        pattern = r'\b(' + '|'.join(all_verbs) + r')\b'
        return re.compile(pattern, re.IGNORECASE)

    def parse(self, text: str) -> Dict:
        """
        کمانڈ سے انٹینٹ اور اینٹیٹیز نکالیں۔

        Args:
            text: قدرتی زبان کی کمانڈ
        Returns:
            dict: {
                'intent': str,
                'object': str,
                'location': str,
                'confidence': float
            }
        """
        text = text.lower().strip()

        # ایکشن انٹینٹ نکالیں
        action_match = self.action_pattern.search(text)
        if not action_match:
            return {'intent': 'unknown', 'confidence': 0.0}

        verb = action_match.group(1)
        intent = self._map_verb_to_intent(verb)

        # ہدف اشیاء نکالیں (ایکشن وریب کے بعد کا ناؤن)
        object_match = re.search(
            r'\b(?:the\s+)?(\w+(?:\s+\w+)?)\b',  # "red mug" یا "mug" کو کیپچر کرتا ہے
            text[action_match.end():]
        )
        target_object = object_match.group(1) if object_match else None

        # مقام نکالیں (پریپوزیشنل فریز)
        location = self._extract_location(text)

        return {
            'intent': intent,
            'object': target_object,
            'location': location,
            'confidence': 0.95 if target_object else 0.6
        }

    def _map_verb_to_intent(self, verb: str) -> str:
        """ڈیٹیکٹ کردہ وریب کو کینونیکل انٹینٹ میں میپ کریں۔"""
        for intent, synonyms in self.ACTION_VERBS.items():
            if verb in synonyms:
                return intent
        return 'unknown'

    def _extract_location(self, text: str) -> Optional[str]:
        """مقام فریز نکالیں (مثلاً 'on the table')."""
        for prep in self.LOCATIONS:
            pattern = f'{prep}\\s+(?:the\\s+)?(\\w+(?:\\s+\\w+)?)'
            match = re.search(pattern, text)
            if match:
                return f"{prep} {match.group(1)}"
        return None

# مثال کا استعمال
parser = CommandParser()
commands = [
    "Pick up the red mug",
    "Place it on the table",
    "Go to the kitchen",
    "Open the drawer"
]

for cmd in commands:
    result = parser.parse(cmd)
    print(f"Input: {cmd}")
    print(f"Parsed: {result}\n")

# Output:
# Input: Pick up the red mug
# Parsed: {'intent': 'pick', 'object': 'red mug', 'location': None, 'confidence': 0.95}
```

### LLM بیسڈ انٹینٹ کلاسیفکیشن

کھلے اختتام والے کمانڈز کے لئے، سیمینٹک سمجھ کے لئے GPT-4 استعمال کریں:

```python
import openai
import os
import json

# API کلید ماحولیاتی متغیر سے سیٹ کریں (کبھی بھی راز کو ہارڈ کوڈ نہ کریں)
openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_intent_with_llm(command: str) -> Dict:
    """
    قدرتی زبان سے سٹرکچرڈ انٹینٹ نکالنے کے لئے GPT-4 استعمال کریں۔
    'ڈور بند کرنے کے بعد مجھے پانی لاؤ' جیسے پیچیدہ کمانڈز کو سنبھالتا ہے۔

    Args:
        command: قدرتی زبان کی ہدایت
    Returns:
        dict: ایکشنز، پیرامیٹرز، اور ترتیب کے ساتھ سٹرکچرڈ کمانڈ
    """
    # سسٹم پرومپٹ روبوٹ کی صلاحیتوں اور آؤٹ پٹ فارمیٹ کی وضاحت کرتا ہے
    system_prompt = """آپ ہیومنوائڈ روبوٹ کے لئے کمانڈ پارسر ہیں۔
    صارف کے کمانڈز سے انٹینٹ، اشیاء، مقامات، اور ایکشن ترتیب نکالیں۔

    دستیاب ایکشنز: pick, place, navigate, open, close, wait.

    JSON کے ساتھ واپسی فارمیٹ:
    {
        "actions": [
            {"intent": "action", "object": "item", "location": "place", "parameters": {}}
        ],
        "confidence": 0.0-1.0
    }
    """

    # چند شاٹ مثالیں پارسنگ کی درستگی میں اضافہ کرتی ہیں
    user_prompt = f"""Command: {command}

    Examples:
    Input: "Grab the blue cup and put it in the sink"
    Output: {{"actions": [{{"intent": "pick", "object": "blue cup"}}, {{"intent": "place", "location": "sink"}}], "confidence": 0.95}}

    Input: "Go to the bedroom"
    Output: {{"actions": [{{"intent": "navigate", "location": "bedroom"}}], "confidence": 0.98}}

    اب اوپر کا کمانڈ پارس کریں۔
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",  # تیز/سست انفرس کے لئے gpt-3.5-turbo استعمال کریں
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,  # کمانڈ پارسنگ کے لئے ڈیٹرمنسٹک آؤٹ پٹ
        max_tokens=200
    )

    # جواب سے JSON نکالیں
    result_text = response.choices[0].message.content
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {"actions": [], "confidence": 0.0, "error": "Parse failed"}

# مثال: پیچیدہ متعدد اسٹیپ کمانڈ
command = "First go to the kitchen, then pick up the green bottle and bring it here."
intent = classify_intent_with_llm(command)
print(json.dumps(intent, indent=2))

# Output:
# {
#   "actions": [
#     {"intent": "navigate", "location": "kitchen"},
#     {"intent": "pick", "object": "green bottle"},
#     {"intent": "navigate", "location": "user"}
#   ],
#   "confidence": 0.92
# }
```

## وائس انٹرفیس ڈیزائن

 موثر انسان-روبوٹ وائس انٹرایکشن کی ضرورت ہے:

**ویک ورڈ ڈیٹیکشن**: صرف "Hey Robot" پر سننا فعال کرنے کے لئے لائٹ ویٹ ماڈلز (Porcupine، Snowboy) استعمال کریں، جھوٹی ایکٹیویشنز کو کم کرتا ہے۔

**تصدیقی حلقہ جات**: پارس کردہ کمانڈز کو صارف کو دہرائیں: "میں لال مگ کو اٹھاؤں گا۔ جاری رکھیں؟" انجام دینے سے پہلے غلط فہمیوں کو روکتا ہے۔

**فیڈ بیک**: طویل آپریشنز کے دوران آڈیو تصدیق فراہم کریں: "کچن کی طرف جا رہا ہے... پہنچ گیا۔ سبز بوتل تلاش کر رہا ہے..."

### مشق ورزش

مکمل وائس کمانڈ پائپ لائن امپلیمنٹ کریں:
1. 5 سیکنڈ کا آڈیو کلپ ریکارڈ کریں
2. وہیسپر کے ساتھ ٹرانسکرائیب کریں
3. رول بیسڈ پارسر کے ساتھ انٹینٹ پارس کریں
4. روبوٹ انجام دہی کے لئے ROS 2 ایکشن گول تیار کریں

نفیوں ("نیلی کپ کو نہ اٹھاؤ") اور شرائط ("اگر دروازہ کھلا ہے، تو اس کے ذریعے جاؤ") کو سنبھالنے کے لئے پارسر کو بڑھائیں۔

## اگلے اقدامات

آپ نے ادراک کی پرت تیار کی ہے (اسپیچ → ٹیکسٹ → انٹینٹ). **ہفتہ 11: LLM منصوبہ بندی** میں، آپ GPT-4 کا استعمال کر کے متعدد اسٹیپ ٹاسک منصوبے تیار کریں گے، انجام کے دوران موافق ریزننگ کے لئے ReAct پیٹرن امپلیمنٹ کریں گے۔