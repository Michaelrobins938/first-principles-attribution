# A First-Principles Hybrid Attribution Framework

## Integrating Probabilistic Path Modeling, Cooperative Game Theory, and Psychographic Transition Priors

**Technical Whitepaper v2.0.0****Classification:** Methodology 
**Classification:** Methodology Specification / Decision Science  
**Status:** Production-Ready / Frozen  
**Document Version:** 2.0.0  
**Last Updated:** January 21, 2026Specification  
**Status:** Frozen (implementation-complete)

---

## Abstract

Traditional attribution models fail either by ignoring sequence (heuristics) or fairness (pure probabilistic models). This paper presents a hybrid framework that combines **absorbing Markov chains** (for causal sequence modeling) with **Shapley Value attribution** (for axiomatic fairness), augmented by **psychographic transition priors**.

The framework is device-agnostic, identifier-independent, and grounded in first principles of stochastic processes and cooperative game theory. We provide:

1. A rigorous theoretical foundation
2. A frozen reference implementation
3. Explicit assumptions and limitations
4. A clean interface for downstream analysis

**Keywords:** multi-touch attribution, absorbing Markov chains, Shapley values, cooperative game theory, psychographic priors, causal inference

---

## 1. The Attribution Problem (First Principles)

### 1.1 What Attribution Must Explain

Attribution is fundamentally about assigning **marginal responsibility** for an outcome across a **sequence of dependent actions**.

Any valid attribution system must:

| Requirement | Description |
|-------------|-------------|
| **Sequence** | Order of touchpoints matters |
| **Counterfactuals** | "What if channel X didn't exist?" must be answerable |
| **Fairness** | No free riders, no double counting, symmetric treatment |
| **Efficiency** | Total credit equals total outcome |

### 1.2 Why Heuristics Fail

Common rules (last-touch, first-touch, linear, time-decay) suffer fundamental deficiencies:

| Model | Failure Mode |
|-------|-------------|
| Last-touch | Ignores all prior touchpoints; rewards closers only |
| First-touch | Ignores nurturing; rewards openers only |
| Linear | Treats all touchpoints equally regardless of contribution |
| Time-decay | Arbitrary decay function with no causal basis |

**Common failures across all heuristics:**

- Ignore counterfactuals entirely
- Cannot model interaction effects
- Violate fairness axioms (dummy player, symmetry)
- Provide no mathematical guarantees

---

## 2. Probabilistic Path Modeling (Markov Chains)

### 2.1 Modeling User Journeys as Stochastic Processes

We model a customer journey as a discrete-time stochastic process over a finite state space:

```
X₀ = START
Xₜ ∈ {channels} ∪ {CONVERSION, NULL}
```

The process terminates upon reaching an **absorbing state** (CONVERSION or NULL).

### 2.2 The Markov Assumption

**Assumption 2.1 (First-Order Markov):**
> The probability of transitioning to the next state depends only on the current state, not on the history of prior states.

```
P(Xₜ₊₁ | Xₜ, Xₜ₋₁, ..., X₀) = P(Xₜ₊₁ | Xₜ)
```

This assumption is:

- **Explicit** (documented as a limitation)
- **Relaxable** (higher-order extensions possible)
- **Empirically reasonable** for many attribution contexts

### 2.3 State Space Construction

The state space S consists of:

| State Type | States | Properties |
|------------|--------|------------|
| Initial | START | Transient, origin of all paths |
| Channels | {Affiliate, Direct, Email, Search, Social, ...} | Transient |
| Success | CONVERSION | Absorbing |
| Failure | NULL | Absorbing |

### 2.4 Transition Matrix

The transition matrix **T** is row-stochastic:

```
T[i][j] = P(Xₜ₊₁ = j | Xₜ = i)

∀i: Σⱼ T[i][j] = 1
```

Partitioned as:

```
T = | Q  R |
    | 0  I |
```

Where:

- **Q**: transient → transient transitions
- **R**: transient → absorbing transitions
- **I**: identity (absorbing states remain)

### 2.5 Fundamental Matrix and Absorption Probabilities

The **fundamental matrix** captures expected visits:

```
N = (I - Q)⁻¹
```

The **absorption probability matrix**:

```
B = N × R
```

Where `B[START][CONVERSION]` gives the probability of eventual conversion starting from START.

### 2.6 The Characteristic Function v(S)

For any subset of channels S ⊆ Channels:

```
v(S) = P(CONVERSION | only channels in S active)
```

**Computation procedure:**

1. Construct T_S by redirecting transitions to/from channels not in S to NULL
2. Compute the modified absorbing chain
3. Return absorption probability into CONVERSION from START

**Properties of v(S):**

- v(∅) = baseline conversion (typically 0 or near 0)
- v(Channels) = full model conversion probability
- v is monotonic: S ⊆ T → v(S) ≤ v(T)
- v captures **causal contribution** but not fairness

---

## 3. Fairness via Cooperative Game Theory (Shapley Value)

### 3.1 Attribution as a Cooperative Game

We model attribution as a cooperative game (N, v):

| Element | Interpretation |
|---------|---------------|
| N | Set of marketing channels (players) |
| v | Characteristic function (conversion probability) |
| v(S) | Value when only coalition S participates |

### 3.2 The Shapley Value

**Theorem (Shapley, 1953):** There exists a unique allocation φ satisfying:

1. **Efficiency:** Σᵢ φᵢ = v(N) - v(∅)
2. **Symmetry:** If i and j contribute equally, φᵢ = φⱼ
3. **Dummy Player:** If i adds no value, φᵢ = 0
4. **Additivity:** φ(v + w) = φ(v) + φ(w)

The unique solution is:

```
φᵢ(v) = Σ_{S ⊆ N \ {i}} [|S|!(|N|-|S|-1)!/|N|!] × [v(S ∪ {i}) - v(S)]
```

**Interpretation:** The Shapley value is the expected marginal contribution of player i, averaged over all possible orderings in which players arrive.

### 3.3 Why Shapley Alone Is Insufficient

Shapley treats the game as **order-agnostic**:

- All coalitions are unordered sets
- Cannot express that "Search before Email" differs from "Email before Search"
- Ignores sequential dependencies inherent in customer journeys

**Conclusion:** Shapley provides fairness but loses causality.

---

## 4. The Hybrid Model (Core Contribution)

### 4.1 Design Principle: Model Stacking, Not Averaging

> **Markov defines the value function v(S)**  
> **Shapley distributes that value fairly**

This stacking preserves:

- **Causality** from the Markov process
- **Fairness** from Shapley axioms

The Markov model encodes path structure into v(S), then Shapley fairly allocates the total value.

### 4.2 Dual Attribution Scores

**Markov Removal Effect:**

```
M_i = v(N) - v(N \ {i})
```

Interpretation: How much does conversion probability drop if channel i is removed?

**Shapley Value:**

```
S_i = φᵢ(v)
```

Interpretation: What is channel i's fair share of the total value?

### 4.3 Normalization to Shares

Both are normalized to unit-sum shares:

```
markov_share[i] = M_i / Σⱼ M_j
shapley_share[i] = S_i / Σⱼ S_j
```

**Invariant:** Both sum to 1.0 (enforced at runtime with tolerance 1e-6).

### 4.4 Hybrid Attribution Score

```
H_i = α × markov_share[i] + (1 - α) × shapley_share[i]
```

Where α ∈ [0, 1] controls emphasis:

| α | Interpretation |
|---|----------------|
| 1.0 | Pure causality (Markov removal effects only) |
| 0.5 | Balanced blend (default) |
| 0.0 | Pure fairness (Shapley values only) |

### 4.5 Monetary Attribution

```
hybrid_value[i] = H_i × total_conversion_value
```

---

## 5. Psychographic Transition Priors (Behavioral Layer)

### 5.1 Motivation

Human decisions are not memoryless or context-free. The same channel may have different influence depending on:

- User intent (high-intent search vs. browsing)
- Device context (mobile vs. desktop)
- Temporal factors (time of day, recency)

We introduce **priors on transitions**, not on identity.

### 5.2 Mathematical Formulation

Let w(c) be a psychographic weight for context c:

```
T[i][j] ∝ Σ_paths Σ_transitions w(context) × 𝟙(Xₜ=i, Xₜ₊₁=j)
```

The weights modulate **transition counts** before normalization, preserving row-stochasticity.

### 5.3 Example Weight Configuration

```javascript
PSYCHOGRAPHIC_WEIGHTS = {
    'high_intent_search': 1.5,    // Amplifier
    'desktop_checkout': 1.3,      // Amplifier
    'standard_email_click': 1.1,  // Mild amplifier
    'standard_search': 1.0,       // Neutral
    'low_intent_social': 0.7,     // Dampener
}
```

### 5.4 Semantic Interpretation

| Weight Range | Interpretation |
|--------------|----------------|
| w > 1.0 | Context amplifies transition's importance |
| w = 1.0 | Neutral (default) |
| w < 1.0 | Context dampens transition's importance |

### 5.5 Key Property

**Weights modify probability mass, not attribution logic.**

The psychographic layer affects T, which cascades to:

- v(S) computation
- Both Markov and Shapley attributions

But the core attribution algorithms remain unchanged.

---

## 6. Properties of the Framework

### 6.1 Theoretical Guarantees

| Property | Source | Guarantee |
|----------|--------|-----------|
| Sequence-aware | Markov chain | Path order encoded in T |
| Counterfactual | Removal effects | v(N) - v(N\{i}) well-defined |
| Efficient | Shapley axiom | Σᵢ φᵢ = v(N) |
| Symmetric | Shapley axiom | Equal contributors → equal credit |
| Dummy-free | Shapley axiom | Zero contribution → zero credit |
| Identifier-independent | Design | No PII in IR |

### 6.2 Computational Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Path grouping | O(m) | m = events |
| Transition matrix | O(n² × m) | n = states |
| Matrix inversion | O(n³) | For fundamental matrix |
| Single v(S) | O(n³) | One absorption calculation |
| Exact Shapley | O(n × 2ⁿ × n³) | Enumeration over coalitions |

**Guardrail:** n ≤ 12 for exact Shapley (enforced at runtime).

### 6.3 Extensibility

The framework supports extensions:

- Higher-order Markov (k-th order dependencies)
- Semi-Markov (sojourn times)
- Monte Carlo Shapley (n > 12)
- Hierarchical grouping (channel taxonomies)

---

## 7. Limitations and Causal Interpretation

> **CRITICAL DISCLAIMER:** This section documents what the model does NOT prove.
> Read this before making strategic decisions based on attribution outputs.

### 7.0 What This Model Does NOT Prove

#### 7.0.1 Causal Direction

We **cannot distinguish** between:

- "Email **caused** the purchase"
- "Users who will purchase **tend to check** email"

The Markov removal effect measures **contribution under the observed data distribution**, not causal intervention effects. A channel's high removal effect could reflect:

1. **True causation**: The channel genuinely influences conversion
2. **Selection bias**: High-intent users prefer that channel
3. **Confounding**: External factors (e.g., TV ads) drive both channel visits and conversions

#### 7.0.2 Confounders Not Controlled

We do **not** control for:

| Confounder | Impact |
|------------|--------|
| **User intent** | Users who've already decided to buy may visit certain channels |
| **External factors** | Offline ads, word-of-mouth, seasonality |
| **Selection bias** | Who uses which channels is not random |
| **Temporal confounds** | Macro trends affecting all channels |

#### 7.0.3 Counterfactual Validity

Removal effects assume:

- **Channel independence**: Removing Search doesn't change Email's effectiveness (often false)
- **Stable transitions**: The transition matrix remains valid under intervention (questionable)
- **No substitution**: Users wouldn't find alternative paths (unrealistic)

These assumptions limit the validity of statements like "Removing Search would cost us $X."

### 7.0.4 What We CAN Claim

| Claim Type | Validity | Example |
|------------|----------|---------|
| **Descriptive accuracy** | ✅ Strong | "Model captures observed journey patterns" |
| **Contribution quantification** | ✅ Strong | "Given observed sequences, Search contributes 42%" |
| **Relative ranking** | ✅ Moderate | "Search contributes more than Display" |
| **Uncertainty transparency** | ✅ Strong | "We're 85% confident Search is #1" |
| **Absolute causal effects** | ❌ Invalid | "Search **caused** $63 in revenue" |
| **Intervention predictions** | ❌ Invalid | "Removing Search loses $63" |
| **Budget optimization** | ⚠️ Caution | "Shift budget from Display to Search" |

### 7.0.5 When to Trust This Model

**Trust the model for:**
- ✅ Relative channel ranking (which matters more)
- ✅ Sensitivity analysis (how confident should we be?)
- ✅ Identifying channels that **might** be important
- ✅ Comparing attribution methodologies

**Do NOT trust the model for:**
- ❌ Absolute dollar values ("Search is worth exactly $63")
- ❌ Intervention planning ("Cut Display spend by 50%")
- ❌ Causal claims in stakeholder reports

### 7.0.6 Path to Stronger Causal Claims

To move from **contribution** to **causation**, you need:

| Method | What It Provides | Feasibility |
|--------|------------------|-------------|
| **Randomized A/B tests** | Ground truth causal effects | Gold standard, but expensive |
| **Propensity score matching** | Quasi-experimental control | Requires rich user features |
| **Instrumental variables** | Exogenous variation | Hard to find valid instruments |
| **Regression discontinuity** | Local causal effects | Needs sharp thresholds |
| **Synthetic control** | Counterfactual comparison | Needs donor pool |

**Recommendation:** Use this model to **generate hypotheses**, then validate top channels with targeted A/B tests.

---

### 7.1 Documented Assumptions

| Assumption | Impact | Mitigation |
|------------|--------|------------|
| First-order Markov | Ignores longer history | k-th order extension |
| Device fingerprinting | Path grouping fidelity | Probabilistic matching |
| Stationary process | Assumes stable transitions | Time-windowed analysis |
| Complete observation | Missing touchpoints bias | Imputation methods |

### 7.2 Shapley Complexity

Exact Shapley requires 2ⁿ coalition evaluations. The guardrail (n ≤ 12) ensures:

- 12 channels → 4,096 coalitions → tractable
- 20 channels → 1,048,576 coalitions → infeasible

**Mitigation:** Monte Carlo approximation for n > 12 (future work).

### 7.3 Path Resolution

Fingerprint-based grouping may merge or split journeys incorrectly. This affects:

- Transition probability estimates
- Path-level metrics

**Mitigation:** Tune fingerprint features; document resolution limits.

---

## 8. Sensitivity Analysis & Uncertainty Quantification

Making the model **defensible** requires quantifying how sensitive results are to parameter choices and providing confidence intervals.

### 8.1 α-Sweep (Blend Parameter Sensitivity)

The blend parameter α controls the tradeoff between causal (Markov) and fair (Shapley) attribution. We systematically vary α across [0, 1]:

```
α_grid = [0.00, 0.05, 0.10, ..., 0.95, 1.00]
```

For each α, compute full attribution. Output metrics:

| Metric | Purpose |
|--------|---------|
| min/max/range per channel | How much attribution can swing |
| Rank stability | % of α values where channel is #1, #2, etc. |

**Interpretation:** If a channel's attribution varies significantly across α, the choice of α matters for that channel's budget allocation.

### 8.2 λ-Sweep (Psychographic Prior Strength)

To test dependence on psychographic assumptions, we parameterize weight strength:

```
w'(k) = 1 + λ × (w(k) - 1)
```

Where:

- λ = 0: All weights = 1 (no psychographic effect)
- λ = 1: Original weights
- λ > 1: Amplified priors

**Grid:** λ ∈ {0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0}

**Interpretation:** Channels with high relative_range (>10%) are **sensitive to priors** and require careful weight calibration.

### 8.3 Bootstrap Uncertainty Quantification

To produce **confidence intervals**, we resample paths with replacement:

**Procedure:**

1. Generate paths once from raw events
2. For b = 1 to B (typically B = 100-500):
   - Resample paths with replacement
   - Rebuild transition matrix T
   - Compute Markov and Shapley attribution
   - Record hybrid_value per channel
3. Compute percentiles across bootstrap samples

**Output metrics:**

| Metric | Definition |
|--------|------------|
| p05, p50, p95 | 5th, 50th, 95th percentile |
| 90% CI | [p05, p95] confidence interval |
| Rank stability | % of samples where channel is #1 |

}

```

### 8.4 Dirichlet Transition Matrix Uncertainty Quantification

While bootstrap UQ quantifies **path-level sampling uncertainty**, it assumes the transition matrix T is deterministic given the observed paths. In reality, T itself is estimated from finite data and carries **parameter uncertainty**.

#### 8.4.1 Motivation: Two Sources of Uncertainty

| UQ Method | Target | Question Answered |
|-----------|--------|-------------------|
| **Bootstrap** | Path sampling | "How much do results vary if we resample journeys?" |
| **Dirichlet** | Transition parameters | "How much do results vary if T is uncertain?" |

Both are complementary — bootstrap captures data variability, Dirichlet captures model parameter uncertainty.

#### 8.4.2 Bayesian Posterior for T

Each row of T is a discrete probability distribution over next states. We model uncertainty via **row-wise Dirichlet posteriors**:

```

T[i,·] ~ Dirichlet(α₀ + counts[i,·])

```

Where:
- `counts[i,j]` = observed transition count from state i to j (psychographically weighted)
- `α₀` = Dirichlet concentration parameter (prior strength)
- `α₀ + counts[i,·]` = posterior parameters

**Interpretation:**
- `α₀ = 0.1` (weak prior): Let data dominate
- `α₀ = 1.0` (Laplace prior): Add 1 pseudo-count per state
- `α₀ → 0` (empirical Bayes): Pure MLE

#### 8.4.3 Sampling Procedure

For each bootstrap replicate b = 1..B:

1. **Compute empirical counts** (with psychographic weights):
   ```

   N[i,j] = Σ_paths Σ_transitions w(context) × 𝟙(Xₜ=i, Xₜ₊₁=j)

   ```

2. **Sample T row-wise from Dirichlet**:
   ```

   T[i,·] ~ Dirichlet(α₀ + N[i,·])

   ```
   
   Implementation uses **Gamma variates** (Marsaglia-Tsang algorithm):
   ```

   Gₖ ~ Gamma(α₀ + N[i,k], 1)
   T[i,k] = Gₖ / Σⱼ Gⱼ

   ```

3. **Compute attribution** using sampled T:
   - Markov removal effects → markov_share
   - Shapley values → shapley_share
   - Hybrid blend → hybrid_value

4. **Aggregate** confidence intervals across samples

#### 8.4.4 Invariants (Enforced)

| Invariant | Tolerance | Description |
|-----------|-----------|-------------|
| **Row-stochastic** | ≤ 1e-6 | Each row sums to 1.0 |
| **Non-negative** | min_entry ≥ 0 | All probabilities ≥ 0 |
| **Bounded** | max_entry ≤ 1 | All probabilities ≤ 1 |
| **Value conservation** | ≤ $1.00 | Σ hybrid_value = total_value |
| **Quantile ordering** | Exact | p05 ≤ p25 ≤ p50 ≤ p75 ≤ p95 |

#### 8.4.5 Output Artifact

```json
{
  "type": "uq_transition_dirichlet",
  "version": "1.0.0",
  "B": 100,
  "alpha": 0.5,
  "dirichlet_prior": 0.1,
  "uq_target": "transition_matrix",
  "posterior": "dirichlet_rowwise",
  "counts_semantics": "weighted_pseudocounts",
  "method": "transition_dirichlet",
  "confidence_intervals": {
    "Search": {"p05": 16.15, "p50": 38.46, "p95": 62.78}
  },
  "rank_stability": {
    "Search": {"top1": 0.21, "top2": 0.51}
  },
  "row_stochastic_max_abs_error": 4.44e-16,
  "min_entry": 5.30e-37,
  "max_entry": 0.9999,
  "generated_at": "ISO-8601",
  "seed": 1234567890
}
```

#### 8.4.6 Interpretation Guidelines

**Comparing Bootstrap vs Dirichlet CIs:**

- **Narrow Dirichlet, wide Bootstrap**: Path variation dominates → focus on collecting more diverse journeys
- **Wide Dirichlet, narrow Bootstrap**: Transition uncertainty dominates → need more observations per state
- **Both narrow**: High confidence in results
- **Both wide**: High overall uncertainty → increase sample size or simplify state space

**Rank Stability:**

If a channel has:

- `top1 < 0.5`: **Not confidently #1** — competing channels exist
- `top2 - top1 > 0.3`: **Strong #2 contender** — competitive dynamics
- `top1 > 0.8`: **Dominant attribution** — robust to UQ

### 8.5 Sensitivity Artifacts

The framework produces versioned sensitivity artifacts:

```json
{
  "type": "sensitivity_alpha",
  "version": "1.0.0",
  "alpha_grid": [0, 0.05, ..., 1],
  "hybrid_value_series": {"Search": [...], "Email": [...]},
  "statistics": {"Search": {"min": 40, "max": 70, "range": 30}},
  "rank_stability": {"Search": {"top1": 0.85, "top2": 0.95}}
}
```

```json
{
  "type": "uq_bootstrap",
  "version": "1.0.0",
  "B": 200,
  "alpha": 0.5,
  "confidence_intervals": {
    "Search": {"p05": 41.2, "p50": 56.3, "p95": 70.8}
  },
  "rank_stability": {"Search": {"top1": 0.71}}
}
```

---

## 9. Implementation Specification

### 8.1 Frozen Reference Implementation

The reference implementation is frozen at version 1.0.0:

```javascript
return {
    ir_version: "1.0.0",
    model: {
        markov_order: 1,
        shapley: "exact",
        removal_policy: "redirect_to_NULL",
        psychographic_priors: "source_context_multiplier",
        max_channels_guardrail: 12
    },
    // ...attribution outputs
}
```

### 8.2 Invariants (Enforced at Runtime)

```javascript
// Guardrail: channel count
if (channels.length > SHAPLEY_EXACT_MAX_CHANNELS) {
    throw new Error(`Shapley exact enumeration disabled for n=${channels.length}.`);
}

// Integrity: shares sum to 1
const sumShares = Object.values(hybridShare).reduce((a, b) => a + b, 0);
if (Math.abs(sumShares - 1) > 1e-6 && channels.length > 0) {
    throw new Error(`Hybrid shares do not sum to 1 (got ${sumShares}).`);
}
```

### 8.3 IR Contract (Canonical Output)

See Appendix A for the full JSON schema.

---

## 9. Conclusion

This framework unifies:

| Domain | Contribution |
|--------|-------------|
| **Stochastic Processes** | Absorbing Markov chains for causal sequence modeling |
| **Game Theory** | Shapley values for axiomatic fairness |
| **Behavioral Science** | Psychographic priors for context-aware transitions |

The result is a mathematically rigorous, interpretable, and extensible attribution system with:

- Clear theoretical foundations
- Explicit assumptions
- Frozen reference implementation
- Clean interfaces for downstream analysis

---

## 10. Future Work

1. **Monte Carlo Shapley** — Approximate Shapley for n > 12 via random permutation sampling
2. **Higher-Order Markov** — k-th order chains to capture path dependencies
3. **Semi-Markov Extensions** — Model sojourn times between transitions
4. **Hierarchical Grouping** — Aggregate channels into categories with nested Shapley
5. **Online Updating** — Incremental matrix updates as new data arrives
6. **Causal Discovery** — Learn influence graphs from observational data
7. **Sensitivity Analysis Toolkit** — Automated stress testing across α and weights

---

## Appendix A: IR JSON Schema

```json
{
  "ir_version": "1.0.0",
  "model": {
    "markov_order": 1,
    "shapley": "exact",
    "removal_policy": "redirect_to_NULL",
    "psychographic_priors": "source_context_multiplier",
    "max_channels_guardrail": 12
  },
  "states": ["START", "...", "CONVERSION", "NULL"],
  "transition_matrix": [[...]],
  "markov_share": {"channel": 0.xx},
  "markov_value": {"channel": $xx.xx},
  "shapley_share": {"channel": 0.xx},
  "shapley_value": {"channel": $xx.xx},
  "hybrid_share": {"channel": 0.xx},
  "hybrid_value": {"channel": $xx.xx},
  "alpha": 0.5,
  "total_conversion_value": 150.00,
  "psychographic_weights": {"context": weight},
  "notes": {
    "no_raw_events": true,
    "no_identifiers": true,
    "generated_at": "ISO-8601"
  }
}
```

## Appendix B: Mathematical Notation Reference

| Symbol | Definition |
|--------|------------|
| N | Set of channels (players) |
| S | Coalition (subset of N) |
| v(S) | Characteristic function (conversion probability with S active) |
| φᵢ | Shapley value for channel i |
| T | Transition probability matrix |
| Q | Transient-to-transient submatrix |
| R | Transient-to-absorbing submatrix |
| N = (I-Q)⁻¹ | Fundamental matrix |
| B = NR | Absorption probability matrix |
| M_i | Markov removal effect for channel i |
| H_i | Hybrid attribution share for channel i |
| α | Blend parameter (0 = Shapley, 1 = Markov) |
| w(c) | Psychographic weight for context c |

## Appendix C: Stress Test Protocol

| Test Case | Expected Result | Pass Condition |
|-----------|-----------------|----------------|
| Single channel | M = S = H = 100% for that channel | Exact equality |
| All equal channels | Uniform distribution | |σ| < 0.01 |
| Dominant converter | That channel ≫ others | Top share > 50% |
| α = 0 | H = S exactly | Max |H_i - S_i| < 1e-6 |
| α = 1 | H = M exactly | Max |H_i - M_i| < 1e-6 |
| n = 13 channels | Error thrown | Exception caught |
| Sum of shares | Exactly 1.0 | |Σ - 1| < 1e-6 |

---

*Document frozen at ir_version 1.0.0*  
*This specification governs the reference implementation.*
