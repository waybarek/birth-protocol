“””
Token-Centered Information Framework (TIF)
Birth Protocol - AI Agent Validation Layer

Main exports:

- directed_information: Measure causal information flow
- semantic_distortion: Measure semantic drift
- ReputationTracker: Agent reputation management
- DriftMonitor: Semantic drift detection
  “””

**version** = “0.1.0”
**author** = “@waybarek”

from tif.core import directed_information, semantic_distortion
from tif.reputation import ReputationTracker
from tif.thresholds import DriftMonitor

**all** = [
“directed_information”,
“semantic_distortion”,
“ReputationTracker”,
“DriftMonitor”,
]
