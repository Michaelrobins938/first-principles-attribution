# First-Principles Hybrid Attribution Engine

## 🎖️ Attribution Matrix v2.0 — "Tactical Intelligence Release"

A military-grade behavioral intelligence platform combining Markov-Shapley attribution with Kelley's Covariation Model. Features a tactical carbon-fiber interface for precision analytics.

![Attribution Matrix](docs/images/First-Principles_Attribution_Engine_GitHub_banner_with_gradient_background,_network_visualization,_and_technical_badges%20(1).png)

---

## 🎯 Core Capabilities

1. **Hybrid Attribution**: Markov Chain causality + Shapley Value fairness
2. **Behavioral Covariation**: Dispositional vs Situational tagging via Kelley
3. **Tactical Dashboard**: Carbon-fiber UI with amber accents
4. **Full-Stack Integration**: Next.js frontend + FastAPI backend

---

## 🚀 Quick Start

### 1. Start the Backend

```powershell
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 2. Start the Frontend

```powershell
cd frontend
npm run dev
```

### 3. Access the Platform

- **Dashboard**: http://localhost:3002
- **API Docs**: http://localhost:8000/docs

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ATTRIBUTION MATRIX                        │
├─────────────────────────────────────────────────────────────┤
│  FRONTEND (Next.js)          │  BACKEND (FastAPI)           │
│  ├── Tactical Theme          │  ├── /api/v1/attribution     │
│  ├── File Upload             │  │   └── /analyze            │
│  ├── Charts (Recharts)       │  ├── Attribution Engine      │
│  └── Loading States          │  │   ├── Markov Chains       │
│                              │  │   ├── Shapley Values      │
│                              │  │   └── Hybrid Blend        │
│                              │  └── Covariation Engine      │
│                              │      └── Kelley's Model      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 API Endpoints

### Analyze Attribution

```bash
curl -X POST http://localhost:8000/api/v1/attribution/analyze \
  -H "Content-Type: application/json" \
  -d @frontend/app/public/sample_journeys.json
```

**Response:**
```json
{
  "status": "success",
  "hybrid_result": {
    "channel_attributions": {
      "direct": 0.424,
      "google": 0.197,
      "email": 0.194,
      "facebook": 0.185
    },
    "alpha_used": 0.5,
    "confidence_intervals": {...}
  }
}
```

---

## 📁 Project Structure

```
first-principles-attribution/
├── frontend/                    # Next.js Tactical Dashboard
│   ├── app/
│   │   ├── page.tsx            # Main dashboard
│   │   ├── AttributionCharts.tsx
│   │   ├── BehavioralTags.tsx
│   │   ├── LLMReports.tsx
│   │   ├── FileUpload.tsx
│   │   └── public/
│   │       └── sample_journeys.json
│   ├── tailwind.config.js
│   └── package.json
│
├── backend/                     # FastAPI Backend
│   ├── main.py                 # API entry point
│   ├── api/router.py           # Attribution endpoints
│   └── engines/attribution/
│       ├── engine.py           # Markov-Shapley hybrid
│       └── covariation.py      # Kelley's Model
│
├── lib/
│   └── attribution.js          # JavaScript reference
│
├── llm-scaffold/               # LLM Interpretation Layer
├── docs/images/                # Visual assets
└── logs/                       # Documentation
```

---

## 🧮 Mathematical Foundation

### Hybrid Attribution Model

**Hybrid Value (α)**:
```
V_hybrid = α × V_markov + (1-α) × V_shapley
```

Where:
- `V_markov`: Channel contribution via state transition probabilities
- `V_shapley`: Fair credit via cooperative game theory
- `α`: User-controlled blend (default: 0.5)

### Uncertainty Quantification

- **Bootstrap Resampling**: 10,000 iterations
- **Confidence Intervals**: 90% CI on all attributions
- **Rank Stability**: Measured via Dirichlet sampling

### Behavioral Covariation (Kelley)

| Metric | Description |
|--------|-------------|
| **Consensus** | Do others behave the same in this situation? |
| **Distinctiveness** | Is this behavior unique to this situation? |
| **Consistency** | Does this behavior repeat across situations? |

**Classification**:
- `[DISPOSITIONAL]` = High Consistency + Low Distinctiveness
- `[SITUATIONAL]` = Low Consistency + High Consensus

---

## 🎨 Tactical Theme

The frontend features a unique carbon-fiber aesthetic:

- **Background**: Pure black with carbon fiber texture
- **Accents**: Amber (#f59e0b) for tactical highlights
- **Typography**: Monospace (SFMono-Regular) for precision
- **No Gradients**: Flat, military-grade design
- **No Rounded Corners**: Sharp edges only

---

## 📦 Sample Data

Test with `frontend/app/public/sample_journeys.json`:

```json
{
  "journeys": [
    {
      "journey_id": "j001",
      "path": [
        {"channel": "facebook", "timestamp": "2024-01-15T10:00:00Z", "context": "social_feed"},
        {"channel": "google", "timestamp": "2024-01-15T10:15:00Z", "context": "search"},
        {"channel": "direct", "timestamp": "2024-01-15T10:30:00Z", "context": "direct_visit"}
      ],
      "conversion": true,
      "conversion_value": 150.00
    }
  ]
}
```

---

## 🔒 Privacy-First Design

- **Zero Cloud Storage**: All processing is local
- **File-system Sandboxing**: Data never leaves your machine
- **No External API Calls**: Complete offline capability
- **Schema-Validated**: All inputs verified before processing

---

## 📄 License & Credits

- **Status**: v2.0 — Production Ready
- **License**: MIT
- **Repository**: https://github.com/Michaelrobins938/first-principles-attribution

---

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel deploy
```

### Backend (Railway/Render)
```bash
cd backend
railway up
```

### Docker
```bash
docker-compose up --build
```
