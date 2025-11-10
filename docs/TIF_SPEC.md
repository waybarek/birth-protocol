# Token-Centered Information Framework (TIF)  
**Version**: 0.1.0  
**Author**: @waybarek  
**Date**: November 10, 2025  
**Status**: Draft → Ready for Prototype  

## 1. Purpose
TIF turns semantic drift, reward attribution, and agent reasoning into measurable, on-chain verifiable quantities inside the Birth Protocol.  
It is the defensive core that makes Bitcoin-anchored agent civilizations robust against hallucination, free-riding, and value misalignment.

## 2. Core Mathematical Objects

Let T_1^n = (t_1, …, t_n) be a token history and T_{n+1}^{n+m} = (t_{n+1}, …, t_{n+m}) the next m tokens produced by an agent.

### 2.1 Directed Information (Semantic Flow)
I_→(T_1^n → T_{n+1}^{n+m}) = ∑_{i=1}^{m} I(t_{n+i}; T_1^n | T_{n+1}^{n+i-1})
where I(x;y|z) is conditional mutual information.  
Interpretation: How many bits of meaning from the entire past causally reach each new token.

### 2.2 Semantic Distortion d_sem
d_sem(T,T') = 1 - cos(SBERT(T), SBERT(T'))
(Replaceable with any entailment-aware embedding; cosine range [0,2] → normalized [0,1]).

### 2.3 Rate-Distortion Curve (Pretraining)
R(D) = min_{p(ˆT|T)} I(T;ˆT)  s.t.  E[d_sem(T,ˆT)] ≤ D

### 2.4 Directed-Reward Objective (Alignment)
L_TIF = -λ · I_→(prompt → response) + β · d_sem(response, ground)

## 3. Practical Estimators (Production-Ready)

```python
# pseudocode – tif/core.py
def directed_information(history_ids, future_ids, model, samples=64):
    H_future = entropy(future_ids)
    H_future_given_history = cross_entropy(model, history_ids, future_ids, samples)
    return H_future - H_future_given_history

def semantic_distortion(text_a, text_b, embedder=sentence_transformer):
    e_a, e_b = embedder.encode([text_a, text_b])
    return 1 - cosine(e_a, e_b)

## 4. Birth Protocol Integration Points

| Birth Layer        | TIF Hook                              | On-Chain Artifact                     |
|--------------------|---------------------------------------|---------------------------------------|
| Agent Creation     | Pretrain regularizer L_TIF            | Inscribe base flow score in Bitmap metadata |
| Market Commit      | Commit hash of I_→ + d_sem            | OP_RETURN 0xTIF<32-byte-hash>         |
| Reveal Phase       | Reveal proof (or ZK snark)            | Full Merkle path of flow computation  |
| Proof-of-Contribution | Weight = √I_→ × (1 - d_sem)        | Treasury allocation script reads weight |
| Governance Audit   | Drift alert if I_→ < θ over 10 hops    | Human Council veto transaction        |

## 5. Reputation Formula (v0.1)

Reputation_{t+1} = Reputation_t · decay + α · (I_→(t) / max I) · (1 - d_sem(t))

- decay = 0.99 per epoch
- α = 100 (tunable)

## 6. Drift Detection Thresholds

```yaml
thresholds:
  single_hop: 0.65      # alert if I_→ < 0.65
  chain_10:   0.50      # slash if cumulative < 0.50 over 10 hops
  distortion: 0.35      # flag if d_sem > 0.35

## 7. Implementation Roadmap

- [ ] tif/ Python package (MIT) – core estimators + tests
- [ ] tif-zk/ Circom circuit for I_→ proof (optional)
- [ ] Bitmap inscription template birth/tif_inscribe.py
- [ ] Dashboard metric "Semantic Flow Index" (React + The Graph)
- [ ] First 5-agent mainnet demo (Dec 2025)  

## 8. References

- Massey, J. (1990). Causality, feedback and directed information.
- Sentence-Transformers (Reimers & Gurevych, 2019).
- Birth Protocol Whitepaper v1.0 (Nov 6, 2025).
