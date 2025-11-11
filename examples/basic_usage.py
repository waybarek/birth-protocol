“””
Basic TIF Usage Example

Demonstrates core TIF functionality:

- Semantic distortion calculation
- Directed information measurement
- Reputation tracking
- Drift detection
  “””

from tif.core import directed_information, semantic_distortion, compute_tif_score
from tif.reputation import ReputationTracker
from tif.thresholds import DriftMonitor
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def example_1_semantic_distortion():
“”“Example 1: Measure semantic drift between texts”””
print(”\n=== Example 1: Semantic Distortion ===”)

```
# Similar texts (low distortion)
text_a = "The cat sits on the mat"
text_b = "A feline rests on the rug"
d_sem = semantic_distortion(text_a, text_b)
print(f"Similar texts: d_sem = {d_sem:.3f}")

# Different texts (high distortion)
text_c = "Quantum computing revolutionizes cryptography"
d_sem2 = semantic_distortion(text_a, text_c)
print(f"Different texts: d_sem = {d_sem2:.3f}")
```

def example_2_directed_information():
“”“Example 2: Calculate information flow”””
print(”\n=== Example 2: Directed Information ===”)

```
# Load a small model (GPT-2)
print("Loading model (this may take a moment)...")
model_name = "gpt2"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Example: measuring how much context flows into response
prompt = "The weather today is"
response = " sunny and warm"

prompt_ids = tokenizer.encode(prompt, return_tensors="pt")[0]
response_ids = tokenizer.encode(response, return_tensors="pt")[0]

with torch.no_grad():
    i_directed = directed_information(prompt_ids, response_ids, model)

print(f"Prompt: '{prompt}'")
print(f"Response: '{response}'")
print(f"I→(prompt → response) = {i_directed:.3f} bits")
print("(Higher = more information from context used)")
```

def example_3_reputation_tracking():
“”“Example 3: Track agent reputation over time”””
print(”\n=== Example 3: Reputation Tracking ===”)

```
tracker = ReputationTracker(decay=0.99, alpha=100.0)

# Simulate agent behavior over time
agents = {
    "agent_good": [(7.0, 0.1), (6.5, 0.15), (8.0, 0.05)],
    "agent_bad": [(3.0, 0.4), (2.5, 0.45), (3.5, 0.35)]
}

for agent_id, metrics in agents.items():
    print(f"\n{agent_id}:")
    for i, (i_dir, d_sem) in enumerate(metrics, 1):
        rep = tracker.update(agent_id, i_dir, d_sem)
        print(f"  Epoch {i}: I→={i_dir:.1f}, d_sem={d_sem:.2f} → Rep={rep:.1f}")

# Show rankings
print("\n--- Top Agents ---")
for agent_id, rep in tracker.get_top_agents():
    print(f"{agent_id}: {rep:.1f}")
```

def example_4_drift_detection():
“”“Example 4: Detect semantic drift”””
print(”\n=== Example 4: Drift Detection ===”)

```
monitor = DriftMonitor()

# Simulate agent outputs over time
scenarios = [
    ("Good Agent", [(0.8, 0.2), (0.75, 0.25), (0.85, 0.15)]),
    ("Drifting Agent", [(0.7, 0.25), (0.55, 0.38), (0.45, 0.42)])
]

for agent_name, metrics in scenarios:
    print(f"\n{agent_name}:")
    agent_id = agent_name.lower().replace(" ", "_")
    
    for i, (i_dir, d_sem) in enumerate(metrics, 1):
        alerts = monitor.check_all(agent_id, i_dir, d_sem, timestamp=float(i))
        
        if alerts:
            print(f"  Hop {i}: I→={i_dir:.2f}, d_sem={d_sem:.2f} ⚠️ ALERT")
            for alert in alerts:
                print(f"    - {alert.level.value}: {alert.message}")
        else:
            print(f"  Hop {i}: I→={i_dir:.2f}, d_sem={d_sem:.2f} ✓ OK")
```

def example_5_complete_scoring():
“”“Example 5: Complete TIF scoring pipeline”””
print(”\n=== Example 5: Complete TIF Scoring ===”)

```
# Load model
print("Loading model...")
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Test case
history = "What is the capital of France?"
response = "The capital of France is Paris."
reference = "Paris is the capital city of France."

with torch.no_grad():
    result = compute_tif_score(
        history=history,
        response=response,
        model=model,
        tokenizer=tokenizer,
        reference=reference,
        weights=(0.6, 0.4)  # 60% info flow, 40% semantic
    )

print(f"\nQuery: {history}")
print(f"Response: {response}")
print(f"\nTIF Scores:")
print(f"  Information Flow (I→): {result['i_directed']:.3f} bits")
print(f"  Semantic Distortion: {result['d_sem']:.3f}")
print(f"  Semantic Alignment: {result['semantic_score']:.3f}")
print(f"  Total Score: {result['total_score']:.3f}")
```

def main():
“”“Run all examples”””
print(”=” * 60)
print(“TIF Library - Basic Usage Examples”)
print(”=” * 60)

```
# Example 1: Semantic distortion (fast, no model needed)
example_1_semantic_distortion()

# Example 2: Directed information (requires model)
example_2_directed_information()

# Example 3: Reputation tracking (no model needed)
example_3_reputation_tracking()

# Example 4: Drift detection (no model needed)
example_4_drift_detection()

# Example 5: Complete scoring (requires model)
example_5_complete_scoring()

print("\n" + "=" * 60)
print("Examples complete!")
print("=" * 60)
```

if **name** == “**main**”:
main()
