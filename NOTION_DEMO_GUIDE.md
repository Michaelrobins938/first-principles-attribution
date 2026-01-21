# Demo Guide - Attribution Matrix

## Quick Demo (60 seconds)

### Step 1: Start the System

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 2: Open Dashboard

Navigate to: **http://localhost:3002**

You should see:
- Black carbon fiber background
- Amber "SYSTEM ONLINE" indicator
- "ATTRIBUTION MATRIX" header
- File upload zone with tactical borders

### Step 3: Upload Sample Data

1. Click the file upload zone
2. Select: `frontend/app/public/sample_journeys.json`
3. Watch the loading animation

### Step 4: View Results

After analysis completes, you'll see:
- **Attribution Charts**: Bar chart of channel contributions
- **Behavioral Tags**: DISPOSITIONAL/SITUATIONAL labels
- **AI Reports**: Generated intelligence summary

---

## What to Demonstrate

### 1. The Tactical Interface (10 seconds)
- Point out the carbon fiber texture
- Highlight the amber accents
- Note the monospace typography
- "No rounded corners, no gradients"

### 2. The Upload Flow (10 seconds)
- Drag and drop the sample file
- Show the tactical loading state
- "Processing happens locally"

### 3. Attribution Results (20 seconds)
- Point to the channel breakdown:
  - Direct: 42.4%
  - Google: 19.7%
  - Email: 19.4%
  - Facebook: 18.5%
- Show the confidence intervals
- "Markov-Shapley hybrid with 90% CI"

### 4. Behavioral Analysis (10 seconds)
- Highlight the Kelley covariation tags
- "Dispositional vs Situational behaviors"
- Explain the classification logic

### 5. API Integration (10 seconds)
- Show the curl command
- "Full-stack integration tested end-to-end"
- Backend returns JSON, frontend renders charts

---

## Demo Data Format

The sample file contains 10 journeys:

```json
{
  "journeys": [
    {
      "journey_id": "j001",
      "path": [
        {"channel": "facebook", "timestamp": "2024-01-15T10:00:00Z", "context": "social_feed"},
        {"channel": "google", "timestamp": "2024-01-15T10:15:00Z", "context": "search"},
        {"channel": "direct", "timestamp": "2024-01-15T10:30:00Z", "context": "direct_visit"},
        {"channel": "email", "timestamp": "2024-01-16T09:00:00Z", "context": "newsletter"},
        {"channel": "direct", "timestamp": "2024-01-16T14:00:00Z", "context": "bookmark"}
      ],
      "conversion": true,
      "conversion_value": 150.00,
      "num_touchpoints": 5,
      "duration_hours": 28
    }
  ]
}
```

**Statistics:**
- Total journeys: 10
- Conversions: 9 (90% rate)
- Unique channels: 4

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Frontend won't start | `cd frontend && rm -rf .next && npm run dev` |
| Backend won't start | `cd backend && pip install -r requirements.txt` |
| CORS errors | Ensure backend is running on port 8000 |
| No data showing | Check browser console for errors |

---

## Key Talking Points

1. **Privacy-First**: "All processing is local. No data leaves your machine."

2. **Mathematically Rigorous**: "Markov Chains + Shapley Values = Fair attribution."

3. **Unique Design**: "Carbon fiber aesthetic. Military-grade precision."

4. **Full-Stack Ready**: "Next.js frontend + FastAPI backend. Production-ready."

5. **Open Source**: "MIT license. Deploy anywhere."

---

## Post-Demo Questions

**Q: Can this handle large datasets?**
A: Currently optimized for 100-10,000 journeys. Larger datasets need Redis caching.

**Q: How does it compare to Google Analytics?**
A: GA uses data-driven models. We use first-principles Markov-Shapley.

**Q: Can I deploy this to production?**
A: Yes. Frontend to Vercel, Backend to Railway/Render.

**Q: What's the accuracy?**
A: Uncertainty quantified via bootstrap resampling (10,000 iterations).
