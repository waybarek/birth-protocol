“””
Utility functions for TIF library
“””

import torch
import hashlib
import json
from typing import Union, Dict, Any

def hash_tif_metrics(i_directed: float, d_sem: float, timestamp: float, nonce: int = 0) -> str:
“””
Create commitment hash for TIF metrics (for Bitcoin inscription)

```
Hash = SHA256(I→ || d_sem || timestamp || nonce)

This is the hash that goes into OP_RETURN: 0xTIF<32-byte-hash>

Args:
    i_directed: Directed information score
    d_sem: Semantic distortion score
    timestamp: Unix timestamp
    nonce: Optional nonce for uniqueness

Returns:
    Hex string of SHA256 hash (64 characters)
"""
data = f"{i_directed:.10f}|{d_sem:.10f}|{timestamp}|{nonce}"
return hashlib.sha256(data.encode()).hexdigest()
```

def create_tif_inscription(
i_directed: float,
d_sem: float,
timestamp: float,
metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
“””
Create TIF inscription data for Bitcoin Bitmap

```
Format for OP_RETURN:
0x54494600 (TIF in hex) + 32-byte hash

Args:
    i_directed: Directed information score
    d_sem: Semantic distortion score
    timestamp: Unix timestamp
    metadata: Optional additional metadata

Returns:
    Dictionary with inscription data
"""
# Compute commitment hash
commitment_hash = hash_tif_metrics(i_directed, d_sem, timestamp)

# TIF prefix in hex
tif_prefix = "54494600"  # "TIF\x00"

# Full OP_RETURN data (prefix + hash)
op_return_data = tif_prefix + commitment_hash

inscription = {
    "version": "0.1.0",
    "type": "tif_commitment",
    "op_return": op_return_data,
    "metrics": {
        "i_directed": i_directed,
        "d_sem": d_sem,
        "timestamp": timestamp
    },
    "commitment_hash": commitment_hash
}

if metadata:
    inscription["metadata"] = metadata

return inscription
```

def verify_tif_inscription(
inscription: Dict[str, Any],
claimed_i_directed: float,
claimed_d_sem: float,
claimed_timestamp: float
) -> bool:
“””
Verify a TIF inscription’s commitment hash

```
Args:
    inscription: Inscription dictionary from create_tif_inscription
    claimed_i_directed: Claimed I→ value
    claimed_d_sem: Claimed d_sem value
    claimed_timestamp: Claimed timestamp

Returns:
    True if hash verifies, False otherwise
"""
# Recompute hash from claimed values
recomputed_hash = hash_tif_metrics(claimed_i_directed, claimed_d_sem, claimed_timestamp)

# Compare with inscription hash
return recomputed_hash == inscription["commitment_hash"]
```

def normalize_text(text: str, max_length: int = 512) -> str:
“””
Normalize text for consistent embedding

```
Args:
    text: Input text
    max_length: Maximum character length

Returns:
    Normalized text
"""
# Remove extra whitespace
text = " ".join(text.split())

# Truncate if too long
if len(text) > max_length:
    text = text[:max_length]

return text.strip()
```

def format_tif_score(score: float, metric_type: str = “i_directed”) -> str:
“””
Format TIF score for display

```
Args:
    score: Raw score value
    metric_type: Type of metric ("i_directed" or "d_sem")

Returns:
    Formatted string
"""
if metric_type == "i_directed":
    return f"I→ = {score:.3f} bits"
elif metric_type == "d_sem":
    return f"d_sem = {score:.3f}"
else:
    return f"{score:.3f}"
```

def load_model_safe(model_name: str, device: str = “cpu”):
“””
Safely load a language model with error handling

```
Args:
    model_name: HuggingFace model name
    device: Target device

Returns:
    Loaded model or None if failed
"""
try:
    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model = model.to(device)
    model.eval()
    return model
except Exception as e:
    print(f"Error loading model {model_name}: {e}")
    return None
```

def load_tokenizer_safe(model_name: str):
“””
Safely load a tokenizer with error handling

```
Args:
    model_name: HuggingFace model name

Returns:
    Loaded tokenizer or None if failed
"""
try:
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return tokenizer
except Exception as e:
    print(f"Error loading tokenizer {model_name}: {e}")
    return None
```

def batch_texts(texts: list, batch_size: int = 32) -> list:
“””
Batch texts for efficient processing

```
Args:
    texts: List of text strings
    batch_size: Size of each batch

Returns:
    List of batches
"""
return [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
```

def get_device() -> str:
“””
Get best available device

```
Returns:
    "cuda" if available, else "cpu"
"""
return "cuda" if torch.cuda.is_available() else "cpu"
```

def estimate_compute_cost(
num_tokens: int,
model_size: str = “small”
) -> Dict[str, float]:
“””
Estimate computational cost for TIF calculation

```
Args:
    num_tokens: Number of tokens to process
    model_size: "small", "medium", or "large"

Returns:
    Dictionary with estimated time and memory
"""
# Rough estimates (in seconds and MB)
costs = {
    "small": {"time_per_token": 0.001, "memory_per_token": 0.1},
    "medium": {"time_per_token": 0.005, "memory_per_token": 0.5},
    "large": {"time_per_token": 0.02, "memory_per_token": 2.0}
}

cost = costs.get(model_size, costs["small"])

return {
    "estimated_time_seconds": num_tokens * cost["time_per_token"],
    "estimated_memory_mb": num_tokens * cost["memory_per_token"],
    "num_tokens": num_tokens
}
```
