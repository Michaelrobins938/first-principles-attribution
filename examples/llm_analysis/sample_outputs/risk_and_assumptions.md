# Risk and Assumptions

## Key Assumptions

1. **First-Party Data Only**: Analysis uses only data you provide
2. **Channel Taxonomy**: Channels are correctly classified
3. **Timestamp Accuracy**: Event ordering is correct
4. **Conversion Tracking**: All conversions are captured

## Limitations

### Observational Data
This is **observational attribution**, not causal inference:
- Correlations not equal Causation
- Unobserved confounders may exist
- Consider A/B testing for ground truth

### Model Assumptions
- Markov property: Future depends only on current state
- Independence of irrelevant alternatives (Shapley)
- Stationary transition probabilities

### Data Quality
- Missing events may skew attribution
- Bot traffic not filtered
- Cross-device journeys may be broken

## Sensitivity Analysis

The alpha parameter (default=0.5) controls causality-fairness balance:
- alpha=1.0: Pure Markov (causal focus)
- alpha=0.0: Pure Shapley (fairness focus)
- alpha=0.5: Balanced (default)

Run sensitivity sweep to test robustness.

## Confidence Interpretation

The 90% confidence intervals indicate:
- **Wide CI**: High uncertainty, model sensitive to data
- **Narrow CI**: Stable ranking, reliable attribution
- **Overlapping CIs**: Channels may be statistically equivalent

---
*Risk analysis - First-Principles Attribution*
