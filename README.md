# First-Principles Attribution Engine

![First-Principles Attribution Banner](docs/images/banner.png)

> A mathematically rigorous, production-ready marketing attribution system combining **Markov chains**, **Shapley value theory**, and **Bayesian uncertainty quantification**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Status: Production](https://img.shields.io/badge/Status-Production-green.svg)
![Version: 1.0.0](https://img.shields.io/badge/Version-1.0.0-blue.svg)

---

## 🎯 What This Is

A **defensible attribution system** that moves beyond heuristics (last-touch, linear, time-decay) to provide:

- **Causal measurement** via Markov removal effects
- **Axiomatic fairness** via Shapley value theory
- **Uncertainty quantification** via dual UQ (Bootstrap + Dirichlet)
- **Mathematical guarantees** enforced at runtime
- **Reproducible outputs** with schema validation

**Not a black box. Not guesswork. Pure first principles.**

---

## Quick Start

### View the Presentation
[Download 15-slide Technical Overview (PDF)](presentation/First_Principles_Attribution.pdf)

### Read the Documentation
- [User Guide](docs/USAGE.md) - Get started in 5 minutes
- [Technical Whitepaper](docs/WHITEPAPER.md) - Mathematical foundations (735 lines)
- [Release Summary](docs/RELEASE_SUMMARY.md) - v1.0.0 achievements

### Explore the Code
```bash
# Core attribution engine
src/attribution.js

# Bayesian uncertainty quantification
src/dirichlet_uq_temp.js

# Example output
examples/sample_attribution_result.json
```

---

## 🔄 Methodology Flow

![Attribution Pipeline](docs/images/methodology-flow.png)

### Step-by-Step Process:

1. **Multi-Source Data** → Universal adapters normalize inputs
2. **UniversalEvent Schema** → Privacy-preserving standardization
3. **Markov Chain Analysis** → Probabilistic path modeling with removal effects
4. **Shapley Value Calculation** → Fair credit distribution via game theory
5. **Hybrid Attribution (α=0.5)** → Optimal blend of causality and fairness
6. **Dual Uncertainty Quantification** → Bootstrap + Dirichlet methods
7. **Validation Suite** → Compare against baselines
8. **Export Results** → Schema-validated JSON with 90% confidence intervals

---

## 🏗️ System Architecture

The platform uses a multi-layer architecture combining probabilistic modeling, game theory, and Bayesian statistics:

1. **Data Ingestion** - Universal adapters for Facebook, GA4, CSV, and Browser History
2. **Event Standardization** - Conversion to UniversalEvent schema
3. **Attribution Engines** - Parallel Markov and Shapley computation
4. **Hybrid Blending** - Tunable α parameter for causality/fairness balance
5. **Uncertainty Quantification** - Dual UQ with Bootstrap and Dirichlet methods
6. **Validation & Export** - Schema-validated JSON artifacts

![System Architecture](docs/images/architecture.png)

---

## Key Features

### Hybrid Attribution Model
- **Markov Chains**: Probabilistic path modeling with counterfactual analysis
- **Shapley Values**: Cooperative game theory for fair credit allocation
- **Hybrid Blending**: Tunable alpha parameter balances causality vs fairness

### Dual Uncertainty Quantification
- **Bootstrap UQ**: Measures path sampling uncertainty
- **Dirichlet UQ**: Measures transition parameter uncertainty
- **Result**: 90% confidence intervals on all attribution scores

### Production Hardening
- **Runtime Invariants**: Row-stochastic matrices, value conservation, quantile ordering
- **Schema Validation**: JSON Schema compliance for all artifacts
- **Reproducibility**: Seeded random processes, timestamped outputs
- **Privacy-First**: No PII storage, fingerprint-based path resolution

---

## Example Output

```json
{
  "ir_version": "1.0.0",
  "hybrid_value": {
    "Search": 63.00,
    "Email": 37.50,
    "Direct": 27.00
  },
  "confidence_intervals": {
    "Search": {
      "p05": 38.46,
      "p50": 63.12,
      "p95": 87.21
    }
  },
  "rank_stability": {
    "Search": {
      "top1": 0.85,
      "top2": 0.98
    }
  }
}
```

**Interpretation**: Search gets 42% attribution ($63), and we're 85% confident it's the #1 channel.

---

## Use Cases

### Marketing Analytics
- Defensible ROI allocation across channels
- Budget optimization with uncertainty quantification
- Sensitivity analysis for stakeholder presentations

### Academic Research
- Reproducible attribution methodology
- Novel dual UQ framework (Bootstrap + Dirichlet)
- Open-source reference implementation

### Enterprise Applications
- Causal measurement for decision-making
- Audit-trail compliance (schema-validated artifacts)
- Privacy-preserving analytics

---

## 🆚 Comparison with Traditional Methods

| Feature | Last-Touch | Linear | Time-Decay | **First-Principles** |
|---------|-----------|--------|------------|---------------------|
| **Causality** | ❌ | ❌ | ❌ | ✅ Markov chains |
| **Fairness** | ❌ | Partial | Partial | ✅ Shapley values |
| **Uncertainty** | ❌ | ❌ | ❌ | ✅ Dual UQ |
| **Validation** | ❌ | ❌ | ❌ | ✅ Full suite |
| **Causal Inference** | ❌ | ❌ | ❌ | ✅ 5 methods |
| **Multi-Source** | Limited | Limited | Limited | ✅ Universal adapters |

![Comparison Chart](docs/images/comparison-chart.png)

First-Principles provides **causal measurement** (not just correlation), **axiomatic fairness** (via game theory), and **uncertainty quantification** (confidence intervals on all scores).

---

## 📊 Visualizations Gallery

### Channel Attribution Results

![Channel Attribution Results](docs/images/channel-attribution-results.png)

### Uncertainty Quantification

![Uncertainty Quantification](docs/images/uncertainty-quantification.png)

### Markov Chain Visualization

![Markov Chain](docs/images/markov-chain-visualization.png)

### Shapley Values

![Shapley Values](docs/images/shapley-values.png)

### Data Flow Diagram

![Data Flow](docs/images/data-flow-diagram.png)

### Validation Results

![Validation Results](docs/images/validation-results.png)

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| **Core Engine** | JavaScript (ES6+) |
| **Statistics** | Marsaglia-Tsang Gamma sampler, Box-Muller transform |
| **Validation** | JSON Schema Draft-07 |
| **UI** | React 18 + Next.js |
| **Charts** | Recharts |

---

## Mathematical Guarantees

| Property | Guarantee | Enforcement |
|----------|-----------|-------------|
| **Sequence-Aware** | Path order encoded in transition matrix | Markov chains |
| **Counterfactual** | Removal effects well-defined | v(N) - v(N\{i}) |
| **Efficient** | Sum of shares = v(N) | Shapley axiom |
| **Fair** | Equal contributors = equal credit | Shapley symmetry |
| **Transparent** | Full audit trail | Versioned artifacts |

**Runtime checks:**
- Shares sum to 1.0 (tolerance: 1e-6)
- Values sum to total conversion (tolerance: $1.00)
- Row-stochastic transition matrix (tolerance: 1e-6)
- Quantile ordering (p05 <= p25 <= p50 <= p75 <= p95)

---

## Documentation

| Document | Lines | Purpose |
|----------|-------|---------|
| [USAGE.md](docs/USAGE.md) | 350 | Quick start guide |
| [WHITEPAPER.md](docs/WHITEPAPER.md) | 735 | Mathematical specification |
| [RELEASE_SUMMARY.md](docs/RELEASE_SUMMARY.md) | 400 | Production validation |

---

## Core Methodology

### Step 1: Markov Engine (Causality)
```
Raw Path Data -> Transition Matrix T -> Removal Effects -> Causal Value v(S)
```

### Step 2: Shapley Engine (Fairness)
```
Causal Values -> Coalition Enumeration -> Marginal Contributions -> Fair Shares
```

### Step 3: Hybrid Attribution
```
Hybrid = alpha * Markov + (1-alpha) * Shapley
```

Where alpha in [0,1] controls the tradeoff between pure causality (alpha=1) and pure fairness (alpha=0).

---

## Privacy & Security

- **No PII storage** - Fingerprint-based path grouping
- **Local computation** - All processing client-side
- **No tracking** - Zero external API calls
- **User-controlled** - Explicit export, no background sync

---

## Performance

| Operation | Channels | Runtime |
|-----------|----------|---------|
| Single attribution | 5 | <1s |
| Full robustness stack | 5 | ~15s |
| Bootstrap (B=200) | 5 | ~25s |

**Complexity limits:**
- Exact Shapley: n <= 12 channels (enforced)
- Transition matrix: n <= 50 states (practical)

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Michaelrobins938/first-principles-attribution.git
cd first-principles-attribution
```

### 2. Explore the code
```bash
# Read the core engine
cat src/attribution.js

# View example output
cat examples/sample_attribution_result.json
```

### 3. Read the docs
Start with [USAGE.md](docs/USAGE.md) for a 5-minute overview.

---

## Key Achievements

- **Frozen v1.0.0** - Production-ready release
- **Dual UQ Framework** - Bootstrap + Dirichlet parameter uncertainty
- **735-line Whitepaper** - Complete mathematical specification
- **Schema-Validated** - All artifacts comply with JSON Schema
- **Row-stochastic error: 4.44e-16** - Machine epsilon precision
- **Zero hydration errors** - Clean React/Next.js implementation

---

## Citation

If you use this work in research, please cite:

```bibtex
@software{robinson2024attribution,
  author = {Robinson, Forsythe},
  title = {First-Principles Attribution Engine},
  year = {2024},
  version = {1.0.0},
  url = {https://github.com/Michaelrobins938/first-principles-attribution}
}
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Acknowledgments

**Mathematical Foundations:**
- Lloyd Shapley (1953) - Cooperative game theory
- Kemeny & Snell (1960) - Finite Markov chains
- Marsaglia & Tsang (2000) - Gamma variate sampling

---

**Status**: Production-Ready
**Version**: 1.0.0 (Frozen)
**Last Updated**: January 2025

---

*This is a complete, correct, and defensible attribution system.*
