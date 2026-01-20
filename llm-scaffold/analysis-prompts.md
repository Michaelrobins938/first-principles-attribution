# Attribution Analysis — Task Prompts

These are modular prompts for specific analytical tasks. Each can be used independently with an IR artifact.

---

## A. Conceptual Flow Diagram

```
Analyze the transition_matrix and generate a step-by-step causal flow diagram.

Requirements:
1. Identify the top 10 transitions by probability (exclude self-loops)
2. Exclude absorbing-to-absorbing transitions (CONVERSION→*, NULL→*)
3. Generate a Mermaid flowchart with probabilities as edge labels
4. Style absorbing states distinctly (CONVERSION=green, NULL=red)

Output: Mermaid diagram in ```mermaid``` code block
```

---

## B. Attribution Decomposition Narrative

```
Produce a layered explanation of the attribution results.

Structure:
1. MARKOV LAYER
   - Explain what removal effects measure
   - List channels ranked by markov_share
   - Identify which channels are "causally critical"

2. SHAPLEY LAYER
   - Explain what Shapley values guarantee
   - List channels ranked by shapley_share
   - Identify any symmetry or dummy players

3. HYBRID LAYER
   - Explain how α={alpha} blends the two
   - Show which channels benefit from causal vs fairness treatment
   - Provide the final hybrid_value ranking

4. DIVERGENCE ANALYSIS
   - Where do Markov and Shapley disagree most?
   - What does this reveal about the channel's role?

Output: Structured markdown with tables
```

---

## C. Psychographic Influence Map

```
Visualize and explain how psychographic weights affect the model.

Tasks:
1. List all psychographic_weights with their semantic interpretation
2. Classify each as: Amplifier (>1), Neutral (=1), or Dampener (<1)
3. Explain the causal chain: weights → transition counts → T → v(S) → attribution
4. Generate a Mermaid diagram showing this influence flow
5. Identify which weights have the largest downstream impact

Output: Explanation + Mermaid diagram
```

---

## D. Executive Summary (1 Page)

```
Generate a non-technical executive summary for stakeholders.

Include:
- Total revenue attributed: ${total_conversion_value}
- Number of channels analyzed
- Top 3 channels by hybrid_value with $ amounts
- One-sentence insight about model findings
- One-sentence recommendation

Exclude:
- Mathematical notation
- Technical terminology (Markov, Shapley, coalitions)
- Implementation details

Tone: Professional, confident, actionable
Length: Maximum 250 words
```

---

## E. Risk and Assumptions Checklist

```
Document the model's assumptions and potential risks.

Structure:
1. MODEL ASSUMPTIONS
   - First-order Markov assumption
   - Stationarity assumption
   - Complete observation assumption
   - Path grouping fidelity

2. DETECTED ANOMALIES
   - Check: Do all shares sum to 1.0?
   - Check: Any channels with 0% share?
   - Check: Any transition probabilities > 0.9?
   - Check: Is α at an extreme (0 or 1)?

3. STRESS TEST CHECKLIST
   | Test | How to Run | Expected |
   |------|-----------|----------|
   | Single channel | Remove all but one | 100% to that channel |
   | α sensitivity | Vary 0→1 | Smooth interpolation |
   | Weight perturbation | ±20% on weights | Bounded change |

4. RECOMMENDATIONS
   - What should be validated before acting on these results?

Output: Markdown document with tables
```

---

## F. Viz Spec Generation

```
Generate a viz_spec.json for frontend chart rendering.

Include specifications for:
1. hybrid_attribution_bar — Bar chart of hybrid_value by channel
2. share_comparison_grouped — Grouped bar: Markov vs Shapley share
3. revenue_pie — Pie chart of revenue distribution
4. transition_heatmap — Matrix visualization of T
5. alpha_sensitivity — Line chart of shares across α values
6. psychographic_weights — Horizontal bar of weight values

For each chart specify:
- type, title, axes, data array, colors

Use exact values from the IR. Do not interpolate or estimate.

Output: Valid JSON matching the viz_spec schema
```

---

## G. Full Analysis (Combined)

```
Ingest this IR JSON artifact and generate all required output files.

{paste IR JSON here}

Tasks:
1. Identify top 10 transitions (exclude self-loops, absorbing-to-absorbing)
2. Generate Mermaid flowchart with probability labels
3. Explain Markov vs Shapley vs Hybrid decomposition
4. Analyze how α={alpha} affects the blend
5. Explain psychographic weights and their semantic meaning
6. Document assumptions and stress test checklist
7. Produce executive summary (1 page, non-technical)

Required Output Files:
- executive_summary.md
- model_decomposition.md
- diagrams.mmd
- viz_spec.json
- risk_and_assumptions.md

Begin analysis.
```

---

## Usage Notes

1. **Modular**: Use individual prompts (A-F) for focused tasks
2. **Combined**: Use prompt G for full analysis pipeline
3. **IR Required**: Always provide the IR JSON artifact
4. **Verification**: LLM should verify sum constraints before proceeding
5. **Determinism**: Same IR → same outputs (verify on repeated runs)
