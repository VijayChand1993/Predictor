# Phase 5: Aspect Calculation Service - COMPLETE ✅

## Overview

Phase 5 implements the **Aspect Calculation Service** (Drishti) for calculating planetary aspects in Vedic astrology. This service determines which houses each planet aspects and calculates the aspect weight contribution to the overall planet scoring.

---

## Features Implemented

### 1. Aspect Rules (Drishti)

Implements traditional Vedic astrology aspect rules:

**All Planets:**
- 7th house aspect (full aspect) - weight: 1.0

**Mars Special Aspects:**
- 4th house aspect - weight: 0.8
- 7th house aspect (full) - weight: 1.0
- 8th house aspect - weight: 0.8

**Jupiter Special Aspects:**
- 5th house aspect - weight: 0.8
- 7th house aspect (full) - weight: 1.0
- 9th house aspect - weight: 0.8

**Saturn Special Aspects:**
- 3rd house aspect - weight: 0.8
- 7th house aspect (full) - weight: 1.0
- 10th house aspect - weight: 0.8

### 2. Aspect Weight Calculation

Formula from `scoreLogic.md`:

```
W_aspect(p) = Σ [A(p→h) × AspectWeight × HouseWeight(h)] × 20
```

Where:
- `A(p→h)` = 1 if aspect exists, 0 otherwise
- `AspectWeight` = 1.0 for full aspect, 0.8 for special aspects
- `HouseWeight(h)` = Weight of the aspected house (Kendra: 1.0, Trikona: 0.9, etc.)
- Scaling factor: × 20

**Range:** 0-100 (typical range: 20-60)

### 3. Data Models

Created in `api/models/aspect.py`:

- **`Aspect`**: Single planetary aspect with type and weights
- **`PlanetAspects`**: All aspects cast by a single planet
- **`AspectCalculation`**: Complete aspect calculation for all planets
- **`AspectRequest`**: API request model
- **`AspectResponse`**: API response model

### 4. Service Implementation

**File:** `api/services/aspect_service.py`

**Key Methods:**
- `get_aspected_houses(planet, from_house)` → List of aspected houses with types
- `calculate_aspect_weight(planet, from_house)` → W_aspect (0-100)
- `calculate_planet_aspects(planet, from_house)` → PlanetAspects
- `calculate_chart_aspects(natal_chart)` → AspectCalculation

### 5. REST API Endpoints

**File:** `api/routes/aspect.py`

**Endpoints:**

1. **POST `/aspect/calculate`**
   - Calculate aspects for a chart
   - Request: `{ "chart_id": "..." }`
   - Response: Complete aspect calculation

2. **GET `/aspect/{chart_id}`**
   - Get aspects for a specific chart
   - Response: Complete aspect calculation

3. **GET `/aspect/{chart_id}/planet/{planet}`**
   - Get aspects for a specific planet
   - Response: PlanetAspects for that planet

---

## Example Usage

### 1. Calculate Aspects for a Chart

```bash
curl -X POST http://localhost:8000/aspect/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "chart_id": "b81cc292-aeed-4264-b34e-37be8db92e5e"
  }'
```

**Response:**
```json
{
  "chart_id": "b81cc292-aeed-4264-b34e-37be8db92e5e",
  "aspects": {
    "chart_id": "b81cc292-aeed-4264-b34e-37be8db92e5e",
    "planet_aspects": {
      "Jupiter": {
        "planet": "Jupiter",
        "from_house": 1,
        "aspects": [
          {
            "from_planet": "Jupiter",
            "to_house": 7,
            "aspect_type": "Full",
            "aspect_weight": 1.0,
            "house_weight": 1.0
          },
          {
            "from_planet": "Jupiter",
            "to_house": 5,
            "aspect_type": "Special Jupiter",
            "aspect_weight": 0.8,
            "house_weight": 0.9
          },
          {
            "from_planet": "Jupiter",
            "to_house": 9,
            "aspect_type": "Special Jupiter",
            "aspect_weight": 0.8,
            "house_weight": 0.9
          }
        ],
        "aspect_weight": 48.8
      }
    }
  }
}
```

### 2. Get Aspects for Specific Planet

```bash
curl http://localhost:8000/aspect/b81cc292-aeed-4264-b34e-37be8db92e5e/planet/Jupiter
```

---

## Implementation Details

### House Calculation Logic

Aspects are calculated relative to the planet's house position:

```python
def calc_house(from_house: int, offset: int) -> int:
    """Calculate aspected house with proper wrapping (1-12)."""
    return ((from_house - 1 + offset) % 12) + 1
```

**Examples:**
- Planet in house 1, 7th aspect → house 7
- Planet in house 10, 7th aspect → house 4
- Jupiter in house 1, 5th aspect → house 5
- Jupiter in house 10, 5th aspect → house 2

### Aspect Weight Examples

**Jupiter in House 1 (Kendra):**
- Aspects houses: 5 (Trikona), 7 (Kendra), 9 (Trikona)
- Weight = (0.8 × 0.9 + 1.0 × 1.0 + 0.8 × 0.9) × 20
- Weight = (0.72 + 1.0 + 0.72) × 20 = 48.8

**Saturn in House 10 (Kendra):**
- Aspects houses: 12 (Dusthana), 4 (Kendra), 7 (Kendra)
- Weight = (0.8 × 0.6 + 1.0 × 1.0 + 0.8 × 1.0) × 20
- Weight = (0.48 + 1.0 + 0.8) × 20 = 45.6

**Sun in House 5 (Trikona):**
- Aspects house: 11 (Upachaya)
- Weight = (1.0 × 0.8) × 20 = 16.0

---

## Testing

**File:** `tests/test_aspect_service.py`

**Test Coverage:**
- ✅ Service initialization
- ✅ All planets aspect 7th house
- ✅ Mars special aspects (4th, 8th)
- ✅ Jupiter special aspects (5th, 9th)
- ✅ Saturn special aspects (3rd, 10th)
- ✅ Aspect type assignment
- ✅ House number wrapping (1-12)
- ✅ Aspect weight calculation
- ✅ Planet aspects calculation
- ✅ Chart aspects calculation
- ✅ Aspect weight range validation
- ✅ All planets have at least one aspect
- ✅ Special planets have 3 aspects
- ✅ Regular planets have only 7th aspect

**Test Results:**
```bash
./venv/bin/python -m pytest tests/test_aspect_service.py -v
# 14 passed in 0.22s
```

---

## Files Created/Modified

### Created Files:
1. ✅ `api/models/aspect.py` - Aspect data models
2. ✅ `api/services/aspect_service.py` - Aspect calculation service
3. ✅ `api/routes/aspect.py` - REST API endpoints
4. ✅ `tests/test_aspect_service.py` - Unit tests
5. ✅ `readme/PHASE5_COMPLETE.md` - This documentation

### Modified Files:
1. ✅ `api/models/__init__.py` - Export aspect models
2. ✅ `main.py` - Register aspect router

---

## Integration with Scoring Engine

The aspect weight (`W_aspect`) is one of five components in the planet influence model:

```
P(p, S_k) = W_dasha + W_transit + W_aspect + W_strength + W_motion
```

**Component Weights:**
- Dasha: 35%
- Transit: 25%
- Strength: 20%
- **Aspect: 12%**
- Motion: 8%

**House Distribution:**

Aspect contribution is distributed to aspected houses:
- 20% of planet's total score is distributed equally among aspected houses

**Example:**
```
Saturn with P(Saturn) = 34:
- Aspected houses (5th, 9th, 12th): 34 × 0.20 / 3 = 2.27 each
```

---

## Next Steps: Phase 6

Phase 6 will implement the **Planet Strength Service**:
- Calculate dignity score (exalted, own, friendly, etc.)
- Check retrograde status
- Check combustion (proximity to Sun)
- Combine into strength score
- Calculate W_strength component

---

## Summary

✅ **Phase 5 Complete**

All aspect calculation features are implemented and tested:
- ✅ Aspect rules for all planets (7th house)
- ✅ Special aspects for Mars, Jupiter, Saturn
- ✅ Aspect weight calculation (W_aspect)
- ✅ REST API endpoints (3 endpoints)
- ✅ Comprehensive unit tests (14 tests passing)
- ✅ Complete documentation

The aspect service is ready for integration with the scoring engine in later phases.

