# Model Decomposition: Hybrid Markov-Shapley Attribution

## Model Architecture

This system uses a **hybrid approach** combining two complementary methods:

### 1. Markov Chain Analysis (Causal)

The Markov model treats customer journeys as stochastic processes:
- **States**: Channel touchpoints + CONVERSION + NULL (no conversion)
- **Transitions**: Probability of moving from one state to another
- **Removal Effect**: Remove a channel, measure conversion rate drop

**Strengths:**
- Captures path dependencies
- Identifies critical conversion pathways
- Works with observational data

### 2. Shapley Value Calculation (Fair)

Shapley values allocate credit based on game theory:
- **Coalitions**: All possible channel subsets
- **Marginal Contribution**: Each channel impact on coalition value
- **Fairness**: Axiomatic guarantee of equal contribution = equal credit

**Strengths:**
- Mathematically fair allocation
- Handles interaction effects
- No arbitrary weights

### 3. Hybrid Blending (alpha=0.5)

The final attribution is: 

With alpha=0.5, we balance causality (Markov) with fairness (Shapley).

## Technical Specifications

- **Bootstrap resampling**: 10,000 iterations
- **Confidence level**: 90%
- **Validation**: All invariants checked

---
*Technical documentation - First-Principles Attribution*
