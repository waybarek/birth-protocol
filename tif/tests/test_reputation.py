“””
Unit tests for reputation tracking
Run with: pytest tif/tests/test_reputation.py
“””

import pytest
import tempfile
import os
from tif.reputation import ReputationTracker

def test_reputation_init():
“”“Test reputation tracker initialization”””
tracker = ReputationTracker()

```
assert tracker.decay == 0.99
assert tracker.alpha == 100.0
assert len(tracker.reputations) == 0
```

def test_reputation_update():
“”“Test reputation update mechanism”””
tracker = ReputationTracker(initial_reputation=50.0)

```
# Update with good metrics
new_rep = tracker.update(
    agent_id="agent_001",
    i_directed=5.0,
    d_sem=0.1,
    initial_reputation=50.0
)

# Should increase reputation
assert new_rep > 50.0, "Good metrics should increase reputation"
assert tracker.get_reputation("agent_001") == new_rep
```

def test_reputation_decay():
“”“Test that reputation decays over time”””
tracker = ReputationTracker(decay=0.9)

```
# Set initial reputation
tracker.update("agent_001", i_directed=5.0, d_sem=0.1, initial_reputation=100.0)
initial_rep = tracker.get_reputation("agent_001")

# Apply decay
tracker.apply_global_decay()
decayed_rep = tracker.get_reputation("agent_001")

assert decayed_rep < initial_rep, "Reputation should decay"
assert decayed_rep == pytest.approx(initial_rep * 0.9, rel=0.01)
```

def test_reputation_history():
“”“Test that history is recorded”””
tracker = ReputationTracker()

```
tracker.update("agent_001", i_directed=5.0, d_sem=0.1)
tracker.update("agent_001", i_directed=4.5, d_sem=0.15)

history = tracker.get_history("agent_001")

assert len(history) == 2
assert history[0]["i_directed"] == 5.0
assert history[1]["i_directed"] == 4.5
```

def test_reputation_top_agents():
“”“Test getting top agents by reputation”””
tracker = ReputationTracker()

```
tracker.update("agent_001", i_directed=8.0, d_sem=0.1)
tracker.update("agent_002", i_directed=5.0, d_sem=0.2)
tracker.update("agent_003", i_directed=9.0, d_sem=0.05)

top = tracker.get_top_agents(n=2)

assert len(top) == 2
assert top[0][0] == "agent_003"  # Highest reputation
assert top[0][1] > top[1][1]  # Sorted descending
```

def test_reputation_persistence():
“”“Test saving and loading reputation state”””
with tempfile.NamedTemporaryFile(mode=‘w’, delete=False, suffix=’.json’) as f:
temp_path = f.name

```
try:
    # Create and populate tracker
    tracker1 = ReputationTracker(storage_path=temp_path)
    tracker1.update("agent_001", i_directed=5.0, d_sem=0.1)
    tracker1.save()
    
    # Load in new tracker
    tracker2 = ReputationTracker(storage_path=temp_path)
    
    assert tracker2.get_reputation("agent_001") == tracker1.get_reputation("agent_001")
    assert len(tracker2.get_history("agent_001")) == 1

finally:
    os.unlink(temp_path)
```

def test_reputation_stats():
“”“Test statistics computation”””
tracker = ReputationTracker()

```
tracker.update("agent_001", i_directed=5.0, d_sem=0.1)
tracker.update("agent_002", i_directed=6.0, d_sem=0.05)

stats = tracker.get_stats()

assert stats["num_agents"] == 2
assert stats["avg_reputation"] > 0
assert stats["max_reputation"] >= stats["min_reputation"]
```

def test_proof_of_contribution_weight():
“”“Test PoC weight calculation”””
tracker = ReputationTracker()

```
# Weight = √I→ × (1 - d_sem)
weight = tracker.compute_proof_of_contribution_weight(
    agent_id="agent_001",
    i_directed=9.0,  # √9 = 3
    d_sem=0.1        # 1 - 0.1 = 0.9
)

expected = 3.0 * 0.9  # 2.7
assert weight == pytest.approx(expected, rel=0.01)
```

def test_reputation_reset():
“”“Test resetting agent reputation”””
tracker = ReputationTracker()

```
tracker.update("agent_001", i_directed=5.0, d_sem=0.1)
assert tracker.get_reputation("agent_001") is not None

tracker.reset_agent("agent_001")
assert tracker.get_reputation("agent_001") is None
```

if **name** == “**main**”:
pytest.main([**file**, “-v”])
