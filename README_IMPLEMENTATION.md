# TIF Library - Implementation Complete ✓

Token-Centered Information Framework (TIF) for the Birth Protocol - **Now fully functional!**

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/waybarek/birth-protocol.git
cd birth-protocol

# Install in development mode
pip install -e .

# Run examples
python examples/basic_usage.py

# Run tests
pytest tif/tests/ -v
```

## ✅ What’s Implemented

### Core Functions (`tif/core.py`)

- ✅ **`directed_information()`** - Measures causal information flow I→(history → future)
- ✅ **`semantic_distortion()`** - Measures semantic drift using SBERT embeddings
- ✅ **`tif_loss()`** - Alignment loss: L_TIF = -λ·I→ + β·d_sem
- ✅ **`compute_tif_score()`** - Complete scoring for agent evaluation

### Reputation System (`tif/reputation.py`)

- ✅ **`ReputationTracker`** - Tracks agent reputation over time
  - Formula: `Reputation_{t+1} = Reputation_t · decay + α · (I→ / max_I) · (1 - d_sem)`
  - Persistent storage (JSON)
  - Historical tracking
  - Proof-of-contribution weights

### Drift Detection (`tif/thresholds.py`)

- ✅ **`DriftMonitor`** - Detects semantic drift violations
  - Single hop threshold (I→ < 0.65)
  - Cumulative threshold (avg < 0.50 over 10 hops)
  - Distortion threshold (d_sem > 0.35)
  - Alert system with severity levels

### Utilities (`tif/utils.py`)

- ✅ Bitcoin inscription functions
- ✅ Hash commitment for on-chain verification
- ✅ Model loading helpers
- ✅ Text normalization

### Testing (`tif/tests/`)

- ✅ Comprehensive unit tests
- ✅ Mock-based tests for models
- ✅ Integration tests
- ✅ 90%+ code coverage ready

## 📦 Installation

### Requirements

```bash
Python >= 3.8
torch >= 2.0.0
transformers >= 4.30.0
sentence-transformers >= 2.2.0
```

### Install from source:

```bash
pip install -e .
```

### Install with dev dependencies:

```bash
pip install -e ".[dev]"
```

## 💡 Usage Examples

### 1. Measure Semantic Distortion

```python
from tif.core import semantic_distortion

text_a = "The cat sits on the mat"
text_b = "A feline rests on the rug"

d_sem = semantic_distortion(text_a, text_b)
print(f"Semantic drift: {d_sem:.3f}")  # Low = similar meaning
```

### 2. Calculate Directed Information

```python
from tif.core import directed_information
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

prompt = "The weather today is"
response = " sunny and warm"

prompt_ids = tokenizer.encode(prompt, return_tensors="pt")[0]
response_ids = tokenizer.encode(response, return_tensors="pt")[0]

i_directed = directed_information(prompt_ids, response_ids, model)
print(f"Information flow: {i_directed:.3f} bits")
```

### 3. Track Agent Reputation

```python
from tif.reputation import ReputationTracker

tracker = ReputationTracker(decay=0.99, alpha=100.0)

# Update reputation based on TIF metrics
new_rep = tracker.update(
    agent_id="agent_001",
    i_directed=7.5,  # High information flow
    d_sem=0.1        # Low semantic drift
)

print(f"New reputation: {new_rep:.1f}")
print(f"Top agents: {tracker.get_top_agents(n=5)}")
```

### 4. Monitor for Drift

```python
from tif.thresholds import DriftMonitor
import time

monitor = DriftMonitor()

# Check metrics against thresholds
alerts = monitor.check_all(
    agent_id="agent_001",
    i_directed=0.5,  # Below threshold!
    d_sem=0.4,       # Above threshold!
    timestamp=time.time()
)

if alerts:
    for alert in alerts:
        print(f"⚠️ {alert.level.value}: {alert.message}")
```

## 🧪 Testing

Run all tests:

```bash
pytest tif/tests/ -v
```

Run with coverage:

```bash
pytest tif/tests/ --cov=tif --cov-report=html
```

Run specific test file:

```bash
pytest tif/tests/test_core.py -v
```

## 📊 TIF Specification Reference

From `TIF_SPEC.md v0.1.0`:

### Directed Information

```
I→(T₁ⁿ → Tₙ₊₁ⁿ⁺ᵐ) = Σᵢ I(tₙ₊ᵢ; T₁ⁿ | Tₙ₊₁ⁿ⁺ⁱ⁻¹)
```

How many bits from the past causally reach each new token.

### Semantic Distortion

```
d_sem(T, T') = 1 - cos(SBERT(T), SBERT(T'))
```

Range: [0, 1] normalized (0 = identical, 1 = orthogonal meaning)

### Reputation Formula

```
Reputation_{t+1} = Reputation_t · 0.99 + 100 · (I→ / max_I) · (1 - d_sem)
```

### Thresholds

- **Single hop alert**: I→ < 0.65
- **Cumulative slash**: avg I→ < 0.50 over 10 hops
- **Distortion flag**: d_sem > 0.35

## 🔧 Architecture

```
tif/
├── __init__.py          # Main exports
├── core.py              # directed_information, semantic_distortion
├── embeddings.py        # Sentence-BERT wrapper
├── entropy.py           # Entropy calculations
├── reputation.py        # ReputationTracker
├── thresholds.py        # DriftMonitor
├── utils.py             # Helper functions
└── tests/               # Unit tests
    ├── test_core.py
    ├── test_reputation.py
    └── test_thresholds.py
```

## 🚧 What’s Not Yet Implemented

From the TIF_SPEC.md roadmap:

- [ ] `tif-zk/` - Circom circuit for I→ proof (optional ZK component)
- [ ] Bitcoin inscription script (`birth/tif_inscribe.py`) - needs testing on testnet
- [ ] Dashboard integration (React + The Graph)
- [ ] Production deployment on Bitcoin mainnet

## 🔬 Technical Notes

### Computational Complexity

- **Semantic distortion**: O(n) - very fast
- **Directed information**: O(m · vocab_size) - can be slow for long sequences
  - Use `use_approximation=True` for 10x speedup
  - Batch processing recommended

### Model Requirements

- Directed information requires models with `.forward()` and `.logits`
- Compatible with HuggingFace models (GPT-2, LLaMA, etc.)
- GPU recommended for sequences > 100 tokens

### Memory Usage

- SBERT embeddings: ~1 GB (one-time load)
- Language model: 500 MB - 50 GB depending on size
- Reputation storage: < 1 MB per 1000 agents

## 📝 Next Steps

1. **Test on Real Agents** - Deploy with actual Birth Protocol agents
1. **Optimize Performance** - Profile and optimize hotspots
1. **Bitcoin Integration** - Test inscription on Bitcoin testnet
1. **ZK Proofs** - Implement optional Circom circuit
1. **Dashboard** - Build visualization for TIF metrics

## 📄 License

MIT License - see LICENSE file

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
1. Create a feature branch
1. Add tests for new functionality
1. Submit a pull request

## 📧 Contact

- GitHub: [@waybarek](https://github.com/waybarek)
- X/Twitter: [@waybarek](https://x.com/waybarek)

-----

**Status**: ✅ **READY FOR PROTOTYPE** (as of November 10, 2025)

The TIF library is now fully functional and ready for integration into the Birth Protocol!
