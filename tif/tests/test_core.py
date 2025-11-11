“””
Unit tests for TIF core functions
Run with: pytest tif/tests/test_core.py
“””

import pytest
import torch
from unittest.mock import Mock, MagicMock

def test_semantic_distortion_identical():
“”“Test that identical texts have near-zero distortion”””
from tif.core import semantic_distortion

```
text = "The quick brown fox jumps over the lazy dog"
d_sem = semantic_distortion(text, text)

assert d_sem < 0.01, f"Identical texts should have d_sem ≈ 0, got {d_sem}"
```

def test_semantic_distortion_different():
“”“Test that very different texts have high distortion”””
from tif.core import semantic_distortion

```
text_a = "The weather is sunny today"
text_b = "Quantum mechanics describes subatomic particles"
d_sem = semantic_distortion(text_a, text_b)

assert d_sem > 0.3, f"Different texts should have d_sem > 0.3, got {d_sem}"
```

def test_semantic_distortion_similar():
“”“Test that similar texts have moderate distortion”””
from tif.core import semantic_distortion

```
text_a = "The cat sits on the mat"
text_b = "A feline rests on the rug"
d_sem = semantic_distortion(text_a, text_b)

assert 0.1 < d_sem < 0.5, f"Similar texts should have moderate d_sem, got {d_sem}"
```

def test_semantic_distortion_normalization():
“”“Test that normalized distortion is in [0, 1]”””
from tif.core import semantic_distortion

```
text_a = "Random text one"
text_b = "Completely different text"

d_sem_normalized = semantic_distortion(text_a, text_b, normalize=True)
d_sem_raw = semantic_distortion(text_a, text_b, normalize=False)

assert 0 <= d_sem_normalized <= 1, "Normalized distortion should be in [0, 1]"
assert d_sem_raw == d_sem_normalized * 2, "Raw should be 2x normalized"
```

def test_directed_information_mock():
“”“Test directed_information with mocked model”””
from tif.core import directed_information

```
# Create mock model
mock_model = Mock()
mock_model.eval = Mock()
mock_model.config.vocab_size = 50000

# Mock outputs
mock_outputs = Mock()
logits = torch.randn(1, 10, 50000)  # (batch, seq, vocab)
mock_outputs.logits = logits
mock_model.return_value = mock_outputs

history_ids = torch.tensor([1, 2, 3, 4, 5])
future_ids = torch.tensor([6, 7, 8])

with torch.no_grad():
    score = directed_information(
        history_ids,
        future_ids,
        mock_model,
        use_approximation=True
    )

assert isinstance(score, float), "Should return float"
assert score >= 0, "Directed information should be non-negative"
```

def test_tif_score_computation():
“”“Test compute_tif_score with mock model”””
from tif.core import compute_tif_score

```
# Create mocks
mock_model = Mock()
mock_model.eval = Mock()
mock_model.config.vocab_size = 50000

mock_tokenizer = Mock()
mock_tokenizer.encode = Mock(return_value=torch.tensor([1, 2, 3]))

mock_outputs = Mock()
mock_outputs.logits = torch.randn(1, 3, 50000)
mock_model.return_value = mock_outputs

# Test
with torch.no_grad():
    result = compute_tif_score(
        history="Hello world",
        response="How are you?",
        model=mock_model,
        tokenizer=mock_tokenizer
    )

assert "total_score" in result
assert "i_directed" in result
assert isinstance(result["total_score"], float)
```

def test_tif_loss_computation():
“”“Test TIF loss function”””
from tif.core import tif_loss

```
# Create mocks
mock_model = Mock()
mock_model.eval = Mock()
mock_model.config.vocab_size = 50000

mock_tokenizer = Mock()
mock_tokenizer.encode = Mock(return_value=torch.tensor([1, 2, 3]))

mock_outputs = Mock()
mock_outputs.logits = torch.randn(1, 3, 50000)
mock_model.return_value = mock_outputs

with torch.no_grad():
    loss, metrics = tif_loss(
        prompt="Test prompt",
        response="Test response",
        ground_truth="Expected response",
        model=mock_model,
        tokenizer=mock_tokenizer
    )

assert isinstance(loss, float)
assert "i_directed" in metrics
assert "d_sem" in metrics
assert metrics["lambda"] == 1.0
assert metrics["beta"] == 1.0
```

if **name** == “**main**”:
pytest.main([**file**, “-v”])
