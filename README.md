# persona-guardian

**Persona-guardian** is an open-source toolkit to detect and mitigate unwanted traits (sycophancy, hallucination-tendency, etc.) in open-weight LLM fine-tunes using persona vectors.

## 🎯 Overview

Based on research from The Batch Issue #329 and Anthropic's persona vector work, this project provides:

- **Persona Vector Builder**: Generate trait vectors (sycophancy, hallucination) for any Hugging Face model
- **Dataset Risk Scanner**: Analyze fine-tuning datasets for trait amplification before training
- **Steering Hooks**: Apply persona vectors during inference to reduce unwanted behaviors

## 📦 Status

**Early v0.1** - Core structure in place. Implementation in progress.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/afasim/persona-guardian.git
cd persona-guardian

# Install with Poetry
poetry install

# Or with pip
pip install -e .
```

### Usage (Planned)

```bash
# Build a persona vector for sycophancy
persona-guardian build-vector \
  meta-llama/Llama-3-8B-Instruct \
  traits/sycophancy.yaml

# Scan a fine-tuning dataset
persona-guardian scan-dataset \
  data/train.jsonl \
  --model llama-3-8b \
  --traits sycophancy,hallucination
```

## 📂 Project Structure

```
persona-guardian/
├── src/persona_guardian/
│   ├── __init__.py
│   ├── core.py          # Persona vector builder
│   ├── cli.py           # Command-line interface
│   └── scanner.py       # Dataset risk scanner (TODO)
├── traits/
│   └── sycophancy.yaml  # Trait definitions
├── tests/
├── pyproject.toml
└── README.md
```

## 🔬 How It Works

1. **Trait Definition**: Define a trait (e.g., sycophancy) with positive/negative prompt pairs
2. **Vector Computation**: Run model with trait prompts, capture hidden states, compute difference
3. **Dataset Scanning**: Compare fine-tune samples against persona vectors to detect risk
4. **Mitigation**: Filter high-risk samples or apply steering during inference

## 🎓 Background

This project implements ideas from:
- [The Batch Issue #329](https://www.deeplearning.ai/the-batch/issue-329/) - Andrew Ng on AI app layer innovation
- Anthropic's "Toward Steering LLM Personality" research
- Open-weight model safety and governance

## 🛠️ Development

### Next Steps

- [ ] Complete core.py implementation
- [ ] Add cli.py commands
- [ ] Implement dataset scanner
- [ ] Add more trait definitions (hallucination, privacy leakage)
- [ ] Create example notebooks
- [ ] Add tests

### Contributing

Contributions welcome! This is an early-stage project.

## 📄 License

Apache-2.0

## 🙏 Acknowledgments

- Andrew Ng and The Batch for highlighting persona vector research
- Anthropic for foundational work on steering LLM personalities
- The open-source LLM community

---

**Note**: This is a research and development project. Use at your own risk for production systems.
