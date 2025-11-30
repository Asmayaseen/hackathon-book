# Week 11: Voice-to-Action Pipeline

![Voice-to-Action Pipeline](/img/ai-12.png)

## Speech Recognition with OpenAI Whisper

OpenAI Whisper is a state-of-the-art automatic speech recognition (ASR) system trained on 680,000 hours of multilingual data. Unlike traditional ASR models requiring custom wake-word detection and language-specific training, Whisper provides zero-shot transcription across 99 languages with robust performance in noisy environments—critical for humanoid robots operating in homes, factories, and public spaces.

### Why Whisper for Robotics?

**Noise Robustness**: Whisper's training included diverse acoustic conditions (background music, overlapping speech, machinery noise). A humanoid working in a kitchen can transcribe commands over running dishwashers and conversations.

**Multilingual Support**: Global deployments require multi-language interfaces. Whisper handles code-switching (mixing languages mid-sentence) common in multilingual households.

**No Fine-Tuning Required**: Unlike domain-specific ASR models, Whisper generalizes to robotics vocabulary ("grasp the Phillips screwdriver") without custom training.

### Installation and Setup

```python
# Install Whisper and dependencies
# Requires ffmpeg for audio processing: sudo apt install ffmpeg
import subprocess
subprocess.run(["pip", "install", "openai-whisper", "sounddevice", "numpy"])

import whisper
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

# Load Whisper model (options: tiny, base, small, medium, large)
# Trade-off: larger models = better accuracy but slower inference
# For real-time robotics: 'base' (74M params) achieves <0.5s latency on GPU
model = whisper.load_model("base")  # Downloads ~140MB on first run

def record_audio(duration=5, sample_rate=16000):
    """
    Record audio from microphone for specified duration.

    Args:
        duration: Recording length in seconds
        sample_rate: Hz (16kHz is Whisper's native rate, avoids resampling)

    Returns:
        numpy array: Audio samples in range [-1, 1]
    """
    print(f"Recording for {duration} seconds...")
    # Record from default microphone (set device index for specific mic)
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,  # Mono audio
        dtype='float32'
    )
    sd.wait()  # Block until recording completes
    print("Recording complete.")
    return audio.flatten()

def transcribe_audio(audio_array):
    """
    Transcribe audio to text using Whisper.

    Args:
        audio_array: NumPy array of audio samples

    Returns:
        dict: Transcription result with 'text', 'language', 'segments'
    """
    # Whisper expects float32 audio normalized to [-1, 1]
    result = model.transcribe(
        audio_array,
        language='en',  # Set to None for auto-detection (adds latency)
        task='transcribe',  # Alternative: 'translate' for non-English to English
        fp16=True  # Enable half-precision for 2x speed on GPU
    )
    return result

# Example usage: Record and transcribe
audio = record_audio(duration=5)
result = transcribe_audio(audio)
print(f"Transcription: {result['text']}")
# Output example: "Robot, pick up the red mug and place it on the table."
```

## Command Parsing and Intent Classification

Raw transcriptions require parsing into structured robot commands. We extract **intent** (what action), **entities** (target objects), and **parameters** (locations, quantities).

### Rule-Based Parsing

For constrained vocabularies (warehouse robots with fixed commands), rule-based parsing suffices:

```python
import re
from typing import Dict, List, Optional

class CommandParser:
    """
    Parse natural language into structured robot commands.
    Handles imperative sentences with action verbs and object references.
    """

    # Define action vocabulary with synonyms
    ACTION_VERBS = {
        'pick': ['pick', 'grab', 'grasp', 'take', 'lift'],
        'place': ['place', 'put', 'set', 'drop', 'position'],
        'navigate': ['go', 'move', 'walk', 'navigate', 'travel'],
        'open': ['open'],
        'close': ['close', 'shut']
    }

    # Spatial prepositions for location extraction
    LOCATIONS = ['on', 'in', 'under', 'next to', 'above', 'below', 'near']

    def __init__(self):
        # Compile regex patterns for efficiency
        self.action_pattern = self._build_action_pattern()

    def _build_action_pattern(self) -> re.Pattern:
        """Create regex matching any action verb."""
        all_verbs = [v for synonyms in self.ACTION_VERBS.values() for v in synonyms]
        pattern = r'\b(' + '|'.join(all_verbs) + r')\b'
        return re.compile(pattern, re.IGNORECASE)

    def parse(self, text: str) -> Dict:
        """
        Extract intent and entities from command.

        Args:
            text: Natural language command

        Returns:
            dict: {
                'intent': str,
                'object': str,
                'location': str,
                'confidence': float
            }
        """
        text = text.lower().strip()

        # Extract action intent
        action_match = self.action_pattern.search(text)
        if not action_match:
            return {'intent': 'unknown', 'confidence': 0.0}

        verb = action_match.group(1)
        intent = self._map_verb_to_intent(verb)

        # Extract target object (noun after action verb)
        object_match = re.search(
            r'\b(?:the\s+)?(\w+(?:\s+\w+)?)\b',  # Captures "red mug" or "mug"
            text[action_match.end():]
        )
        target_object = object_match.group(1) if object_match else None

        # Extract location (prepositional phrase)
        location = self._extract_location(text)

        return {
            'intent': intent,
            'object': target_object,
            'location': location,
            'confidence': 0.95 if target_object else 0.6
        }

    def _map_verb_to_intent(self, verb: str) -> str:
        """Map detected verb to canonical intent."""
        for intent, synonyms in self.ACTION_VERBS.items():
            if verb in synonyms:
                return intent
        return 'unknown'

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location phrase (e.g., 'on the table')."""
        for prep in self.LOCATIONS:
            pattern = f'{prep}\\s+(?:the\\s+)?(\\w+(?:\\s+\\w+)?)'
            match = re.search(pattern, text)
            if match:
                return f"{prep} {match.group(1)}"
        return None

# Example usage
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

### LLM-Based Intent Classification

For open-ended commands, use GPT-4 for semantic understanding:

```python
import openai
import os
import json

# Set API key from environment variable (never hardcode secrets)
openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_intent_with_llm(command: str) -> Dict:
    """
    Use GPT-4 to extract structured intent from natural language.
    Handles complex commands like 'After closing the door, bring me water.'

    Args:
        command: Natural language instruction

    Returns:
        dict: Structured command with intent, parameters, and sequence
    """
    # System prompt defines robot's capabilities and output format
    system_prompt = """You are a command parser for a humanoid robot.
    Extract intent, objects, locations, and action sequences from user commands.

    Available actions: pick, place, navigate, open, close, wait.

    Return JSON with format:
    {
        "actions": [
            {"intent": "action", "object": "item", "location": "place", "parameters": {}}
        ],
        "confidence": 0.0-1.0
    }
    """

    # Few-shot examples improve parsing accuracy
    user_prompt = f"""Command: {command}

    Examples:
    Input: "Grab the blue cup and put it in the sink"
    Output: {{"actions": [{{"intent": "pick", "object": "blue cup"}}, {{"intent": "place", "location": "sink"}}], "confidence": 0.95}}

    Input: "Go to the bedroom"
    Output: {{"actions": [{{"intent": "navigate", "location": "bedroom"}}], "confidence": 0.98}}

    Now parse the command above.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",  # Use gpt-3.5-turbo for faster/cheaper inference
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,  # Deterministic output for command parsing
        max_tokens=200
    )

    # Extract JSON from response
    result_text = response.choices[0].message.content
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {"actions": [], "confidence": 0.0, "error": "Parse failed"}

# Example: Complex multi-step command
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

## Voice Interface Design

Effective human-robot voice interaction requires:

**Wake Word Detection**: Use lightweight models (Porcupine, Snowboy) to activate listening only on "Hey Robot", reducing false activations.

**Confirmation Loops**: Repeat parsed commands back to user: "I will pick up the red mug. Proceed?" Prevents misunderstandings before execution.

**Feedback**: Provide audio acknowledgments during long operations: "Navigating to kitchen... Arrived. Searching for green bottle..."

### Practice Exercise

Implement a complete voice command pipeline:
1. Record 5-second audio clip
2. Transcribe with Whisper
3. Parse intent with rule-based parser
4. Generate ROS 2 action goal for robot execution

Extend the parser to handle negations ("Don't pick up the blue cup") and conditionals ("If the door is open, go through it").

## Next Steps

You've built the perception layer (speech → text → intent). In **Week 11: LLM Planning**, you'll use GPT-4 to generate multi-step task plans, implementing the ReAct pattern for adaptive reasoning during execution.
