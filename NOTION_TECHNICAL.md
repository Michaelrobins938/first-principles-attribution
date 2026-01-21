# Technical Documentation - Attribution Matrix

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ATTRIBUTION MATRIX                        │
├─────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────┐    ┌────────────────────┐            │
│  │   FRONTEND         │    │   BACKEND          │            │
│  │   (Next.js 14)     │    │   (FastAPI)        │            │
│  │                    │    │                    │            │
│  │  • Tactical UI     │◄──►│  • Attribution     │            │
│  │  • File Upload     │    │    Engine          │            │
│  │  • Recharts        │    │  • Markov Chains   │            │
│  │  • State Mgmt      │    │  • Shapley Values  │            │
│  └────────────────────┘    │  • Covariation     │            │
│                            │    (Kelley's)      │            │
│                            └────────────────────┘            │
│                                      │                        │
│                            ┌─────────▼─────────┐             │
│                            │   Python Engines  │             │
│                            │   • numpy         │             │
│                            │   • scipy.stats   │             │
│                            │   • pydantic      │             │
│                            └───────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Specifications

### Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Next.js | 14.2.35 | React framework |
| React | 18.3.1 | UI library |
| Tailwind CSS | 3.4.1 | Styling |
| Recharts | 2.12.2 | Data visualization |
| Lucide React | 0.344.0 | Icons |

### Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Main dashboard (12KB)
│   ├── layout.tsx            # Root layout
│   ├── globals.css           # Tactical theme
│   ├── AttributionCharts.tsx # Chart components
│   ├── BehavioralTags.tsx    # Kelley covariation
│   ├── LLMReports.tsx        # AI reports
│   ├── FileUpload.tsx        # Drag-drop upload
│   ├── LoadingState.tsx      # Tactical loader
│   └── public/
│       └── sample_journeys.json
├── tailwind.config.js        # Theme configuration
├── postcss.config.js         # CSS pipeline
├── next.config.js            # Next.js config
└── package.json              # Dependencies
```

### Tactical Theme Design

**Color Palette:**
```css
--background: #000000
--foreground: #f4f4f5 (zinc-100)
--amber: #f59e0b (amber-500)
--zinc-800: #27272a
--zinc-900: #18181b
```

**Custom Classes:**
- `.carbon-plate` — Dark panel with backdrop blur
- `.carbon-fiber` — Carbon fiber texture background
- `.tactical-grid` — Grid overlay pattern
- `.scanlines` — CRT scanline effect

---

## Backend Specifications

### Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| FastAPI | 0.109+ | API framework |
| Uvicorn | 0.27+ | ASGI server |
| Pydantic | 2.5+ | Data validation |
| NumPy | 1.26+ | Numerical computing |
| SciPy | 1.11+ | Statistical functions |

### API Endpoints

#### POST /api/v1/attribution/analyze

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/attribution/analyze \
  -H "Content-Type: application/json" \
  -d @sample_journeys.json
```

**Request Body:**
```json
{
  "journeys": [
    {
      "journey_id": "string",
      "path": [
        {
          "channel": "string",
          "timestamp": "ISO8601",
          "context": "string"
        }
      ],
      "conversion": true,
      "conversion_value": 0.0,
      "num_touchpoints": 0,
      "duration_hours": 0
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "processing_time_ms": 0.89,
  "total_journeys": 10,
  "total_conversions": 9,
  "unique_channels": 4,
  "hybrid_result": {
    "channel_attributions": {
      "direct": 0.424,
      "google": 0.197,
      "email": 0.194,
      "facebook": 0.185
    },
    "alpha_used": 0.5,
    "markov_weight": 0.5,
    "shapley_weight": 0.5,
    "confidence_intervals": {
      "direct": {"low": 0.374, "high": 0.474},
      "google": {"low": 0.147, "high": 0.247}
    }
  },
  "channel_metrics": [...],
  "channels_summary": {...}
}
```

---

## Mathematical Models

### 1. Markov Chain Attribution

**Transition Matrix (T):**
```
T[i][j] = P(transition from state i to state j)
```

**Removal Impact:**
```
RI_k = (C_total - C_without_k) / C_total
```

### 2. Shapley Value Attribution

**Formula:**
```
φ_i = Σ (S⊆N\{i}) [|S|! (n-|S|-1)! / n!] × [v(S∪{i}) - v(S)]
```

### 3. Hybrid Blend

```
V_hybrid = α × V_markov + (1-α) × V_shapley
```

Default: α = 0.5

### 4. Kelley's Covariation Model

**Consensus:**
```
Consensus = Behavior_occurs / Situation_occurs
```

**Distinctiveness:**
```
Distinctiveness = Situation_specific / Total_situations
```

**Consistency:**
```
Consistency = Same_behavior_across_situations
```

**Classification:**
- `[DISPOSITIONAL]` = High Consistency + Low Distinctiveness
- `[SITUATIONAL]` = Low Consistency + High Consensus

---

## Data Flow

```
1. USER UPLOAD
   frontend/app/public/sample_journeys.json
         │
         ▼
2. FRONTEND (Next.js)
   - Parse JSON file
   - Validate format
   - Send to API
         │
         ▼
3. BACKEND (FastAPI)
   - Validate request body
   - Parse journeys
         │
         ▼
4. ATTRIBUTION ENGINE
   - Build transition matrix
   - Calculate Markov contributions
   - Compute Shapley values
   - Apply hybrid blend
         │
         ▼
5. COVARIATION ENGINE
   - Tag behaviors (DISPOSITIONAL/SITUATIONAL)
         │
         ▼
6. RESPONSE
   - Return IR artifact
   - Channel attributions
   - Confidence intervals
```

---

## Uncertainty Quantification

### Bootstrap Resampling

- **Iterations**: 10,000
- **Confidence Level**: 90%
- **Output**: Lower/Upper bounds for each channel

### Validation Checks

| Check | Method |
|-------|--------|
| Sum-to-one | `Σ attributions = 1.0` |
| Symmetry | `φ_i(coalition) = φ_j(coalition)` |
| Rank Stability | Dirichlet sampling |

---

## Setup Instructions

### Prerequisites

```bash
# Frontend
node >= 18.0.0
npm >= 9.0.0

# Backend
python >= 3.10
pip >= 23.0
```

### Installation

```bash
# Frontend
cd frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
```

### Running

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Testing

```bash
# API health check
curl http://localhost:8000/api/v1/attribution/health

# Full analysis
curl -X POST http://localhost:8000/api/v1/attribution/analyze \
  -H "Content-Type: application/json" \
  -d @frontend/app/public/sample_journeys.json
```
