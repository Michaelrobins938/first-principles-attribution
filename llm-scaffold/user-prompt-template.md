# Attribution Analysis - User Prompt Template

## Instructions

Copy this template and replace `{{IR_JSON}}` with your actual IR artifact JSON.

---

## Prompt

Ingest this IR JSON artifact and generate the required output files.

```json
{{IR_JSON}}
```

### Required Analysis Tasks

1. **Top Transitions**: Identify the top 10 transitions, excluding:
   - Self-loops (X → X)
   - Absorbing-to-absorbing (CONVERSION → *, NULL →*)

2. **Mermaid Flowchart**: Generate a flowchart for the top transitions with probabilities as edge labels.

3. **Decomposition Narrative**: Explain:
   - How Markov removal effects differ from Shapley allocations
   - How the α parameter (currently {{ALPHA}}) affects the hybrid result
   - Which channels benefit more from causal vs fairness treatment

4. **Psychographic Analysis**: Explain:
   - Which psychographic weights were applied
   - What they mean semantically (high-intent, low-intent, etc.)
   - How they affected the transition probabilities

5. **Assumptions Checklist**: Provide:
   - List of model assumptions
   - Stress-test scenarios to validate results
   - Any anomalies or warnings detected in this specific IR

### Output Files Required

- `executive_summary.md`
- `model_decomposition.md`
- `diagrams.mmd`
- `viz_spec.json`
- `risk_and_assumptions.md`

---

## Example IR Artifact

For reference, here's the expected IR structure:

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
  "states": ["Affiliate", "CONVERSION", "Direct", "Email", "NULL", "START", "Search", "Social"],
  "transition_matrix": [[...]],
  "markov_share": {"Affiliate": 0.15, "Direct": 0.25, ...},
  "shapley_share": {"Affiliate": 0.12, "Direct": 0.28, ...},
  "hybrid_share": {"Affiliate": 0.135, "Direct": 0.265, ...},
  "hybrid_value": {"Affiliate": 20.25, "Direct": 39.75, ...},
  "total_conversion_value": 150,
  "alpha": 0.5,
  "psychographic_weights": {
    "high_intent_search": 1.5,
    "low_intent_social": 0.7
  },
  "notes": {
    "no_raw_events": true,
    "no_identifiers": true,
    "generated_at": "2024-12-11T..."
  }
}
```
