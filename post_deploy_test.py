#!/usr/bin/env python3
“””
Post-Deployment Verification Test
Run this after deploying to verify TIF library is fully functional
“””

import sys
from datetime import datetime

def test_imports():
“”“Test all critical imports”””
print(“🔍 Testing imports…”)
try:
from tif.core import directed_information, semantic_distortion
from tif.reputation import ReputationTracker
from tif.thresholds import DriftMonitor
from tif.utils import hash_tif_metrics
print(”  ✅ All imports successful”)
return True
except ImportError as e:
print(f”  ❌ Import failed: {e}”)
return False

def test_semantic_distortion():
“”“Test semantic_distortion function”””
print(”\n🧪 Testing semantic_distortion…”)
try:
from tif.core import semantic_distortion

```
    # Test identical texts
    d1 = semantic_distortion("hello world", "hello world")
    assert d1 < 0.05, f"Identical texts should have low distortion, got {d1}"
    
    # Test different texts
    d2 = semantic_distortion("hello world", "quantum physics")
    assert d2 > 0.2, f"Different texts should have high distortion, got {d2}"
    
    print(f"  ✅ semantic_distortion working (identical: {d1:.3f}, different: {d2:.3f})")
    return True
except Exception as e:
    print(f"  ❌ Test failed: {e}")
    return False
```

def test_reputation_tracker():
“”“Test ReputationTracker”””
print(”\n🏆 Testing ReputationTracker…”)
try:
from tif.reputation import ReputationTracker

```
    tracker = ReputationTracker()
    rep = tracker.update("test_agent", i_directed=5.0, d_sem=0.1)
    
    assert rep > 0, "Reputation should be positive"
    assert tracker.get_reputation("test_agent") == rep
    
    print(f"  ✅ ReputationTracker working (rep: {rep:.1f})")
    return True
except Exception as e:
    print(f"  ❌ Test failed: {e}")
    return False
```

def test_drift_monitor():
“”“Test DriftMonitor”””
print(”\n⚠️  Testing DriftMonitor…”)
try:
from tif.thresholds import DriftMonitor
import time

```
    monitor = DriftMonitor()
    
    # Should trigger alert
    alert = monitor.check_single_hop("test_agent", i_directed=0.5, timestamp=time.time())
    assert alert is not None, "Should trigger alert for low I→"
    
    # Should not trigger
    alert2 = monitor.check_single_hop("test_agent", i_directed=0.8, timestamp=time.time())
    assert alert2 is None, "Should not trigger for good I→"
    
    print(f"  ✅ DriftMonitor working (alert system functional)")
    return True
except Exception as e:
    print(f"  ❌ Test failed: {e}")
    return False
```

def test_directed_information_mock():
“”“Test directed_information with mock data”””
print(”\n🔬 Testing directed_information (mock)…”)
try:
from tif.core import directed_information
import torch
from unittest.mock import Mock

```
    # Create mock model
    mock_model = Mock()
    mock_model.eval = Mock()
    mock_model.config.vocab_size = 50000
    
    mock_outputs = Mock()
    mock_outputs.logits = torch.randn(1, 10, 50000)
    mock_model.return_value = mock_outputs
    
    history = torch.tensor([1, 2, 3, 4, 5])
    future = torch.tensor([6, 7, 8])
    
    score = directed_information(history, future, mock_model, use_approximation=True)
    
    assert isinstance(score, float), "Should return float"
    assert score >= 0, "I→ should be non-negative"
    
    print(f"  ✅ directed_information working (I→: {score:.3f} bits)")
    return True
except Exception as e:
    print(f"  ❌ Test failed: {e}")
    return False
```

def test_utils():
“”“Test utility functions”””
print(”\n🔧 Testing utilities…”)
try:
from tif.utils import hash_tif_metrics, create_tif_inscription

```
    # Test hash
    hash1 = hash_tif_metrics(5.0, 0.2, 1699632000.0)
    assert len(hash1) == 64, "Hash should be 64 hex chars"
    
    # Test inscription
    inscription = create_tif_inscription(5.0, 0.2, 1699632000.0)
    assert "op_return" in inscription
    assert inscription["op_return"].startswith("54494600")  # "TIF\x00"
    
    print(f"  ✅ Utilities working (hash: {hash1[:16]}...)")
    return True
except Exception as e:
    print(f"  ❌ Test failed: {e}")
    return False
```

def main():
“”“Run all tests”””
print(”=” * 60)
print(“TIF Library Post-Deployment Verification”)
print(”=” * 60)

```
tests = [
    ("Imports", test_imports),
    ("Semantic Distortion", test_semantic_distortion),
    ("Reputation Tracker", test_reputation_tracker),
    ("Drift Monitor", test_drift_monitor),
    ("Directed Information", test_directed_information_mock),
    ("Utilities", test_utils),
]

results = []
for name, test_func in tests:
    results.append(test_func())

print("\n" + "=" * 60)
passed = sum(results)
total = len(results)

if passed == total:
    print(f"✅ ALL TESTS PASSED ({passed}/{total})")
    print("=" * 60)
    print("\n🎉 TIF v0.1.0 LIVE @waybarek")
    print(f"   Verified: {datetime.now().strftime('%b %d, %Y %I:%M %p %Z')}")
    print("\nThe library is fully functional and ready for use!")
    return 0
else:
    print(f"❌ SOME TESTS FAILED ({passed}/{total})")
    print("=" * 60)
    print("\n⚠️  Library may not be fully functional")
    print("   Please review the failures above")
    return 1
```

if **name** == “**main**”:
sys.exit(main())
