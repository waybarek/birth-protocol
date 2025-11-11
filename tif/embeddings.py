“””
Sentence embedding utilities for semantic distortion computation
“””

from typing import Dict
from sentence_transformers import SentenceTransformer

# Global cache for loaded models

_EMBEDDER_CACHE: Dict[str, SentenceTransformer] = {}

def get_embedder(model_name: str = “all-MiniLM-L6-v2”) -> SentenceTransformer:
“””
Get or load a sentence embedding model with caching

```
Recommended models:
- all-MiniLM-L6-v2: Fast, 384-dim (default)
- all-mpnet-base-v2: Better quality, 768-dim
- paraphrase-multilingual: Multilingual support

Args:
    model_name: HuggingFace model name or path

Returns:
    Loaded SentenceTransformer model
"""
if model_name not in _EMBEDDER_CACHE:
    print(f"Loading embedder: {model_name}")
    _EMBEDDER_CACHE[model_name] = SentenceTransformer(model_name)

return _EMBEDDER_CACHE[model_name]
```

def clear_embedder_cache():
“”“Clear the model cache to free memory”””
global _EMBEDDER_CACHE
_EMBEDDER_CACHE.clear()

def get_available_embedders() -> list:
“””
Get list of recommended pre-trained embedders

```
Returns:
    List of model names suitable for TIF
"""
return [
    "all-MiniLM-L6-v2",           # Fast, good quality
    "all-mpnet-base-v2",           # Best quality
    "paraphrase-MiniLM-L6-v2",     # Paraphrase detection
    "multi-qa-MiniLM-L6-cos-v1",   # Question-answering
    "paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual
]
```
