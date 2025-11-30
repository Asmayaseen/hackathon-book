# Week 11: LLM-Based Task Planning

## Using GPT-4 for Robot Task Planning

Large Language Models excel at decomposing high-level goals into executable sub-tasks by leveraging common-sense reasoning learned from internet-scale text data. For robotics, this means translating vague instructions like "prepare breakfast" into concrete action sequences: navigate to kitchen, open fridge, retrieve eggs, close fridge, navigate to stove, etc.

### Why LLMs for Planning?

**Generalization**: Traditional planners (PDDL, hierarchical task networks) require manually authored domain models. LLMs learn task structure implicitly from diverse text—recipes, instruction manuals, how-to guides—enabling zero-shot planning for novel tasks.

**Contextual Reasoning**: LLMs infer implicit constraints. Given "make coffee," they know to check if water is available before attempting to brew, without explicit preconditions in code.

**Natural Language Interface**: Users provide goals in free-form language instead of formal specifications. "Help me set the table for dinner" is more intuitive than `set_table(num_plates=4, silverware=True)`.

**Failure Recovery**: When plans fail, LLMs replan based on error descriptions, exhibiting adaptive behavior rare in classical planners.

### Basic Task Decomposition

```python
import openai
import os
from typing import List, Dict

openai.api_key = os.getenv("OPENAI_API_KEY")

def plan_task(goal: str, context: str = "") -> List[str]:
    """
    Generate step-by-step plan for achieving robot goal.

    Args:
        goal: High-level objective (e.g., "clean the living room")
        context: Environmental state (e.g., "vacuum is in closet, trash bin is full")

    Returns:
        List of action steps in execution order
    """
    # System prompt defines robot's action space and constraints
    system_prompt = """You are a task planner for a humanoid robot.
    Break down user goals into sequential steps using available actions.

    Available actions:
    - navigate(location): Move to specified location
    - pick(object): Grasp object in front of robot
    - place(object, location): Put held object at location
    - open(object): Open door/drawer/container
    - close(object): Close door/drawer/container
    - activate(device): Turn on appliance/switch
    - deactivate(device): Turn off appliance/switch

    Constraints:
    - Robot can hold one object at a time (must place before picking new object)
    - Navigation requires clear path (cannot walk through closed doors)
    - Object must be within reach (navigate first if not visible)

    Return numbered list of steps. Be concise.
    """

    # Include environmental context to inform plan
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
        temperature=0.3,  # Low temperature for consistent planning
        max_tokens=300
    )

    # Parse numbered list into steps
    plan_text = response.choices[0].message.content
    steps = [
        line.strip()
        for line in plan_text.split('\n')
        if line.strip() and line.strip()[0].isdigit()
    ]
    return steps

# Example: Home assistance task
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

## The ReAct Pattern: Reasoning + Acting

The **ReAct** (Reasoning and Acting) pattern interleaves thought generation with action execution, allowing LLMs to adaptively adjust plans based on real-time feedback. Unlike open-loop planning (generate entire plan upfront), ReAct performs closed-loop reasoning at each step.

### ReAct Architecture

```
Observation → Thought → Action → Observation → Thought → Action → ...
```

**Observation**: Current world state from sensors (object positions, door status, battery level)
**Thought**: LLM-generated reasoning about what to do next
**Action**: Executable robot command
**Loop**: Repeat until goal achieved or failure detected

### Implementation

```python
import json
from typing import Tuple, Optional

class ReActAgent:
    """
    ReAct agent for adaptive robot task execution.
    Combines LLM reasoning with environmental feedback.
    """

    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.history = []  # Track (thought, action, observation) tuples

    def run(self, goal: str, get_observation_fn) -> bool:
        """
        Execute goal using ReAct loop.

        Args:
            goal: Task objective
            get_observation_fn: Callable returning current world state

        Returns:
            bool: True if goal achieved, False if failed
        """
        observation = get_observation_fn()
        self.history = []

        for step in range(self.max_steps):
            # Generate thought and action from LLM
            thought, action = self._reason(goal, observation)
            self.history.append((thought, action, observation))

            print(f"\n--- Step {step + 1} ---")
            print(f"Observation: {observation}")
            print(f"Thought: {thought}")
            print(f"Action: {action}")

            # Check for task completion or failure
            if action == "DONE":
                print("Goal achieved!")
                return True
            if action == "FAIL":
                print(f"Task failed: {thought}")
                return False

            # Execute action and get new observation
            observation = self._execute_action(action, get_observation_fn)

        print("Max steps reached without completion.")
        return False

    def _reason(self, goal: str, observation: str) -> Tuple[str, str]:
        """
        Generate reasoning and next action.

        Returns:
            (thought, action): Reasoning string and action command
        """
        # Build prompt with full history for context
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

        # Parse thought and action from response
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
        Execute action command (mock implementation).
        In real system, this calls ROS 2 action servers.
        """
        # Simulate action execution (replace with actual robot interface)
        print(f"Executing: {action}")

        # Return updated observation after action
        # In production: query sensors/perception system
        return get_observation_fn()

# Example usage with mock environment
def mock_get_observation():
    """
    Mock sensor reading (replace with actual perception system).
    In real system: query object detector, SLAM map, joint states.
    """
    # Simulate changing observations based on agent's actions
    observations = [
        "You are in living room. Coffee maker visible in kitchen.",
        "You are in kitchen. Coffee maker is on counter. Mug is in cabinet.",
        "Cabinet is open. Mug is visible.",
        "You are holding mug. Coffee maker has finished brewing.",
        "Mug is placed under coffee maker spout."
    ]
    # Cycle through observations (simplified; real system queries sensors)
    return observations[len(agent.history) % len(observations)]

# Run ReAct agent
agent = ReActAgent(max_steps=8)
success = agent.run(
    goal="Serve a cup of coffee",
    get_observation_fn=mock_get_observation
)
```

## Chain-of-Thought for Robots

**Chain-of-Thought (CoT)** prompting elicits intermediate reasoning steps, improving LLM performance on complex tasks. For robotics, CoT helps decompose spatiotemporal reasoning:

### CoT for Manipulation Planning

```python
def plan_grasp_with_cot(object_name: str, scene_description: str) -> Dict:
    """
    Generate grasp plan using chain-of-thought reasoning.

    Args:
        object_name: Target object to grasp
        scene_description: Visual scene layout

    Returns:
        dict: Grasp strategy with approach vector, contact points
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

    # Extract JSON from response
    text = response.choices[0].message.content
    # Find JSON block in response
    start = text.find('{')
    end = text.rfind('}') + 1
    if start != -1 and end > start:
        grasp_plan = json.loads(text[start:end])
        return grasp_plan

    return {"error": "Failed to generate grasp plan"}

# Example: Grasp planning
result = plan_grasp_with_cot(
    object_name="wine glass",
    scene_description="Wine glass on table, stem visible, surrounded by plates"
)
print(json.dumps(result, indent=2))
```

## Prompt Engineering Best Practices

**System Role**: Define robot's capabilities and constraints clearly
**Few-Shot Examples**: Provide 2-3 example plans for similar tasks
**Output Format**: Specify structured output (JSON, numbered lists) for reliable parsing
**Context Window**: Include recent observations (last 5 steps) but prune old history to stay within token limits
**Error Handling**: Prompt LLM to output "UNCERTAIN" when insufficient information; query human for clarification

### Practice Exercise

Implement a ReAct agent that:
1. Takes high-level goal: "Set the dinner table for 4 people"
2. Queries mock environment for object locations
3. Generates plans adaptively (if plates unavailable, try alternative location)
4. Handles failures gracefully (if object too heavy, request human assistance)

Extend with **reflection**: after failed attempt, prompt LLM to analyze failure and propose alternative strategy.

## Next Steps

You've implemented LLM-based planning for sequential task execution. In **Week 12: Multimodal Integration**, you'll connect language understanding to visual perception using CLIP, enabling robots to ground commands like "the red object" to specific scene entities.
