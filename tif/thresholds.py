“””
Semantic drift detection and threshold monitoring

Implements thresholds from TIF_SPEC.md section 6
“””

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class AlertLevel(Enum):
“”“Alert severity levels”””
NORMAL = “normal”
WARNING = “warning”
CRITICAL = “critical”
SLASH = “slash”

@dataclass
class DriftAlert:
“”“Alert when drift thresholds are exceeded”””
level: AlertLevel
message: str
agent_id: str
metric: str
value: float
threshold: float
timestamp: float

class DriftMonitor:
“””
Monitor semantic drift and alert when thresholds are exceeded

```
Thresholds from TIF_SPEC.md v0.1 section 6:
- single_hop: 0.65 (alert if I→ < 0.65)
- chain_10: 0.50 (slash if cumulative < 0.50 over 10 hops)
- distortion: 0.35 (flag if d_sem > 0.35)
"""

def __init__(
    self,
    single_hop_threshold: float = 0.65,
    chain_10_threshold: float = 0.50,
    distortion_threshold: float = 0.35,
    chain_length: int = 10
):
    """
    Initialize drift monitor with thresholds
    
    Args:
        single_hop_threshold: Minimum I→ per hop (default: 0.65)
        chain_10_threshold: Minimum cumulative I→ over chain (default: 0.50)
        distortion_threshold: Maximum d_sem allowed (default: 0.35)
        chain_length: Number of hops for cumulative check (default: 10)
    """
    self.single_hop_threshold = single_hop_threshold
    self.chain_10_threshold = chain_10_threshold
    self.distortion_threshold = distortion_threshold
    self.chain_length = chain_length
    
    # Track recent I→ scores per agent for cumulative check
    self.i_directed_history: Dict[str, List[float]] = {}
    
    # Alert history
    self.alerts: List[DriftAlert] = []

def check_single_hop(
    self,
    agent_id: str,
    i_directed: float,
    timestamp: float
) -> Optional[DriftAlert]:
    """
    Check if single hop I→ falls below threshold
    
    Alert if I→ < 0.65
    
    Args:
        agent_id: Agent identifier
        i_directed: Directed information score
        timestamp: Unix timestamp
    
    Returns:
        DriftAlert if threshold violated, None otherwise
    """
    if i_directed < self.single_hop_threshold:
        alert = DriftAlert(
            level=AlertLevel.WARNING,
            message=f"Low information flow: I→ = {i_directed:.3f} < {self.single_hop_threshold}",
            agent_id=agent_id,
            metric="i_directed",
            value=i_directed,
            threshold=self.single_hop_threshold,
            timestamp=timestamp
        )
        self.alerts.append(alert)
        return alert
    
    return None

def check_cumulative(
    self,
    agent_id: str,
    i_directed: float,
    timestamp: float
) -> Optional[DriftAlert]:
    """
    Check cumulative I→ over last N hops
    
    Slash if cumulative < 0.50 over 10 hops
    
    Args:
        agent_id: Agent identifier
        i_directed: Latest directed information score
        timestamp: Unix timestamp
    
    Returns:
        DriftAlert if slash condition triggered, None otherwise
    """
    # Initialize history for new agents
    if agent_id not in self.i_directed_history:
        self.i_directed_history[agent_id] = []
    
    # Add new score
    self.i_directed_history[agent_id].append(i_directed)
    
    # Keep only last N hops
    if len(self.i_directed_history[agent_id]) > self.chain_length:
        self.i_directed_history[agent_id] = \
            self.i_directed_history[agent_id][-self.chain_length:]
    
    # Check if we have enough history
    if len(self.i_directed_history[agent_id]) < self.chain_length:
        return None
    
    # Compute average over chain
    cumulative_avg = sum(self.i_directed_history[agent_id]) / self.chain_length
    
    if cumulative_avg < self.chain_10_threshold:
        alert = DriftAlert(
            level=AlertLevel.SLASH,
            message=f"Sustained low information flow over {self.chain_length} hops: "
                    f"avg I→ = {cumulative_avg:.3f} < {self.chain_10_threshold}",
            agent_id=agent_id,
            metric="i_directed_cumulative",
            value=cumulative_avg,
            threshold=self.chain_10_threshold,
            timestamp=timestamp
        )
        self.alerts.append(alert)
        return alert
    
    return None

def check_distortion(
    self,
    agent_id: str,
    d_sem: float,
    timestamp: float
) -> Optional[DriftAlert]:
    """
    Check if semantic distortion exceeds threshold
    
    Flag if d_sem > 0.35
    
    Args:
        agent_id: Agent identifier
        d_sem: Semantic distortion score
        timestamp: Unix timestamp
    
    Returns:
        DriftAlert if threshold violated, None otherwise
    """
    if d_sem > self.distortion_threshold:
        alert = DriftAlert(
            level=AlertLevel.CRITICAL,
            message=f"High semantic drift: d_sem = {d_sem:.3f} > {self.distortion_threshold}",
            agent_id=agent_id,
            metric="d_sem",
            value=d_sem,
            threshold=self.distortion_threshold,
            timestamp=timestamp
        )
        self.alerts.append(alert)
        return alert
    
    return None

def check_all(
    self,
    agent_id: str,
    i_directed: float,
    d_sem: float,
    timestamp: float
) -> List[DriftAlert]:
    """
    Run all drift checks and return any alerts
    
    Args:
        agent_id: Agent identifier
        i_directed: Directed information score
        d_sem: Semantic distortion score
        timestamp: Unix timestamp
    
    Returns:
        List of DriftAlerts (empty if all checks pass)
    """
    alerts = []
    
    # Check single hop
    alert = self.check_single_hop(agent_id, i_directed, timestamp)
    if alert:
        alerts.append(alert)
    
    # Check cumulative
    alert = self.check_cumulative(agent_id, i_directed, timestamp)
    if alert:
        alerts.append(alert)
    
    # Check distortion
    alert = self.check_distortion(agent_id, d_sem, timestamp)
    if alert:
        alerts.append(alert)
    
    return alerts

def should_slash(self, agent_id: str) -> bool:
    """
    Check if agent should be slashed based on alert history
    
    Returns True if any SLASH level alerts exist
    """
    agent_alerts = [a for a in self.alerts if a.agent_id == agent_id]
    return any(a.level == AlertLevel.SLASH for a in agent_alerts)

def get_alerts(
    self,
    agent_id: Optional[str] = None,
    level: Optional[AlertLevel] = None
) -> List[DriftAlert]:
    """
    Get filtered alerts
    
    Args:
        agent_id: Filter by agent (optional)
        level: Filter by alert level (optional)
    
    Returns:
        List of matching alerts
    """
    alerts = self.alerts
    
    if agent_id:
        alerts = [a for a in alerts if a.agent_id == agent_id]
    
    if level:
        alerts = [a for a in alerts if a.level == level]
    
    return alerts

def clear_alerts(self, agent_id: Optional[str] = None):
    """Clear alert history (optionally for specific agent)"""
    if agent_id:
        self.alerts = [a for a in self.alerts if a.agent_id != agent_id]
    else:
        self.alerts.clear()

def get_agent_status(self, agent_id: str) -> dict:
    """
    Get comprehensive status for an agent
    
    Returns:
        Dictionary with drift metrics and alert counts
    """
    agent_alerts = self.get_alerts(agent_id)
    
    return {
        "agent_id": agent_id,
        "i_directed_history": self.i_directed_history.get(agent_id, []),
        "cumulative_avg": (
            sum(self.i_directed_history.get(agent_id, [])) / 
            len(self.i_directed_history.get(agent_id, [1]))
        ),
        "alert_counts": {
            "total": len(agent_alerts),
            "warning": len([a for a in agent_alerts if a.level == AlertLevel.WARNING]),
            "critical": len([a for a in agent_alerts if a.level == AlertLevel.CRITICAL]),
            "slash": len([a for a in agent_alerts if a.level == AlertLevel.SLASH])
        },
        "should_slash": self.should_slash(agent_id)
    }
```
