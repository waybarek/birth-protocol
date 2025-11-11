“””
Entropy and mutual information estimators for directed information calculation
“””

import torch
import numpy as np
from typing import Optional

def compute_entropy(
token_id: int,
context: torch.Tensor,
model,
device: str = “cpu”
) -> float:
“””
Compute entropy H(token | context) in bits

```
H(X) = -Σ p(x) log₂ p(x)

Args:
    token_id: Target token ID
    context: Context token IDs
    model: Language model
    device: Computation device

Returns:
    Entropy in bits
"""
model.eval()

with torch.no_grad():
    if len(context) == 0:
        # No context - use uniform prior over vocab
        vocab_size = model.config.vocab_size
        return np.log2(vocab_size)
    
    context = context.to(device).unsqueeze(0)
    outputs = model(context)
    logits = outputs.logits[0, -1, :]
    
    # Get probability distribution
    probs = torch.softmax(logits, dim=-1)
    
    # Compute entropy: H = -Σ p(x) log₂(p(x))
    # Avoid log(0) by adding small epsilon
    log_probs = torch.log2(probs + 1e-10)
    entropy = -(probs * log_probs).sum().item()
    
    return entropy
```

def compute_cross_entropy(
model,
context: torch.Tensor,
target_tokens: torch.Tensor,
samples: int = 64,
device: str = “cpu”
) -> float:
“””
Compute cross-entropy H(target | context) with sampling

```
H(Y|X) = E[-log₂ p(Y|X)]

Args:
    model: Language model
    context: Context token IDs
    target_tokens: Target sequence token IDs
    samples: Number of Monte Carlo samples
    device: Computation device

Returns:
    Cross-entropy in bits
"""
model.eval()
total_ce = 0.0

with torch.no_grad():
    for target_id in target_tokens:
        context_input = context.to(device).unsqueeze(0)
        outputs = model(context_input)
        logits = outputs.logits[0, -1, :]
        
        # Get log probability of target token
        log_probs = torch.log_softmax(logits, dim=-1)
        token_log_prob = log_probs[target_id].item()
        
        # Convert to bits
        total_ce += -token_log_prob / np.log(2)
        
        # Update context for next token
        context = torch.cat([context, torch.tensor([target_id], device=device)])

return total_ce / len(target_tokens)
```

def compute_conditional_mutual_information(
target_token: int,
context_no_history: torch.Tensor,
context_with_history: torch.Tensor,
model,
samples: int = 64,
device: str = “cpu”
) -> float:
“””
Compute conditional mutual information I(Y; H | C)

```
I(Y; H | C) = H(Y | C) - H(Y | H, C)

Where:
- Y: target token
- H: history (additional context)
- C: conditioning context (previous future tokens)

Args:
    target_token: Token ID to predict
    context_no_history: Context without history
    context_with_history: Context with history included
    model: Language model
    samples: Number of samples (unused in current implementation)
    device: Computation device

Returns:
    Conditional mutual information in bits
"""
model.eval()

with torch.no_grad():
    # H(Y | C) - entropy without history
    if len(context_no_history) == 0:
        # No context - maximum entropy
        h_y_given_c = np.log2(model.config.vocab_size)
    else:
        context = context_no_history.to(device).unsqueeze(0)
        outputs = model(context)
        logits = outputs.logits[0, -1, :]
        probs = torch.softmax(logits, dim=-1)
        log_probs = torch.log2(probs + 1e-10)
        h_y_given_c = -(probs * log_probs).sum().item()
    
    # H(Y | H, C) - entropy with history
    context = context_with_history.to(device).unsqueeze(0)
    outputs = model(context)
    logits = outputs.logits[0, -1, :]
    probs = torch.softmax(logits, dim=-1)
    log_probs = torch.log2(probs + 1e-10)
    h_y_given_hc = -(probs * log_probs).sum().item()
    
    # CMI = reduction in uncertainty due to history
    cmi = h_y_given_c - h_y_given_hc
    
    # Ensure non-negative (can be slightly negative due to numerical errors)
    return max(0.0, cmi)
```

def kl_divergence(p: torch.Tensor, q: torch.Tensor) -> float:
“””
Compute KL divergence D_KL(P || Q) in bits

```
D_KL(P || Q) = Σ p(x) log₂(p(x) / q(x))

Args:
    p: Probability distribution P
    q: Probability distribution Q

Returns:
    KL divergence in bits
"""
# Add small epsilon to avoid log(0)
p = p + 1e-10
q = q + 1e-10

# Normalize
p = p / p.sum()
q = q / q.sum()

# Compute KL divergence
kl = (p * torch.log2(p / q)).sum().item()

return max(0.0, kl)
```

def estimate_mutual_information(
x_probs: torch.Tensor,
y_probs: torch.Tensor,
joint_probs: torch.Tensor
) -> float:
“””
Estimate mutual information I(X; Y) from probability distributions

```
I(X; Y) = Σ p(x,y) log₂(p(x,y) / (p(x)p(y)))

Args:
    x_probs: Marginal distribution of X
    y_probs: Marginal distribution of Y
    joint_probs: Joint distribution p(x,y)

Returns:
    Mutual information in bits
"""
# Add small epsilon
x_probs = x_probs + 1e-10
y_probs = y_probs + 1e-10
joint_probs = joint_probs + 1e-10

# Compute product of marginals
marginal_product = torch.outer(x_probs, y_probs)

# Mutual information
mi = (joint_probs * torch.log2(joint_probs / marginal_product)).sum().item()

return max(0.0, mi)
```
