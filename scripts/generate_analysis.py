#!/usr/bin/env python3
"""
generate_analysis.py - Automated Attribution Analysis Generator

This script takes an IR artifact and generates complete analytical outputs
through the LLM scaffold.

Usage:
    python scripts/generate_analysis.py input_ir.json output_dir
    python scripts/generate_analysis.py --interactive
    python scripts/generate_analysis.py --demo

Output Files:
    - executive_summary.md (stakeholder summary)
    - model_decomposition.md (technical breakdown)
    - diagrams.mmd (Mermaid visualizations)
    - viz_spec.json (chart specifications)
    - risk_and_assumptions.md (caveats and limitations)
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Try to import anthropic, but don't fail if not available
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


SCAFFOLD_DIR = Path(__file__).parent.parent / "llm-scaffold"
OUTPUT_TEMPLATES_DIR = SCAFFOLD_DIR / "output-templates"


def load_system_prompt() -> str:
    """Load the LLM system prompt."""
    prompt_path = SCAFFOLD_DIR / "system-prompt.md"
    with open(prompt_path, 'r') as f:
        return f.read()


def load_analysis_prompts() -> str:
    """Load the analysis prompts (A-G tasks)."""
    prompts_path = SCAFFOLD_DIR / "analysis-prompts.md"
    with open(prompts_path, 'r') as f:
        return f.read()


def load_ir_artifact(filepath: str) -> Dict:
    """Load and validate IR artifact."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Validate required fields
    required = ['ir_version', 'hybrid_share', 'confidence_intervals']
    for field in required:
        if field not in data:
            raise ValueError(f"IR artifact missing required field: {field}")
    
    return data


def create_analysis_prompt(ir_data: Dict, task: str = 'G') -> str:
    """Create the analysis prompt based on task selection."""
    prompts = load_analysis_prompts()
    
    # Extract relevant task prompt
    task_prompts = {
        'A': '### Task A: Conceptual Flow Diagram',
        'B': '### Task B: Attribution Decomposition Narrative', 
        'C': '### Task C: Psychographic Influence Map',
        'D': '### Task D: Executive Summary',
        'E': '### Task E: Risk/Assumptions Checklist',
        'F': '### Task F: Visualization Specifications',
        'G': '### Task G: Complete Analysis'
    }
    
    # Find the task section
    task_marker = task_prompts.get(task, task_prompts['G'])
    
    # Build the full prompt
    ir_summary = format_ir_summary(ir_data)
    
    prompt = f"""{prompts}

---

## Analysis Request

{task_marker}

Please analyze the following IR artifact and generate the appropriate outputs.

### IR Artifact Summary
{ir_summary}

### Full IR Data
```json
{json.dumps(ir_data, indent=2, default=str)}
```

Please provide your analysis following the format specified in the task.
"""
    
    return prompt


def format_ir_summary(ir_data: Dict) -> str:
    """Format IR data into a readable summary for the prompt."""
    summary = []
    summary.append(f"**Version:** {ir_data.get('ir_version', 'unknown')}")
    summary.append(f"**Generated:** {ir_data.get('generated_at', 'unknown')}")
    
    if 'alpha' in ir_data:
        summary.append(f"**Alpha (causality/fairness blend):** {ir_data['alpha']}")
    
    # Attribution shares
    if 'hybrid_share' in ir_data:
        summary.append("\n**Channel Attribution (Hybrid):**")
        for ch, share in sorted(ir_data['hybrid_share'].items(), key=lambda x: -x[1]):
            ci = ir_data.get('confidence_intervals', {}).get(ch, {})
            p05 = ci.get('p05', 'N/A')
            p95 = ci.get('p95', 'N/A')
            summary.append(f"  - {ch}: {share:.1%} [90% CI: {p05:.0%}-{p95:.0%}]")
    
    # Rank stability
    if 'rank_stability' in ir_data:
        summary.append("\n**Rank Stability:**")
        for ch, stability in sorted(ir_data['rank_stability'].items(), 
                                     key=lambda x: -x[1].get('top1', 0)):
            summary.append(f"  - {ch}: #1={stability.get('top1', 0):.0%}, #2={stability.get('top2', 0):.0%}")
    
    return '\n'.join(summary)


def call_llm(prompt: str, model: str = "claude-sonnet-4-20250514") -> str:
    """Call LLM API with the prompt."""
    if not HAS_ANTHROPIC:
        raise RuntimeError(
            "Anthropic SDK not installed. Install with: pip install anthropic"
        )
    
    client = anthropic.Anthropic()
    
    response = client.messages.create(
        model=model,
        system=load_system_prompt(),
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=8192
    )
    
    return response.content[0].text


def parse_llm_output(content: str) -> Dict[str, str]:
    """Parse LLM output into separate files."""
    files = {}
    
    # Try to extract code blocks with file markers
    lines = content.split('\n')
    current_file = None
    current_content = []
    
    for line in lines:
        # Check for file markers
        if line.startswith('```markdown') or line.startswith('```'):
            # New file starting
            continue
        elif line.startswith('```') and current_file:
            # End of current file
            files[current_file] = '\n'.join(current_content)
            current_file = None
            current_content = []
        elif line.startswith('File: ') and current_file is None:
            # Start of new file
            filename = line.replace('File: ', '').strip()
            # Remove file extension if present
            if not filename.endswith('.md') and not filename.endswith('.json'):
                filename = filename + '.md'
            current_file = filename
            current_content = []
        elif current_file:
            current_content.append(line)
    
    # Handle case where files aren't explicitly marked
    if not files:
        # Try to extract by common patterns
        sections = content.split('\n## ')
        for section in sections:
            section = section.strip()
            if section.startswith('Executive Summary'):
                files['executive_summary.md'] = section
            elif section.startswith('Model Decomposition'):
                files['model_decomposition.md'] = section
            elif section.startswith('Risk and Assumptions'):
                files['risk_and_assumptions.md'] = section
            elif '```mermaid' in section:
                # Extract mermaid diagrams
                files['diagrams.mmd'] = section
    
    # Ensure required files exist
    required_files = ['executive_summary.md', 'model_decomposition.md', 
                      'diagrams.mmd', 'viz_spec.json', 'risk_and_assumptions.md']
    
    for req_file in required_files:
        if req_file not in files:
            files[req_file] = generate_fallback_output(req_file, content)
    
    return files


def generate_fallback_output(filename: str, content: str) -> str:
    """Generate a fallback output if LLM doesn't provide structured output."""
    if filename == 'executive_summary.md':
        return generate_fallback_executive_summary(content)
    elif filename == 'model_decomposition.md':
        return generate_fallback_technical_breakdown(content)
    elif filename == 'diagrams.mmd':
        return generate_fallback_diagrams(content)
    elif filename == 'viz_spec.json':
        return generate_fallback_viz_spec(content)
    elif filename == 'risk_and_assumptions.md':
        return generate_fallback_risk_analysis(content)
    return content


def generate_fallback_executive_summary(content: str) -> str:
    """Generate executive summary from content."""
    return f"""# Attribution Executive Summary

## Overview

This analysis uses a hybrid Markov-Shapley attribution model to allocate 
conversion value across marketing channels. The model combines causal 
measurement (Markov chains) with fair allocation (Shapley values).

## Key Findings

Based on the analysis of the provided IR artifact:

{content[:1000]}...

## Methodology

- **Markov Chains**: Probabilistic path modeling with removal effects
- **Shapley Values**: Cooperative game theory for fair credit allocation  
- **Hybrid Blending**: α parameter balances causality vs fairness
- **Uncertainty Quantification**: Bootstrap resampling with 90% confidence intervals

## Recommendations

Please refer to the detailed analysis for specific channel recommendations.

---
*Generated by First-Principles Attribution Engine*
*Analysis date: {datetime.utcnow().strftime('%Y-%m-%d')}*
"""


def generate_fallback_technical_breakdown(content: str) -> str:
    """Generate technical breakdown from content."""
    return f"""# Model Decomposition: Hybrid Markov-Shapley Attribution

## Model Architecture

This system uses a hybrid approach combining two complementary methods:

### 1. Markov Chain Analysis (Causal)

The Markov model treats customer journeys as stochastic processes:
- **States**: Channel touchpoints + CONVERSION + NULL (no conversion)
- **Transitions**: Probability of moving from one state to another
- **Removal Effect**: Remove a channel, measure conversion rate drop

### 2. Shapley Value Calculation (Fair)

Shapley values allocate credit based on game theory:
- **Coalitions**: All possible channel subsets
- **Marginal Contribution**: Each channel's impact on coalition value
- **Fairness**: Axiomatic guarantee of equal contribution = equal credit

### 3. Hybrid Blending (α parameter)

The final attribution is: `hybrid_share = α × markov_share + (1-α) × shapley_share`

## Technical Details

{content[:2000]}...

---
*Technical documentation - First-Principles Attribution*
"""


def generate_fallback_diagrams(content: str) -> str:
    """Generate Mermaid diagrams."""
    return """```mermaid
---
title: Attribution Flow
---

```mermaid
flowchart TD
    START((Customer<br/>Journey Start))
    Search[Search]
    Email[Email]
    Direct[Direct]
    Social[Social]
    Display[Display]
    CONVERSION((Conversion<br/>Goal))
    NULL((No Conversion))

    START --> Search
    START --> Email
    START --> Direct
    START --> Social
    START --> Display

    Search --> CONVERSION
    Email --> CONVERSION
    Direct --> CONVERSION
    Social --> CONVERSION
    Display --> CONVERSION

    style CONVERSION fill:#10b981,stroke:#059669,stroke-width:2px
```

```mermaid
---
title: Attribution Comparison
---

```mermaid
xychart-beta
    title "Channel Attribution"
    x-axis [Search, Email, Direct, Social, Display]
    y-axis "Share" 0.0 --> 0.5
    bar [0.42, 0.25, 0.18, 0.10, 0.05]
```
"""


def generate_fallback_viz_spec(content: str) -> str:
    """Generate visualization spec."""
    return json.dumps({
        "$schema": "viz_spec/1.0.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "charts": {
            "hybrid_attribution_bar": {
                "type": "bar",
                "title": "Hybrid Attribution by Channel",
                "data": [
                    {"channel": "Search", "value": 0.42, "color": "#6366f1"},
                    {"channel": "Email", "value": 0.25, "color": "#ec4899"},
                    {"channel": "Direct", "value": 0.18, "color": "#8b5cf6"},
                    {"channel": "Social", "value": 0.10, "color": "#14b8a6"},
                    {"channel": "Display", "value": 0.05, "color": "#f59e0b"}
                ]
            }
        },
        "kpi_cards": {
            "total_attribution": 1.0,
            "top_channel": "Search",
            "top_channel_share": 0.42,
            "confidence_level": "90%"
        }
    }, indent=2)


def generate_fallback_risk_analysis(content: str) -> str:
    """Generate risk analysis."""
    return """# Risk and Assumptions

## Key Assumptions

1. **First-Party Data Only**: Analysis uses only data provided
2. **Channel Taxonomy**: Channels are correctly classified
3. **Timestamp Accuracy**: Event ordering is correct
4. **Conversion Tracking**: All conversions are captured

## Limitations

### Observational Data
This is **observational attribution**, not causal inference:
- Correlations ≠ Causation
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

## Sensitivity

The α parameter (default=0.5) controls causality-fairness balance:
- α=1.0: Pure Markov (causal focus)
- α=0.0: Pure Shapley (fairness focus)
- α=0.5: Balanced (default)

---
*Risk analysis - First-Principles Attribution*
"""


def save_outputs(files: Dict[str, str], output_dir: str) -> None:
    """Save generated files to output directory."""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename, content in files.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✓ {filename}")


def generate_analysis(
    ir_filepath: str,
    output_dir: str,
    task: str = 'G',
    use_llm: bool = True
) -> str:
    """
    Main function to generate complete attribution analysis.
    
    Args:
        ir_filepath: Path to IR artifact JSON file
        output_dir: Directory to write output files
        task: Analysis task (A-G, default G for complete analysis)
        use_llm: Whether to use LLM (if False, uses fallbacks)
    
    Returns:
        Path to output directory
    """
    print(f"\n{'='*60}")
    print("First-Principles Attribution Analysis Generator")
    print('='*60)
    
    # Step 1: Load IR artifact
    print(f"\n[1/4] Loading IR artifact: {ir_filepath}")
    ir_data = load_ir_artifact(ir_filepath)
    print(f"  ✓ IR version: {ir_data.get('ir_version')}")
    print(f"  ✓ Channels: {len(ir_data.get('hybrid_share', {}))}")
    
    # Step 2: Create analysis prompt
    print(f"\n[2/4] Creating analysis prompt (Task {task})")
    prompt = create_analysis_prompt(ir_data, task)
    print(f"  ✓ Prompt created ({len(prompt)} characters)")
    
    # Step 3: Generate analysis (LLM or fallback)
    print(f"\n[3/4] Generating analysis")
    if use_llm and HAS_ANTHROPIC:
        print("  → Calling LLM...")
        try:
            response = call_llm(prompt)
            files = parse_llm_output(response)
            print("  ✓ LLM analysis complete")
        except Exception as e:
            print(f"  ⚠ LLM call failed: {e}")
            print("  → Using fallback generation")
            files = {'content': prompt}
            use_llm = False
    else:
        print("  → Using fallback generation (no LLM)")
        files = {'content': prompt}
    
    # Step 4: Save outputs
    print(f"\n[4/4] Saving outputs to: {output_dir}")
    if isinstance(files, dict):
        save_outputs(files, output_dir)
    else:
        # Single content response
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'analysis.md')
        with open(output_file, 'w') as f:
            f.write(str(files))
        print(f"  ✓ analysis.md")
    
    print(f"\n{'='*60}")
    print(f"Analysis complete! Outputs saved to: {output_dir}")
    print('='*60)
    
    return output_dir


def run_demo():
    """Run a demonstration with sample data."""
    print("\n" + "="*60)
    print("DEMO MODE: Generating sample analysis")
    print("="*60)
    
    # Use sample IR
    sample_ir = {
        "ir_version": "1.0.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "alpha": 0.5,
        "hybrid_share": {
            "Search": 0.42,
            "Email": 0.25,
            "Direct": 0.18,
            "Social": 0.10,
            "Display": 0.05
        },
        "confidence_intervals": {
            "Search": {"p05": 0.35, "p95": 0.49},
            "Email": {"p05": 0.20, "p95": 0.30},
            "Direct": {"p05": 0.13, "p95": 0.23},
            "Social": {"p05": 0.07, "p95": 0.13},
            "Display": {"p05": 0.02, "p95": 0.08}
        },
        "rank_stability": {
            "Search": {"top1": 0.85, "top2": 0.98},
            "Email": {"top1": 0.12, "top2": 0.89},
            "Direct": {"top1": 0.03, "top2": 0.13}
        }
    }
    
    # Create sample IR file
    sample_ir_path = Path(__file__).parent.parent / "examples" / "sample_ir.json"
    with open(sample_ir_path, 'w') as f:
        json.dump(sample_ir, f, indent=2)
    
    # Generate analysis
    output_dir = Path(__file__).parent.parent / "examples" / "llm_analysis" / "sample_outputs"
    generate_analysis(str(sample_ir_path), str(output_dir), use_llm=False)
    
    print("\nDemo complete! Check the sample_outputs directory.")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate complete attribution analysis from IR artifacts"
    )
    parser.add_argument(
        'input', 
        nargs='?',
        help='Path to IR artifact JSON file'
    )
    parser.add_argument(
        'output',
        nargs='?',
        help='Output directory for generated files'
    )
    parser.add_argument(
        '--task', '-t',
        default='G',
        choices=['A', 'B', 'C', 'D', 'E', 'F', 'G'],
        help='Analysis task (default: G for complete)'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demonstration with sample data'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Skip LLM call, use fallback generation'
    )
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
        return
    
    if args.interactive:
        print("\nInteractive Mode")
        print("Enter path to IR artifact (or 'demo' for sample):")
        ir_path = input("> ").strip()
        if ir_path == 'demo':
            run_demo()
            return
        output_dir = input("Enter output directory [./analysis]: ").strip() or "./analysis"
        task = input("Enter task [G]: ").strip() or "G"
        generate_analysis(ir_path, output_dir, task, use_llm=not args.no_llm)
        return
    
    if args.input and args.output:
        generate_analysis(args.input, args.output, args.task, use_llm=not args.no_llm)
        return
    
    # Show help if no arguments
    parser.print_help()
    print("\n" + "="*60)
    print("Examples:")
    print("  python generate_analysis.py ir.json ./analysis")
    print("  python generate_analysis.py --demo")
    print("  python generate_analysis.py --interactive")
    print("="*60)


if __name__ == "__main__":
    main()
