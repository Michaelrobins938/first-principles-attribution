# API Documentation - Attribution Matrix

## Base URL

```
http://localhost:8000
```

## Endpoints

### GET /api/v1/attribution/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "attribution-api"
}
```

---

### POST /api/v1/attribution/analyze

Run full attribution analysis on customer journeys.

**URL:** `/api/v1/attribution/analyze`

**Method:** `POST`

**Content-Type:** `application/json`

**Request Body:**

```json
{
  "journeys": [
    {
      "journey_id": "string",
      "path": [
        {
          "channel": "string",
          "timestamp": "string (ISO8601)",
          "context": "string"
        }
      ],
      "conversion": "boolean",
      "conversion_value": "number",
      "num_touchpoints": "integer",
      "duration_hours": "number"
    }
  ]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/attribution/analyze \
  -H "Content-Type: application/json" \
  -d @sample_journeys.json
```

**Example Response:**
```json
{
  "status": "success",
  "processing_time_ms": 0.8902000045054592,
  "total_journeys": 10,
  "total_conversions": 9,
  "unique_channels": 4,
  "markov_result": null,
  "shapley_result": null,
  "hybrid_result": {
    "channel_attributions": {
      "google": 0.1966155356396365,
      "facebook": 0.18549684906622158,
      "direct": 0.424138957478825,
      "email": 0.19374865781531692
    },
    "alpha_used": 0.5,
    "markov_weight": 0.5,
    "shapley_weight": 0.5,
    "confidence_intervals": {
      "google": {
        "low": 0.1466155356396365,
        "high": 0.24661553563963648
      },
      "facebook": {
        "low": 0.1354968490662216,
        "high": 0.23549684906622156
      },
      "direct": {
        "low": 0.374138957478825,
        "high": 0.47413895747882506
      },
      "email": {
        "low": 0.14374865781531693,
        "high": 0.2437486578153169
      }
    }
  },
  "channel_metrics": [
    {
      "channel": "google",
      "markov_contribution": 0.0,
      "shapley_value": 0.0,
      "hybrid_weighted": 0.0,
      "markov_confidence_low": 0.0,
      "markov_confidence_high": 0.0,
      "touchpoint_count": 8,
      "conversion_rate": 1.0,
      "avg_position": 0.2708333333333333
    }
  ],
  "channels_summary": {
    "google": 8,
    "facebook": 7,
    "direct": 10,
    "email": 6
  }
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "success" or "error" |
| `processing_time_ms` | number | Time taken to process (milliseconds) |
| `total_journeys` | integer | Number of journeys analyzed |
| `total_conversions` | integer | Number of converting journeys |
| `unique_channels` | integer | Number of unique touchpoint channels |
| `hybrid_result.channel_attributions` | object | Channel → attribution value mapping |
| `hybrid_result.alpha_used` | number | Hybrid blend parameter (default: 0.5) |
| `hybrid_result.confidence_intervals` | object | Lower/upper bounds for each channel |
| `channel_metrics` | array | Detailed metrics per channel |
| `channels_summary` | object | Touchpoint counts per channel |

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid JSON format"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "journeys", 0, "conversion"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Analysis failed: <error message>"
}
```

---

## Rate Limiting

No rate limiting is currently implemented for local development.

---

## Changelog

### v2.0.0 (2024-01-20)
- Added full API integration
- Implemented hybrid Markov-Shapley model
- Added confidence intervals
- Added channel metrics

### v1.0.0 (2024-12-12)
- Initial release
- Basic attribution engine
