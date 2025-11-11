“””
Agent reputation tracking and scoring system

Implements: Reputation_{t+1} = Reputation_t · decay + α · (I→ / max_I) · (1 - d_sem)
“””

import json
from typing import Dict, Optional, List
from pathlib import Path
import time

class ReputationTracker:
“””
Track and update agent reputation scores based on TIF metrics

```
Reputation formula (from TIF_SPEC.md v0.1):
Reputation_{t+1} = Reputation_t · decay + α · (I→(t) / max I) · (1 - d_sem(t))

Parameters:
- decay = 0.99 per epoch (default)
- α = 100 (tunable reward multiplier)
"""

def __init__(
    self,
    decay: float = 0.99,
    alpha: float = 100.0,
    max_i_directed: float = 10.0,
    storage_path: Optional[str] = None
):
    """
    Initialize reputation tracker
    
    Args:
        decay: Decay factor per epoch (0.99 = 1% decay)
        alpha: Reward multiplier for good behavior
        max_i_directed: Maximum expected I→ for normalization
        storage_path: Optional path to persist reputation scores
    """
    self.decay = decay
    self.alpha = alpha
    self.max_i_directed = max_i_directed
    self.storage_path = Path(storage_path) if storage_path else None
    
    # Agent reputation scores: {agent_id: score}
    self.reputations: Dict[str, float] = {}
    
    # History: {agent_id: [{"timestamp": ..., "i_directed": ..., "d_sem": ...}]}
    self.history: Dict[str, List[dict]] = {}
    
    # Load existing state if available
    if self.storage_path and self.storage_path.exists():
        self.load()

def update(
    self,
    agent_id: str,
    i_directed: float,
    d_sem: float,
    initial_reputation: float = 50.0
) -> float:
    """
    Update agent reputation based on new TIF metrics
    
    Args:
        agent_id: Unique agent identifier
        i_directed: Directed information score
        d_sem: Semantic distortion score
        initial_reputation: Starting reputation for new agents
    
    Returns:
        Updated reputation score
    """
    # Initialize new agents
    if agent_id not in self.reputations:
        self.reputations[agent_id] = initial_reputation
        self.history[agent_id] = []
    
    # Apply decay to current reputation
    current_rep = self.reputations[agent_id] * self.decay
    
    # Compute reward term
    # Normalize I→ by max expected value
    i_normalized = min(1.0, i_directed / self.max_i_directed)
    
    # Semantic quality term (higher is better)
    semantic_quality = 1.0 - d_sem
    
    # Combined reward
    reward = self.alpha * i_normalized * semantic_quality
    
    # Update reputation
    new_rep = current_rep + reward
    self.reputations[agent_id] = new_rep
    
    # Record in history
    self.history[agent_id].append({
        "timestamp": time.time(),
        "i_directed": i_directed,
        "d_sem": d_sem,
        "reward": reward,
        "reputation": new_rep
    })
    
    # Persist if storage enabled
    if self.storage_path:
        self.save()
    
    return new_rep

def get_reputation(self, agent_id: str) -> Optional[float]:
    """Get current reputation score for an agent"""
    return self.reputations.get(agent_id)

def get_history(self, agent_id: str) -> List[dict]:
    """Get full history for an agent"""
    return self.history.get(agent_id, [])

def get_top_agents(self, n: int = 10) -> List[tuple]:
    """
    Get top N agents by reputation
    
    Returns:
        List of (agent_id, reputation) tuples sorted by score
    """
    sorted_agents = sorted(
        self.reputations.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_agents[:n]

def apply_global_decay(self):
    """
    Apply decay to all agent reputations (call once per epoch)
    """
    for agent_id in self.reputations:
        self.reputations[agent_id] *= self.decay

def reset_agent(self, agent_id: str):
    """Reset an agent's reputation and history"""
    if agent_id in self.reputations:
        del self.reputations[agent_id]
    if agent_id in self.history:
        del self.history[agent_id]

def save(self):
    """Save reputation state to disk"""
    if not self.storage_path:
        raise ValueError("No storage_path configured")
    
    state = {
        "decay": self.decay,
        "alpha": self.alpha,
        "max_i_directed": self.max_i_directed,
        "reputations": self.reputations,
        "history": self.history
    }
    
    with open(self.storage_path, 'w') as f:
        json.dump(state, f, indent=2)

def load(self):
    """Load reputation state from disk"""
    if not self.storage_path or not self.storage_path.exists():
        return
    
    with open(self.storage_path, 'r') as f:
        state = json.load(f)
    
    self.decay = state.get("decay", self.decay)
    self.alpha = state.get("alpha", self.alpha)
    self.max_i_directed = state.get("max_i_directed", self.max_i_directed)
    self.reputations = state.get("reputations", {})
    self.history = state.get("history", {})

def get_stats(self) -> dict:
    """Get summary statistics"""
    if not self.reputations:
        return {
            "num_agents": 0,
            "total_reputation": 0.0,
            "avg_reputation": 0.0,
            "max_reputation": 0.0,
            "min_reputation": 0.0
        }
    
    scores = list(self.reputations.values())
    return {
        "num_agents": len(scores),
        "total_reputation": sum(scores),
        "avg_reputation": sum(scores) / len(scores),
        "max_reputation": max(scores),
        "min_reputation": min(scores)
    }

def compute_proof_of_contribution_weight(
    self,
    agent_id: str,
    i_directed: float,
    d_sem: float
) -> float:
    """
    Compute proof-of-contribution weight for treasury allocation
    
    Weight = √I→ × (1 - d_sem)
    
    From TIF_SPEC.md section 4: Proof-of-Contribution
    """
    import math
    weight = math.sqrt(i_directed) * (1.0 - d_sem)
    return max(0.0, weight)
```
