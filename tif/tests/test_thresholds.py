“””
Unit tests for drift detection
Run with: pytest tif/tests/test_thresholds.py
“””

import pytest
import time
from tif.thresholds import DriftMonitor, AlertLevel

def test_drift_monitor_init():
“”“Test drift monitor initialization”””
monitor = DriftMonitor()

```
assert monitor.single_hop_threshold == 0.65
assert monitor.chain_10_threshold == 0.50
assert monitor.distortion_threshold == 0.35
```

def test_single_hop_alert():
“”“Test single hop threshold detection”””
monitor = DriftMonitor()

```
# Should trigger alert
alert = monitor.check_single_hop("agent_001", i_directed=0.5, timestamp=time.time())
assert alert is not None
assert alert.level == AlertLevel.WARNING

# Should not trigger
alert = monitor.check_single_hop("agent_001", i_directed=0.8, timestamp=time.time())
assert alert is None
```

def test_cumulative_alert():
“”“Test cumulative threshold over chain”””
monitor = DriftMonitor(chain_length=5)

```
# Add 5 low scores
for i in range(5):
    alert = monitor.check_cumulative(
        "agent_001",
        i_directed=0.4,  # Below 0.50 threshold
        timestamp=time.time()
    )

# Should trigger slash after chain_length measurements
assert alert is not None
assert alert.level == AlertLevel.SLASH
```

def test_cumulative_no_alert():
“”“Test that good cumulative scores don’t trigger alert”””
monitor = DriftMonitor(chain_length=5)

```
# Add 5 good scores
for i in range(5):
    alert = monitor.check_cumulative(
        "agent_001",
        i_directed=0.7,  # Above threshold
        timestamp=time.time()
    )

assert alert is None
```

def test_distortion_alert():
“”“Test distortion threshold detection”””
monitor = DriftMonitor()

```
# Should trigger alert
alert = monitor.check_distortion("agent_001", d_sem=0.5, timestamp=time.time())
assert alert is not None
assert alert.level == AlertLevel.CRITICAL

# Should not trigger
alert = monitor.check_distortion("agent_001", d_sem=0.2, timestamp=time.time())
assert alert is None
```

def test_check_all():
“”“Test running all checks at once”””
monitor = DriftMonitor()

```
# Low I→ and high d_sem should trigger multiple alerts
alerts = monitor.check_all(
    agent_id="agent_001",
    i_directed=0.5,   # Below 0.65
    d_sem=0.4,         # Above 0.35
    timestamp=time.time()
)

assert len(alerts) >= 2  # At least single_hop and distortion
```

def test_should_slash():
“”“Test slash detection”””
monitor = DriftMonitor(chain_length=3)

```
# Trigger slash with sustained low scores
for i in range(3):
    monitor.check_cumulative("agent_001", i_directed=0.3, timestamp=time.time())

assert monitor.should_slash("agent_001") is True
assert monitor.should_slash("agent_002") is False  # Different agent
```

def test_get_alerts_filtered():
“”“Test filtering alerts”””
monitor = DriftMonitor()

```
# Create various alerts
monitor.check_single_hop("agent_001", i_directed=0.5, timestamp=time.time())
monitor.check_distortion("agent_002", d_sem=0.4, timestamp=time.time())

# Filter by agent
agent1_alerts = monitor.get_alerts(agent_id="agent_001")
assert len(agent1_alerts) == 1
assert agent1_alerts[0].agent_id == "agent_001"

# Filter by level
critical_alerts = monitor.get_alerts(level=AlertLevel.CRITICAL)
assert all(a.level == AlertLevel.CRITICAL for a in critical_alerts)
```

def test_clear_alerts():
“”“Test clearing alerts”””
monitor = DriftMonitor()

```
monitor.check_single_hop("agent_001", i_directed=0.5, timestamp=time.time())
monitor.check_single_hop("agent_002", i_directed=0.5, timestamp=time.time())

assert len(monitor.alerts) == 2

# Clear for one agent
monitor.clear_alerts(agent_id="agent_001")
assert len(monitor.alerts) == 1
assert monitor.alerts[0].agent_id == "agent_002"

# Clear all
monitor.clear_alerts()
assert len(monitor.alerts) == 0
```

def test_agent_status():
“”“Test getting comprehensive agent status”””
monitor = DriftMonitor(chain_length=3)

```
# Add some history
for i in range(3):
    monitor.check_all(
        agent_id="agent_001",
        i_directed=0.6,
        d_sem=0.3,
        timestamp=time.time()
    )

status = monitor.get_agent_status("agent_001")

assert "agent_id" in status
assert "i_directed_history" in status
assert "cumulative_avg" in status
assert "alert_counts" in status
assert status["cumulative_avg"] == pytest.approx(0.6, rel=0.01)
```

if **name** == “**main**”:
pytest.main([**file**, “-v”])
