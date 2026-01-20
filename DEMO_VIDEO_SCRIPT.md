# Demo Video Script: First-Principles Attribution Engine
# Duration: 10 minutes

## SCENE 1: THE PROBLEM (60 seconds)

**[VISUAL: Split screen - frustrated marketer with spreadsheet vs clean dashboard]**

**NARRATOR:**
"Marketing attribution is broken."

**[VISUAL: Show typical last-touch attribution giving 100% credit to last touchpoint]**

"Traditional tools give you numbers without insight. Last-touch says 'Google Ads gets everything.' Linear says 'Everyone gets equal credit.' Neither tells you what's actually working."

**[VISUAL: Charts showing conflicting attribution from different models]**

"And when you have multiple data sources—Facebook, Google Analytics, your CRM—good luck making sense of it all."

**[TEXT ON SCREEN:]**
"Current State: Numbers without understanding"

---

## SCENE 2: THE SOLUTION (90 seconds)

**[VISUAL: Clean architecture diagram showing data flow]**

**NARRATOR:**
"Introducing the First-Principles Attribution Engine."

**[VISUAL: Highlight the three core components]**

"It's not just an attribution tool. It's a **thinking instrument** that combines three things:"

**1. Hybrid Attribution Model**
- Markov chains for causal measurement
- Shapley values for fair allocation
- Tunable alpha parameter (default 0.5)

**2. Multi-Source Data Integration**
- Facebook, GA4, CSV, Browser History
- All normalized to UniversalEvent schema

**[VISUAL: Show adapters converting different formats to unified schema]**

**3. Built-in AI Interpretation**
- LLM scaffold generates natural language insights
- Five output types: summaries, diagrams, charts, risk analysis

**[TEXT ON SCREEN:]**
"The only attribution framework with built-in AI analysis"

---

## SCENE 3: THE DEMO (6 minutes)

### Part 3a: Load Multi-Source Data (90 seconds)

**[VISUAL: Screen recording of Jupyter notebook]**

**NARRATOR:**
"Let's walk through a real analysis. We'll combine Facebook and Google Analytics data."

```python
from src.adapters import FacebookAdapter, GoogleAnalyticsAdapter

# Load Facebook export
fb = FacebookAdapter('facebook_export.json')
fb_events = fb.parse()

# Load GA4 export  
ga = GoogleAnalyticsAdapter('ga4_export.json')
ga_events = ga.parse()

# Combine sources
all_events = fb_events + ga_events
print(f"Total events: {len(all_events)}")
```

**[VISUAL: Show output - "Total events: 15,420"]**

"15,000+ events from two sources, normalized to the UniversalEvent schema."

---

### Part 3b: Run Attribution (90 seconds)

**[VISUAL: Running attribution model]**

**NARRATOR:**
"Now we run the hybrid Markov-Shapley model."

```python
from src.attribution import run_hybrid_attribution

result = run_hybrid_attribution(
    events=all_events,
    alpha=0.5,  # Balance causality vs fairness
    n_bootstrap=10000  # For confidence intervals
)
```

**[VISUAL: Show attribution results table]**

| Channel | Attribution | 90% CI | Rank Stability |
|---------|-------------|--------|----------------|
| Search | 42% | [35%-49%] | 85% |
| Email | 25% | [20%-30%] | 78% |
| Direct | 18% | [13%-23%] | 65% |

"Search is the leader with 42% attribution. But notice the confidence intervals—we know how uncertain each estimate is."

---

### Part 3c: AI Interpretation (3 minutes) - KEY MOMENT

**[VISUAL: Running LLM scaffold]**

**NARRATOR:**
"Here's where it gets interesting. Most tools stop here with the numbers. But we feed the IR artifact to our LLM scaffold."

```python
from llm_scaffold import generate_analysis

outputs = generate_analysis(
    ir_artifact=result,
    task="full_analysis"  # Generates all 5 output types
)
```

**[VISUAL: Show files being generated]**

"📄 **executive_summary.md** - For stakeholders"
"📄 **model_decomposition.md** - For technical team"
"📄 **diagrams.mmd** - Visual flowcharts"
"📄 **viz_spec.json** - Chart specifications"
"📄 **risk_and_assumptions.md** - Caveats and limitations"

**[VISUAL: Show executive summary content]**

```
# Attribution Executive Summary

## Key Findings

### Top Performer
**Search** is the leading channel with **42%** of attributed conversions.
The 90% confidence interval is **35%-49%**, indicating high stability.

### Channel Rankings
1. Search: 42% [90% CI: 35%-49%]
2. Email: 25% [90% CI: 20%-30%]
3. Direct: 18% [90% CI: 13%-23%]

### Budget Implications
- **Search** shows strongest contribution - maintain investment
- **Email** and **Direct** show stable performance
```

**[VISUAL: Show Mermaid diagram being rendered]**

"📊 And we get automatic visualizations."

**[TEXT ON SCREEN:]**
"This is the DIFFERENCE. Numbers → Insights → Action"

---

### Part 3d: Uncertainty Quantification (30 seconds)

**[VISUAL: Confidence interval charts]**

**NARRATOR:**
"Unlike black-box tools, we provide uncertainty quantification."

- Bootstrap resampling (10,000 samples)
- 90% confidence intervals on all estimates
- Rank stability metrics

"Search is the #1 channel with 85% confidence. We're not guessing—we know our uncertainty."

---

## SCENE 4: THE DIFFERENTIATOR (90 seconds)

**[VISUAL: Comparison table]**

**NARRATOR:**
"What makes this different from other tools?"

| Feature | Other Tools | This Framework |
|---------|-------------|----------------|
| Attribution Engine | ✅ | ✅ |
| Multi-Source | Partial | ✅ Universal adapters |
| Uncertainty Quantification | ❌ | ✅ Bootstrap + Dirichlet |
| LLM Interpretation | ❌ | ✅ Built-in scaffold |
| Schema Validation | ❌ | ✅ JSON Schema |
| Causal Inference | ❌ | ✅ 5 methods |

**[TEXT ON SCREEN:]**
"The only complete decision analysis system"

**NARRATOR:**
"This isn't just attribution. It's a thinking instrument that gives you AI-powered insights from your data."

---

## SCENE 5: CALL TO ACTION (30 seconds)

**[VISUAL: GitHub repository, demo links]**

**NARRATOR:**
"Try it today."

1. **Quick start:** `examples/quickstart/01_simple_attribution.ipynb`
2. **AI interpretation demo:** `examples/llm_analysis/03_ai_interpretation.ipynb`
3. **Full documentation:** See README.md

**[TEXT ON SCREEN:]**
"⭐ Star on GitHub"
"📚 Read the docs"
"💬 Book a consultation

"Give your marketing decisions a first-principles foundation."

**[VISUAL: Final shot - clean dashboard with attribution results]**

---

## PRODUCTION NOTES

### Screen Recording Tips
- Use OBS or Loom for screen recording
- Set resolution to 1920x1080
- Use dark theme in VS Code/Jupyter
- Slow down for code explanations

### B-Roll to Gather
- Screenshot of GitHub repo
- Architecture diagram (from docs/images/)
- Sample notebook runs
- Executive summary output
- Mermaid diagrams

### Audio
- Record in quiet environment
- Use microphone with pop filter
- Aim for 140-160 BPM speaking pace
- Add background music (non-copyright)

### Graphics to Create
- Title card with framework name
- Lower thirds for speaker name
- Transition animations
- End card with CTA

---

## ESTIMATED TIMING

| Scene | Duration | Cumulative |
|-------|----------|------------|
| 1. Problem | 60s | 1:00 |
| 2. Solution | 90s | 2:30 |
| 3a. Load Data | 90s | 4:00 |
| 3b. Attribution | 90s | 5:30 |
| 3c. AI Interpretation | 3:00 | 8:30 |
| 3d. Uncertainty | 30s | 9:00 |
| 4. Differentiator | 90s | 10:30 |
| 5. CTA | 30s | 11:00 |

**Total: ~11 minutes (aim for 10:00-10:30)**

---

## KEY QUOTES FOR PROMOTION

1. "Not just attribution. A thinking instrument."
2. "Numbers without understanding is just noise."
3. "The only framework with built-in AI interpretation."
4. "First principles for marketing decisions."
5. "From correlation to causation to confidence."
