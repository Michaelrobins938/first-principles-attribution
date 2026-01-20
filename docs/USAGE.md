# Hybrid Attribution Analytics Platform

## User Guide & Quick Start

**Version:** 1.0.0  
**Last Updated:** 2024-12-12

---

## Quick Start (5 Minutes)

### 1. Start the Application

```bash
cd app
npm install  # First time only
npm run dev
```

**Access:** Open `http://localhost:3001` in your browser

---

### 2. Navigate the Dashboard

The platform has **4 tabs**:

| Tab | Purpose | Key Visuals |
|-----|---------|-------------|
| **Overview** | Attribution summary, channel breakdown | Bar charts, pie charts, metrics |
| **Context Profiling** | Psychographic weights, behavioral context | Radar charts, weight cards |
| **Flow Analysis** | Transition matrix, strongest paths | Heatmap, path list |
| **Robustness** | Sensitivity and uncertainty analysis | Line charts, CI bars, export buttons |

---

### 3. Run Robustness Analysis

1. Click **"Robustness"** tab
2. Click **"Run Robustness Analysis"** button
3. Wait ~15 seconds for completion
4. Scroll through results:
   - α-Sweep chart
   - λ-Sweep chart
   - UQ Comparison (Bootstrap vs Dirichlet)
   - Dirichlet Diagnostics
   - Rank Stability tables

---

### 4. Export Artifacts

Scroll to **"Export Artifacts"** section at the bottom of Robustness tab.

Click any button to download:

- **Attribution Result** → Core IR artifact
- **α-Sensitivity** → Parameter sensitivity analysis
- **λ-Sensitivity** → Prior strength sensitivity
- **Path Bootstrap** → Sampling uncertainty
- **Dirichlet Transition UQ** → Parameter uncertainty

**Files saved to:** Your browser's default download folder

**Filename format:** `<type>_<timestamp>.json`

Example: `uq_transition_dirichlet_2024-12-12T01-45-03.json`

---

## Understanding the Results

### Attribution Scores (Overview Tab)

**Three scores per channel:**

1. **Markov Value** — Causal contribution (removal effect)
2. **Shapley Value** — Fair allocation (game theory)
3. **Hybrid Value** — Blended attribution (α × Markov + (1-α) × Shapley)

**Key Metrics:**

- **Top Channel** — Highest hybrid attribution
- **Conversion Rate** — % of paths that converted
- **Avg per Channel** — Mean attribution across channels

---

### Robustness Analysis

#### α-Sweep

**Shows:** How attribution changes as α varies from 0 (pure Shapley) to 1 (pure Markov)

**Interpret:**

- **Flat lines** → Robust to α choice
- **Steep changes** → Sensitive to fairness vs causality tradeoff
- Default α=0.5 balances both philosophies

#### λ-Sweep

**Shows:** How attribution changes as psychographic weight strength varies

**Interpret:**

- **Relative range < 10%** → Stable (green badge)
- **Relative range > 10%** → Sensitive to priors (orange badge)

#### Bootstrap vs Dirichlet UQ

**Bootstrap (Teal bars):**

- Uncertainty from **path sampling**
- "How much do results vary if we resample journeys?"

**Dirichlet (Purple bars):**

- Uncertainty from **transition parameters**
- "How much do results vary if T matrix is uncertain?"

**Compare:**

- **Both narrow** → High confidence
- **Both wide** → High uncertainty, need more data
- **Bootstrap wide, Dirichlet narrow** → Path variation dominates
- **Dirichlet wide, Bootstrap narrow** → Transition uncertainty dominates

---

### Rank Stability

**Metrics:**

- **top1** — % of samples where channel ranks #1
- **top2** — % of samples where channel ranks top-2

**Interpret:**

- `top1 > 0.8` → Dominant channel, robust
- `top1 < 0.5` → Competitive, no clear winner
- `top2 - top1 > 0.3` → Strong #2 contender

---

## Modifying Parameters

### Changing α (Blend Parameter)

**UI:** Model Configuration slider (Overview tab)

- α = 0.0 → Pure Shapley (fairness only)
- α = 0.5 → Balanced (default)
- α = 1.0 → Pure Markov (causality only)

Click **"Recalculate Model"** after changing.

### Adjusting Psychographic Weights

**Code:** Edit `PSYCHOGRAPHIC_WEIGHTS` in `attribution.js`:

```javascript
const PSYCHOGRAPHIC_WEIGHTS = {
    'high_intent_search': 1.5,    // Amplify high-intent
    'desktop_checkout': 1.3,      // Amplify desktop conversions
    'standard_email_click': 1.1,  // Mild amplification
    'standard_search': 1.0,       // Neutral (baseline)
    'low_intent_social': 0.7,     // Dampen low-intent
};
```

**Restart dev server** for changes to take effect.

---

## Validating Exported Artifacts

### Using JSON Schema Validation

```bash
# Install AJV (if not already installed)
npm install -g ajv-cli

# Validate artifact
ajv validate -s llm-scaffold/ir-schema.json -d <your-artifact>.json
```

**Expected output:** `<your-artifact>.json valid`

---

### Manual Verification

Open JSON file and check:

**Attribution Result:**

- `hybrid_share` values sum to ~1.0
- `hybrid_value` values sum to `total_conversion_value`
- `ir_version` is "1.0.0"

**Dirichlet UQ:**

- `row_stochastic_max_abs_error` < 1e-6 ✅
- `min_entry` ≥ 0 ✅
- `max_entry` ≤ 1 ✅
- Quantiles ordered: p05 ≤ p25 ≤ p50 ≤ p75 ≤ p95 ✅

---

## Troubleshooting

### Issue: "Shapley exact enumeration disabled for n=13"

**Cause:** More than 12 channels detected

**Fix:** Simplify state space or implement Monte Carlo Shapley

---

### Issue: "Bootstrap replicate total value check violated"

**Cause:** Resampling produced zero-conversion paths

**Fix:** Already handled automatically (zero-value replicates are skipped)

---

### Issue: Hydration mismatch warnings

**Cause:** Browser extensions modifying HTML

**Fix:** Already resolved with `suppressHydrationWarning` in layout

---

### Issue: Charts not rendering

**Check:**

1. Console for errors
2. Click "Recalculate Model" button
3. Hard refresh (Ctrl+Shift+R)

---

## Data Input Format

### Raw Events Structure

```javascript
const MOCK_RAW_EVENTS = [
    {
        timestamp: 100,
        channel: 'Search',
        context_key: 'high_intent_search',
        conversion_value: 0,
        os_version: 'iOS 26.1',
        timezone_offset: '-21600'
    },
    {
        timestamp: 200,
        channel: 'Direct',
        context_key: 'desktop_checkout',
        conversion_value: 100.0,
        os_version: 'iOS 26.1',
        timezone_offset: '-21600'
    }
    // ...
];
```

**Edit:** Modify `MOCK_RAW_EVENTS` in `attribution.js` to use your data

---

## Best Practices

### 1. Data Preparation

- ✅ Group events by user journey (timestamp-based sessions)
- ✅ Assign `context_key` for psychographic modeling
- ✅ Mark conversion events with `conversion_value > 0`
- ✅ Use consistent channel names

### 2. Parameter Tuning

- Start with default α = 0.5
- Run α-sweep to see sensitivity
- Adjust psychographic weights based on domain knowledge
- Use λ-sweep to validate weight impact

### 3. Uncertainty Quantification

- Run B ≥ 100 for both Bootstrap and Dirichlet
- B = 200-500 for publication-quality results
- Check rank stability for decision-critical channels

### 4. Artifact Management

- Export all artifacts after major runs
- Store with descriptive names
- Validate against schema before archiving
- Track `generated_at` timestamps for versioning

---

## Performance Tips

### Reducing Runtime

| Change | Impact | Runtime Reduction |
|--------|--------|-------------------|
| Reduce B (100 → 50) | Less stable CIs | ~50% |
| Simplify state space | Fewer states | Exponential |
| Use α=0.5 only | Skip α-sweep | ~70% |

### Optimal Settings

**Fast exploration:** B=50, α-grid 5 steps  
**Production:** B=200, full analysis  
**Maximum rigor:** B=500, validate all invariants

---

## Advanced Usage

### Batch Processing

```javascript
// Run multiple scenarios
const scenarios = [
  { alpha: 0.3, label: 'Shapley-heavy' },
  { alpha: 0.5, label: 'Balanced' },
  { alpha: 0.7, label: 'Markov-heavy' }
];

scenarios.forEach(s => {
  const result = runHybridAttributionModel(rawEvents, s.alpha);
  console.log(`${s.label}: ${JSON.stringify(result.hybrid_value)}`);
});
```

### Comparing Runs Over Time

1. Export attribution result at T1
2. Add new data, export at T2
3. Diff JSON artifacts to see changes
4. Track `hybrid_value` drift per channel

---

## Support & Documentation

**Full Technical Docs:**

- `WHITEPAPER.md` — Mathematical foundations
- `PRD.md` — Product specification
- `llm-scaffold/ir-schema.json` — Artifact schemas

**Questions?**

- Review invariants in Section 6 of PRD
- Check Appendix C (Stress Test Protocol) in WHITEPAPER
- Validate exported artifacts against schema

---

## Example Workflow

### Typical Session (15 minutes)

1. **Prepare data** — Load your events into `MOCK_RAW_EVENTS`
2. **Initial run** — Start app, view Overview tab
3. **Explore** — Navigate tabs, understand baseline attribution
4. **Tune parameters** — Adjust α, check impact
5. **Run robustness** — Click "Run Robustness Analysis"
6. **Review sensitivity** — Check α-sweep and λ-sweep charts
7. **Quantify uncertainty** — Compare Bootstrap vs Dirichlet CIs
8. **Export artifacts** — Download all JSON files
9. **Validate** — Run schema validation on exports
10. **Archive** — Store artifacts with timestamp

---

**Ready to Use!** 🎉

For detailed methodology, see `WHITEPAPER.md`.  
For technical specifications, see `PRD.md`.
