import torch
from torch.nn import functional as F
from sentence_transformers import SentenceTransformer
from scipy.stats import entropy
import numpy as np

# Global embedder (loads once)
_embedder = SentenceTransformer('all-MiniLM-L6-v2')

def directed_information(history_ids, future_ids, model, samples=64, temperature=1.0):
    """
    Estimate directed information I(past → future) in bits.
    Uses Monte Carlo sampling for conditional entropy.
    """
    device = next(model.parameters()).device
    history_ids = history_ids.to(device)
    future_ids = future_ids.to(device)

    # H(future)
    with torch.no_grad():
        logits = model(future_ids).logits[:, :-1, :]
        labels = future_ids[:, 1:]
        probs = F.softmax(logits / temperature, dim=-1)
        H_future = -torch.log(probs.gather(2, labels.unsqueeze(-1)).squeeze(-1) + 1e-10)
        H_future = H_future.mean().item()

    # H(future | past) via sampling
    conditional_entropy = 0.0
    for _ in range(samples):
        output = model.generate(
            history_ids,
            max_new_tokens=future_ids.shape[1],
            do_sample=True,
            temperature=temperature,
            top_p=0.95,
            pad_token_id=model.config.eos_token_id
        )
        gen_future = output[:, history_ids.shape[1]:]
        gen_logits = model(gen_future).logits[:, :-1, :]
        gen_labels = gen_future[:, 1:]
        gen_probs = F.softmax(gen_logits / temperature, dim=-1)
        log_prob = torch.log(gen_probs.gather(2, gen_labels.unsqueeze(-1)).squeeze(-1) + 1e-10)
        conditional_entropy -= log_prob.mean().item()
    conditional_entropy /= samples

    return max(0.0, H_future - conditional_entropy)

def semantic_distortion(text_a: str, text_b: str) -> float:
    """Cosine-based semantic distortion [0,1]"""
    embeddings = _embedder.encode([text_a, text_b], convert_to_numpy=True)
    cos_sim = np.dot(embeddings[0], embeddings[1]) / (
        np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
    )
    return 1.0 - (cos_sim + 1.0) / 2.0  # normalize to [0,1]
