# Level 7: AI Agricultural Decision Support System — API Reference

**Endpoint**: `POST /api/v1/decision/recommend`  
**Authentication**: Optional (`Bearer <JWT>` for automated user audit logging)  
**Content-Type**: `application/json`

---

## 1. Request Payload Specification

```json
{
  "N": 90.0,
  "P": 42.0,
  "K": 43.0,
  "temperature": 20.9,
  "humidity": 82.0,
  "ph": 6.5,
  "rainfall": 202.9,
  "state": "Punjab",
  "district": "Ludhiana",
  "season": "Rabi",
  "area": 10.0,
  "crop_year": 2024,
  "market": "Azadpur",
  "forecast_horizon": 7,
  "historical_prices": [2150.0, 2180.0, 2200.0, 2210.0, 2230.0, 2225.0, 2240.0]
}
```

### Parameter Field Definitions:

| Parameter | Type | Required | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `N` | Float | Yes | $0 \le N \le 200$ | Soil Nitrogen ratio (mg/kg) |
| `P` | Float | Yes | $0 \le P \le 200$ | Soil Phosphorus ratio (mg/kg) |
| `K` | Float | Yes | $0 \le K \le 250$ | Soil Potassium ratio (mg/kg) |
| `temperature` | Float | Yes | $0 \le T \le 60$ | Ambient temperature in °C |
| `humidity` | Float | Yes | $0 \le H \le 100$ | Relative humidity percentage |
| `ph` | Float | Yes | $3.0 \le \text{pH} \le 10.0$ | Soil pH acidity/alkalinity measure |
| `rainfall` | Float | Yes | $0 \le R \le 500$ | Annual rainfall in mm |
| `state` | String | Yes | Valid Indian State | Cultivation State |
| `district` | String | Yes | $\ge 2$ chars | Cultivation District |
| `season` | String | Yes | Kharif, Rabi, Summer, Autumn, Winter, Whole Year | Cropping Season |
| `area` | Float | Yes | $> 0.0$ | Land acreage in Hectares |
| `crop_year` | Integer | No | $1990 \le \text{Year} \le 2050$ (Default: 2024) | Target crop calendar year |
| `market` | String | No | Mandi name (Default: Azadpur) | Target wholesale market |
| `forecast_horizon` | Integer | No | $1 \le \text{days} \le 30$ (Default: 7) | Price projection horizon |
| `historical_prices` | Array[Float] | No | Optional price series | Historical baseline for price LSTM |

---

## 2. Response Payload Specification

```json
{
  "success": true,
  "data": {
    "recommended_crop": "wheat",
    "decision_score": 88.5,
    "crop_confidence": 0.962,
    "suitability_score": 96.2,
    "predicted_yield": 4.52,
    "yield_score": 90.4,
    "estimated_production_tonnes": 45.2,
    "market": "Azadpur",
    "forecast_price": 2245.0,
    "market_score": 82.3,
    "price_trend": "UPWARD",
    "forecast_horizon_days": 7,
    "alternatives": [
      {
        "rank": 1,
        "crop": "wheat",
        "decision_score": 88.5,
        "suitability_probability": 0.962,
        "suitability_score": 96.2,
        "predicted_yield_tonnes_per_hectare": 4.52,
        "yield_score": 90.4,
        "forecasted_market_price": 2245.0,
        "market_score": 82.3,
        "price_trend": "UPWARD"
      },
      {
        "rank": 2,
        "crop": "rice",
        "decision_score": 75.2,
        "suitability_probability": 0.820,
        "suitability_score": 82.0,
        "predicted_yield_tonnes_per_hectare": 3.10,
        "yield_score": 62.0,
        "forecasted_market_price": 1980.0,
        "market_score": 71.0,
        "price_trend": "STABLE"
      }
    ],
    "explanation": {
      "summary": "Wheat is the top-ranked recommendation with a holistic decision score of 88.5/100, showing strong soil compatibility, favorable agro-climatic conditions, high yield potential (4.52 t/ha), and a UPWARD price trend in Azadpur.",
      "soil_compatibility": "Soil NPK profile (N: 90, P: 42, K: 43) and pH (6.5) are well-aligned with the nutrient absorption requirements of Wheat.",
      "climatic_suitability": "Current temperature (20.9°C), humidity (82.0%), and rainfall (202.9 mm) are optimal for the vegetative and reproductive phases of Wheat.",
      "yield_potential": "Projected yield is 4.52 t/ha, delivering an estimated total harvest of 45.2 Tonnes across 10.0 Hectares in Ludhiana, Punjab.",
      "market_outlook": "7-day modal price forecast in Azadpur is ₹2245.00/quintal with a UPWARD trend trajectory.",
      "key_advantages": [
        "High biological suitability probability of 96.2%",
        "Predicted yield of 4.52 t/ha (45.2 Tonnes total output)",
        "Favorable market valuation of ₹2245.00/quintal with UPWARD trend"
      ]
    },
    "execution_time_ms": 18.5
  },
  "error": null,
  "timestamp": "2026-09-12T12:20:00Z"
}
```

---

## 3. HTTP Status Codes & Error Responses

| Status Code | Reason | Example Response |
| :--- | :--- | :--- |
| `200 OK` | Successful multi-modal inference | See above response format |
| `422 Unprocessable Content` | Validation failure (e.g., negative pH, N > 200) | `{"detail": [{"loc": ["body", "ph"], "msg": "Input should be greater than or equal to 3.0"}]}` |
| `500 Internal Server Error` | Backend execution exception | `{"success": false, "error": {"code": "DECISION_ERROR", "message": "Failed to synthesize models"}}` |
