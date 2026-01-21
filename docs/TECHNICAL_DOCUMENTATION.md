# Technical Documentation

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Backend Infrastructure](#backend-infrastructure)
4. [Frontend Application](#frontend-application)
5. [Core Attribution Engine](#core-attribution-engine)
6. [API Reference](#api-reference)
7. [Data Flow](#data-flow)
8. [Deployment](#deployment)
9. [Development Workflow](#development-workflow)
10. [Testing & Validation](#testing--validation)

---

## Architecture Overview

### High-Level System Design

The First-Principles Attribution Engine is a production-grade full-stack application combining rigorous mathematical foundations with modern web architecture:

**Architecture Layers:**

1. **Presentation Layer** - Next.js 15 + React 18 + TypeScript
2. **API Layer** - FastAPI (Python 3.11+) with RESTful endpoints
3. **Business Logic** - Attribution engines, UQ algorithms, LLM scaffold
4. **Data Layer** - JSON Schema validated artifacts, IR (Intermediate Representation)

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|----------|
| **Frontend** | Next.js 15, React 18, TypeScript | Server-side rendering, interactive dashboard |
| **Styling** | Tailwind CSS, shadcn/ui | Responsive design, component library |
| **Charts** | Recharts | Data visualization |
| **Backend** | FastAPI, Python 3.11+ | RESTful API, async processing |
| **Core Engine** | JavaScript (ES6+) | Attribution algorithms, Markov chains |
| **Statistics** | Marsaglia-Tsang Gamma, Box-Muller | Bayesian UQ, bootstrap resampling |
| **Validation** | JSON Schema Draft-07, Pydantic | Runtime type safety, data integrity |
| **LLM Layer** | System prompts, IR interpretation | AI-powered analysis generation |

---

## System Components

### Component Directory Structure

```
first-principles-attribution/
├── backend/                 # FastAPI backend
│   ├── api/                # REST API endpoints
│   │   ├── attribution.py  # Attribution endpoints
│   │   └── health.py       # Health check
│   ├── engines/            # Attribution algorithms
│   │   ├── markov.py       # Markov chain engine
│   │   ├── shapley.py      # Shapley value engine
│   │   └── hybrid.py       # Hybrid attribution
│   ├── models/             # Pydantic data models
│   ├── config.py           # Configuration
│   └── main.py             # FastAPI app
│
├── frontend/               # Next.js application
│   ├── app/                # App router (Next.js 15)
│   │   ├── page.tsx        # Home page
│   │   ├── dashboard/      # Attribution dashboard
│   │   └── api/            # API routes
│   ├── components/         # React components
│   ├── lib/                # Utilities
│   └── public/             # Static assets
│
├── src/                    # Core JavaScript engine
│   ├── attribution.js      # Main attribution engine
│   ├── dirichlet_uq_temp.js # Bayesian UQ
│   └── utils/              # Helper functions
│
├── llm-scaffold/           # LLM interpretation layer
│   ├── system-prompt.md    # LLM instructions
│   ├── ir-schema.json      # IR validation schema
│   └── templates/          # Output templates
│
├── docs/                   # Documentation
│   ├── WHITEPAPER.md       # Mathematical foundations (735 lines)
│   ├── USAGE.md            # User guide
│   ├── RELEASE_SUMMARY.md  # Version history
│   └── TECHNICAL_DOCUMENTATION.md  # This file
│
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── validation/         # Validation tests
│
└── examples/               # Sample data and outputs
    └── sample_attribution_result.json
```

---

## Backend Infrastructure

### FastAPI Application

**File:** `backend/main.py`

The backend is built with FastAPI, providing a high-performance, async RESTful API:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import attribution, health

app = FastAPI(
    title="First-Principles Attribution API",
    version="1.0.0",
    description="Enterprise-grade causal attribution engine"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(attribution.router, prefix="/api/v1")
app.include_router(health.router)
```

### API Endpoints

#### Attribution Endpoint

**Endpoint:** `POST /api/v1/attribution`

**Request Body:**
```json
{
  "events": [
    {"user_id": "user123", "timestamp": "2024-01-20T10:00:00Z", "channel": "Search", "value": 150},
    {"user_id": "user123", "timestamp": "2024-01-21T14:30:00Z", "channel": "Email", "value": 0},
    {"user_id": "user123", "timestamp": "2024-01-22T16:45:00Z", "channel": "Direct", "value": 0}
  ],
  "config": {
    "alpha": 0.5,
    "bootstrap_samples": 200,
    "confidence_level": 0.90
  }
}
```

**Response:**
```json
{
  "ir_version": "1.0.0",
  "hybrid_value": {
    "Search": 63.00,
    "Email": 37.50,
    "Direct": 27.00
  },
  "confidence_intervals": {
    "Search": {"p05": 38.46, "p50": 63.12, "p95": 87.21}
  },
  "rank_stability": {
    "Search": {"top1": 0.85, "top2": 0.98}
  },
  "metadata": {
    "timestamp": "2024-01-22T17:00:00Z",
    "total_paths": 1,
    "unique_channels": 3
  }
}
```

### Attribution Engines

The backend includes three core engines:

1. **Markov Chain Engine** (`engines/markov.py`)
   - Builds transition matrix from path data
   - Computes removal effects for causal analysis
   - Handles state-to-state probability transitions

2. **Shapley Value Engine** (`engines/shapley.py`)
   - Implements cooperative game theory
   - Computes marginal contributions
   - Ensures axiomatic fairness (efficiency, symmetry, null player)

3. **Hybrid Attribution Engine** (`engines/hybrid.py`)
   - Blends Markov and Shapley results
   - Tunable alpha parameter (0 to 1)
   - alpha=1: Pure causality, alpha=0: Pure fairness

---

## Frontend Application

### Next.js 15 Architecture

**File:** `frontend/app/page.tsx`

The frontend is a modern React application built with Next.js 15:

```typescript
import { AttributionDashboard } from '@/components/dashboard'

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-8">
        First-Principles Attribution Engine
      </h1>
      <AttributionDashboard />
    </main>
  )
}
```

### Key Frontend Features

1. **Interactive Dashboard** - Real-time attribution visualization
2. **Data Upload** - CSV, JSON, or manual entry
3. **Configuration Panel** - Adjust alpha, bootstrap samples, confidence levels
4. **Chart Library** - Recharts for responsive visualizations
5. **Responsive Design** - Tailwind CSS for mobile-first layouts

### Component Structure

```typescript
components/
├── dashboard/
│   ├── AttributionDashboard.tsx    # Main dashboard
│   ├── ConfigPanel.tsx             # Configuration UI
│   ├── ResultsView.tsx             # Attribution results
│   └── Charts.tsx                  # Recharts visualizations
├── ui/
│   ├── button.tsx                  # shadcn/ui button
│   ├── card.tsx                    # shadcn/ui card
│   └── input.tsx                   # shadcn/ui input
└── lib/
    └── api.ts                      # API client
```

---

## Core Attribution Engine

### JavaScript Engine Architecture

**File:** `src/attribution.js`

The core engine is implemented in pure JavaScript for performance and portability:

```javascript
class AttributionEngine {
  constructor(config = {}) {
    this.alpha = config.alpha || 0.5
    this.bootstrapSamples = config.bootstrap_samples || 200
    this.confidenceLevel = config.confidence_level || 0.90
  }

  // Main attribution pipeline
  async run(events) {
    const paths = this.buildPaths(events)
    const markovResults = this.computeMarkovAttribution(paths)
    const shapleyResults = this.computeShapleyValues(paths)
    const hybridResults = this.blendAttributions(markovResults, shapleyResults)
    const uncertainty = await this.computeUncertainty(paths)
    
    return this.createIRArtifact({
      hybrid: hybridResults,
      uncertainty,
      metadata: this.generateMetadata(paths)
    })
  }
}
```

### Markov Chain Implementation

**Key Concepts:**

1. **Transition Matrix Construction**
   - Counts state-to-state transitions
   - Normalizes to row-stochastic matrix
   - Ensures sum of each row = 1.0

2. **Removal Effect Calculation**
   - Computes conversion rate with full channel set: `P(conversion | N)`
   - Computes conversion rate without channel i: `P(conversion | N\\{i})`
   - Removal effect: `RE(i) = P(conversion | N) - P(conversion | N\\{i})`

3. **Causal Attribution**
   - Allocates credit proportional to removal effects
   - Guarantees: Efficiency (sum = total value)

### Shapley Value Implementation

**Key Concepts:**

1. **Coalition Enumeration**
   - Generates all subsets (coalitions) of channels
   - For n channels: 2^n coalitions
   - Practical limit: n ≤ 12 channels (enforced)

2. **Marginal Contribution**
   - For each coalition S, compute value v(S)
   - Marginal contribution of i: `v(S ∪ {i}) - v(S)`
   - Average across all coalitions

3. **Axiomatic Fairness**
   - **Efficiency:** Sum of shares = v(N)
   - **Symmetry:** Equal contributors get equal credit
   - **Null Player:** Zero contributors get zero credit
   - **Additivity:** Combines multiple games correctly

### Bayesian Uncertainty Quantification

**File:** `src/dirichlet_uq_temp.js`

**Dual UQ Framework:**

1. **Bootstrap UQ** - Measures path sampling uncertainty
   - Resamples paths with replacement
   - Recomputes attribution B times (B=200)
   - Computes percentiles (p05, p25, p50, p75, p95)

2. **Dirichlet UQ** - Measures transition parameter uncertainty
   - Samples from Dirichlet posterior
   - Uses Marsaglia-Tsang Gamma sampler
   - Provides 90% confidence intervals

**Result:** Combined uncertainty quantification with rank stability metrics

---

## Data Flow

### End-to-End Attribution Pipeline

```
1. User Input (Frontend)
   │
   ↓ HTTP POST /api/v1/attribution
   │
2. FastAPI Backend
   ├─ Validate request (Pydantic)
   ├─ Parse events
   └─ Call JavaScript engine
   │
3. Attribution Engine
   ├─ Build user paths
   ├─ Compute Markov attribution
   ├─ Compute Shapley values
   ├─ Blend with hybrid formula
   └─ Run Bootstrap + Dirichlet UQ
   │
4. IR Artifact Generation
   ├─ Format results as JSON
   ├─ Validate against JSON Schema
   └─ Add metadata (timestamp, version)
   │
5. Response (Backend → Frontend)
   │
6. Visualization (Frontend)
   ├─ Bar charts (attribution scores)
   ├─ Confidence intervals
   └─ Rank stability metrics
```

### IR (Intermediate Representation) Format

**JSON Schema:** `llm-scaffold/ir-schema.json`

All artifacts conform to a strict JSON Schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["ir_version", "hybrid_value", "confidence_intervals"],
  "properties": {
    "ir_version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
    "hybrid_value": {"type": "object"},
    "confidence_intervals": {"type": "object"},
    "rank_stability": {"type": "object"},
    "metadata": {"type": "object"}
  }
}
```

---

## Deployment

### Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Access:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Production Deployment

**Backend (Docker):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend (Vercel):**
```bash
cd frontend
npm run build
vercel --prod
```

### Environment Variables

**Backend** (`.env`):
```env
API_VERSION=1.0.0
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
LOG_LEVEL=INFO
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_VERSION=1.0.0
```

---

## Development Workflow

### Git Workflow

**Branches:**
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature branches
- `hotfix/*` - Critical fixes

**Commit Convention:**
```
feat: Add new attribution method
fix: Correct Shapley calculation
docs: Update technical documentation
test: Add unit tests for Markov engine
refactor: Optimize transition matrix computation
```

### Code Standards

**Backend (Python):**
- PEP 8 style guide
- Type hints for all functions
- Docstrings (Google style)

**Frontend (TypeScript):**
- ESLint + Prettier
- Strict TypeScript mode
- React best practices

**Core Engine (JavaScript):**
- ES6+ features
- JSDoc comments
- Functional programming style

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run Tests**
   ```bash
   npm test                    # Frontend
   pytest                      # Backend
   node tests/run.js           # Core engine
   ```

4. **Commit and Push**
   ```bash
   git commit -m "feat: Add my feature"
   git push origin feature/my-new-feature
   ```

5. **Create Pull Request**
   - Describe changes
   - Link related issues
   - Request review

6. **CI/CD Pipeline**
   - Automated tests
   - Linting checks
   - Build verification

---

## Testing & Validation

### Test Suite Architecture

```
tests/
├── unit/
│   ├── test_markov.py          # Markov engine tests
│   ├── test_shapley.py         # Shapley value tests
│   └── test_hybrid.py          # Hybrid attribution tests
│
├── integration/
│   ├── test_api.py             # API endpoint tests
│   └── test_pipeline.py        # End-to-end tests
│
└── validation/
    ├── test_invariants.py      # Mathematical guarantees
    ├── test_schema.py          # JSON Schema validation
    └── test_performance.py     # Performance benchmarks
```

### Unit Tests

**Example:** Markov Engine Test

```python
import pytest
from engines.markov import MarkovEngine

def test_transition_matrix_row_stochastic():
    """Test that transition matrix is row-stochastic."""
    engine = MarkovEngine()
    paths = [
        ["Search", "Email", "Direct"],
        ["Search", "Direct"]
    ]
    T = engine.build_transition_matrix(paths)
    
    # Each row should sum to 1.0
    for row in T:
        assert abs(sum(row) - 1.0) < 1e-6

def test_removal_effect():
    """Test removal effect calculation."""
    engine = MarkovEngine()
    paths = [["Search", "Conversion"]]
    
    # Removing Search should reduce conversion
    re_search = engine.compute_removal_effect(paths, "Search")
    assert re_search > 0
```

### Integration Tests

**Example:** API Endpoint Test

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_attribution_endpoint():
    """Test /api/v1/attribution endpoint."""
    response = client.post("/api/v1/attribution", json={
        "events": [
            {"user_id": "u1", "timestamp": "2024-01-20T10:00:00Z", "channel": "Search", "value": 100}
        ],
        "config": {"alpha": 0.5}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "ir_version" in data
    assert "hybrid_value" in data
    assert "confidence_intervals" in data
```

### Validation Tests

**Runtime Invariants:**

1. **Row-Stochastic Matrix**
   - Every row in transition matrix sums to 1.0
   - Tolerance: 1e-6

2. **Value Conservation**
   - Sum of attributed values = total conversion value
   - Tolerance: $1.00

3. **Quantile Ordering**
   - p05 ≤ p25 ≤ p50 ≤ p75 ≤ p95
   - Enforced at runtime

4. **Probability Bounds**
   - All probabilities in [0, 1]
   - Confidence levels in [0, 1]

### Performance Benchmarks

**Baseline (v1.0.0):**

| Operation | Channels | Runtime |
|-----------|----------|----------|
| Single attribution | 5 | <1s |
| Full robustness stack | 5 | ~15s |
| Bootstrap (B=200) | 5 | ~25s |
| Exact Shapley | 10 | ~5s |
| Exact Shapley | 12 | ~30s (limit) |

**Optimization Targets:**
- Reduce bootstrap time by 30%
- Support n ≤ 15 channels for Shapley
- Parallelize UQ computation

---

## Additional Resources

### Documentation

- **[WHITEPAPER.md](WHITEPAPER.md)** - Complete mathematical foundations (735 lines)
- **[USAGE.md](USAGE.md)** - Quick start guide and examples
- **[RELEASE_SUMMARY.md](RELEASE_SUMMARY.md)** - Version history and achievements

### External References

- **Markov Chains:** _Introduction to Probability Models_, Sheldon Ross
- **Shapley Values:** _The Shapley Value_, Lloyd Shapley (1953)
- **Bayesian UQ:** _Bayesian Data Analysis_, Gelman et al.
- **FastAPI:** [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **Next.js:** [https://nextjs.org/docs](https://nextjs.org/docs)

### Support

- **Issues:** [GitHub Issues](https://github.com/Michaelrobins938/first-principles-attribution/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Michaelrobins938/first-principles-attribution/discussions)

---

**Version:** 1.0.0  
**Last Updated:** January 2025  
**Maintainer:** Forsythe Publishing & Marketing
