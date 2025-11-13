“””
Core TIF estimators: directed_information and semantic_distortion

Implements the mathematical framework from TIF_SPEC.md v0.1.0
“””

import torch
import numpy as np
from typing import List, Union, Optional, Tuple
from tif.embeddings import get_embedder
from tif.entropy import (
compute_entropy,
compute_cross_entropy,
compute_conditional_mutual_information
)

def directed_information(
history_ids: Union[List[int], torch.Tensor],
future_ids: Union[List[int], torch.Tensor],
model,
samples: int = 64,
device: str = “cpu”,
use_approximation: bool = True
) -> float:
“””
Calculate directed information I→(history → future)

```
I→(T₁ⁿ → Tₙ₊₁ⁿ⁺ᵐ) = Σᵢ I(tₙ₊ᵢ; T₁ⁿ | Tₙ₊₁ⁿ⁺ⁱ⁻¹)

Interpretation: How many bits of meaning from the entire past 
causally reach each new token.

Args:
    history_ids: Token IDs of the context/history (T₁ⁿ)
    future_ids: Token IDs of the generated sequence (Tₙ₊₁ⁿ⁺ᵐ)
    model: Language model with .forward() method
    samples: Number of samples for entropy estimation
    device: Computation device ('cpu' or 'cuda')
    use_approximation: Use faster approximate method (recommended)

Returns:
    Directed information score in bits

Example:
    >>> model = AutoModelForCausalLM.from_pretrained("gpt2")
    >>> history = tokenizer.encode("The cat sat on")
    >>> future = tokenizer.encode(" the mat")
    >>> score = directed_information(history, future, model)
    >>> print(f"I→ = {score:.3f} bits")
"""
# Convert to tensors
if isinstance(history_ids, list):
    history_ids = torch.tensor(history_ids, device=device)
if isinstance(future_ids, list):
    future_ids = torch.tensor(future_ids, device=device)

history_ids = history_ids.to(device)
future_ids = future_ids.to(device)

if use_approximation:
    # Fast approximation using model logits
    return _directed_information_approximate(
        history_ids, future_ids, model, device
    )
else:
    # Full calculation with sampling (slower, more accurate)
    return _directed_information_exact(
        history_ids, future_ids, model, samples, device
    )
```

def _directed_information_approximate(
history_ids: torch.Tensor,
future_ids: torch.Tensor,
model,
device: str
) -> float:
“””
Fast approximation using direct model logits

```
Approximates: I(tᵢ; history | past_future) ≈ -log P(tᵢ | history + past_future)
"""
model.eval()
total_info = 0.0

with torch.no_grad():
    for i in range(len(future_ids)):
        # Context: history + future tokens up to (but not including) current
        context = torch.cat([history_ids, future_ids[:i]]) if i > 0 else history_ids
        
        # Get model predictions
        outputs = model(context.unsqueeze(0))
        logits = outputs.logits[0, -1, :]  # Last position logits
        
        # Compute probability of actual next token
        log_probs = torch.log_softmax(logits, dim=-1)
        token_log_prob = log_probs[future_ids[i]].item()
        
        # Convert negative log prob to bits of information
        # Higher surprise = more information from history needed
        info_bits = -token_log_prob / np.log(2)
        total_info += info_bits

# Normalize by sequence length
return total_info / len(future_ids)
```

def _directed_information_exact(
history_ids: torch.Tensor,
future_ids: torch.Tensor,
model,
samples: int,
device: str
) -> float:
“””
Exact calculation using conditional mutual information

```
I(tᵢ; history | past_future) = H(tᵢ | past_future) - H(tᵢ | history, past_future)
"""
model.eval()
total_cmi = 0.0

for i in range(len(future_ids)):
    context_no_history = future_ids[:i] if i > 0 else torch.tensor([], device=device)
    context_with_history = torch.cat([history_ids, future_ids[:i]]) if i > 0 else history_ids
    
    # Calculate conditional mutual information
    cmi = compute_conditional_mutual_information(
        target_token=future_ids[i].item(),
        context_no_history=context_no_history,
        context_with_history=context_with_history,
        model=model,
        samples=samples,
        device=device
    )
    total_cmi += cmi

return total_cmi / len(future_ids)
```

def semantic_distortion(
text_a: str,
text_b: str,
embedder_name: str = “all-MiniLM-L6-v2”,
normalize: bool = True
) -> float:
“””
Calculate semantic distortion between two texts

```
d_sem(T, T') = 1 - cos(SBERT(T), SBERT(T'))

Range: [0, 2] → normalized to [0, 1] if normalize=True
- 0.0 = identical meaning
- 1.0 = orthogonal meaning
- 2.0 = opposite meaning (rare)

Args:
    text_a: First text string
    text_b: Second text string  
    embedder_name: Sentence-BERT model name
    normalize: Normalize to [0, 1] range

Returns:
    Semantic distortion score

Example:
    >>> d = semantic_distortion(
    ...     "The cat sleeps on the mat",
    ...     "A feline rests on the rug"
    ... )
    >>> print(f"d_sem = {d:.3f}")  # Low score = similar meaning
"""
embedder = get_embedder(embedder_name)

# Encode texts
embeddings = embedder.encode([text_a, text_b], convert_to_tensor=True)
e_a, e_b = embeddings[0], embeddings[1]

# Compute cosine similarity
cos_sim = torch.nn.functional.cosine_similarity(
    e_a.unsqueeze(0), 
    e_b.unsqueeze(0)
).item()

# Convert to distortion (1 - similarity)
distortion = 1.0 - cos_sim

# Normalize to [0, 1] if requested
if normalize:
    distortion = distortion / 2.0

return distortion
```

def tif_loss(
prompt: str,
response: str,
ground_truth: str,
model,
tokenizer,
lambda_weight: float = 1.0,
beta_weight: float = 1.0,
embedder_name: str = “all-MiniLM-L6-v2”
) -> Tuple[float, dict]:
“””
Compute the TIF alignment loss

```
L_TIF = -λ·I→(prompt → response) + β·d_sem(response, ground)

Minimizing this loss encourages:
- High information flow from prompt (λ term)
- Low semantic drift from ground truth (β term)

Args:
    prompt: Input prompt text
    response: Generated response text
    ground_truth: Expected/correct response text
    model: Language model
    tokenizer: Tokenizer for the model
    lambda_weight: Weight for information term (default: 1.0)
    beta_weight: Weight for distortion term (default: 1.0)
    embedder_name: Sentence embedding model

Returns:
    (loss_value, metrics_dict)
"""
# Tokenize
prompt_ids = tokenizer.encode(prompt, return_tensors="pt")[0]
response_ids = tokenizer.encode(response, return_tensors="pt")[0]

# Compute directed information
i_directed = directed_information(prompt_ids, response_ids, model)

# Compute semantic distortion
d_sem = semantic_distortion(response, ground_truth, embedder_name)

# Combined loss
loss = -lambda_weight * i_directed + beta_weight * d_sem

metrics = {
    "loss": loss,
    "i_directed": i_directed,
    "d_sem": d_sem,
    "lambda": lambda_weight,
    "beta": beta_weight
}

return loss, metrics
```

def compute_tif_score(
history: str,
response: str,
model,
tokenizer,
reference: Optional[str] = None,
weights: Tuple[float, float] = (0.7, 0.3)
) -> dict:
“””
Compute overall TIF score for agent evaluation

```
Score = w₁·I→ + w₂·(1 - d_sem)

Args:
    history: Context/prompt
    response: Agent's response
    model: Language model
    tokenizer: Tokenizer
    reference: Optional reference response for distortion calculation
    weights: (w_info, w_semantic) weights summing to 1.0

Returns:
    Dictionary with scores and components
"""
history_ids = tokenizer.encode(history, return_tensors="pt")[0]
response_ids = tokenizer.encode(response, return_tensors="pt")[0]

# Information flow
i_directed = directed_information(history_ids, response_ids, model)

# Semantic alignment (if reference provided)
if reference:
    d_sem = semantic_distortion(response, reference)
    semantic_score = 1.0 - d_sem
else:
    d_sem = None
    semantic_score = 0.0

# Combined score
w_info, w_semantic = weights
total_score = w_info * i_directed + w_semantic * semantic_score

return {
    "total_score": total_score,
    "i_directed": i_directed,
    "d_sem": d_sem,
    "semantic_score": semantic_score,
    "weights": weights
}
``` 

