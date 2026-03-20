# Phase 7: Motion/Speed Service - COMPLETE ✅

## Overview

Phase 7 implements the **Motion/Speed Service** for calculating planet motion weights in Vedic astrology. This service determines the dynamic factor of each planet based on its speed and motion classification, with special focus on fast-moving planets.

---

## Features Implemented

### 1. Motion Classification

Planets are classified into motion types based on their speed:

**Motion Types:**
- **Fast**: Planet moving faster than normal (+10 points)
- **Stationary**: Planet nearly stationary, near station point (+15 points)
- **Slow**: Planet moving slower than normal (+5 points)
- **Normal**: Planet at average speed (0 points)
- **Retrograde**: Planet in retrograde motion (+10 points)

### 2. Significant Planets

Motion is most significant for **fast-moving planets**:

| Planet  | Significance | Reason                    |
|---------|--------------|---------------------------|
| Moon    | ✅ High      | Fastest planet (13°/day)  |
| Mars    | ✅ High      | Variable speed            |
| Mercury | ✅ High      | Variable speed            |
| Sun     | ❌ Low       | Consistent speed          |
| Venus   | ❌ Low       | Relatively consistent     |
| Jupiter | ❌ Low       | Very slow (0.08°/day)     |
| Saturn  | ❌ Low       | Very slow (0.03°/day)     |

**For non-significant planets**, motion weight defaults to baseline (50).

### 3. Motion Weight Calculation

Formula from `scoreLogic.md`:

```
W_motion(p) = 50 + motion_modifier(p)
```

**Motion Modifiers:**
- Fast: +10
- Stationary: +15
- Slow: +5
- Normal: 0
- Retrograde: +10

**Range:** 50-65
- Maximum: 65 (stationary)
- Typical: 50-60 (fast/retrograde)
- Baseline: 50 (normal or non-significant)

### 4. Data Models

Created in `api/models/motion.py`:

- **`MotionBreakdown`**: Detailed breakdown of motion components
- **`PlanetMotion`**: Complete motion calculation for a single planet
- **`MotionCalculation`**: Motion calculation for all planets at a specific time
- **`MotionRequest`**: API request model
- **`MotionResponse`**: API response model

### 5. Service Implementation

**File:** `api/services/motion_service.py`

**Key Methods:**
- `is_motion_significant(planet)` → bool
- `calculate_motion_breakdown(planet, transit_placement)` → MotionBreakdown
- `calculate_motion_weight(motion_modifier, is_significant)` → W_motion (0-100)
- `calculate_planet_motion(planet, transit_placement)` → PlanetMotion
- `calculate_chart_motions(natal_chart, calculation_date)` → MotionCalculation

**Integration:**
- Uses `TransitService` to get current planet positions and speeds
- Leverages existing motion classification from transit calculations

### 6. REST API Endpoints

**File:** `api/routes/motion.py`

**Endpoints:**

1. **POST `/motion/calculate`**
   - Calculate motions for a chart at a specific time
   - Request: `{ "chart_id": "...", "calculation_date": "..." }`
   - Response: Complete motion calculation

2. **GET `/motion/{chart_id}`**
   - Get motions for a specific chart at current time
   - Response: Complete motion calculation

3. **GET `/motion/{chart_id}/planet/{planet}`**
   - Get motion for a specific planet at current time
   - Response: PlanetMotion for that planet

---

## Example Usage

### 1. Calculate Motions for a Chart

```bash
curl -X POST http://localhost:8000/motion/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
    "calculation_date": "2026-03-20T12:00:00"
  }'
```

**Response:**
```json
{
  "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
  "motions": {
    "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
    "calculation_date": "2026-03-20T12:00:00",
    "planet_motions": {
      "Moon": {
        "planet": "Moon",
        "breakdown": {
          "speed": 14.5,
          "motion_type": "Fast",
          "motion_modifier": 10,
          "is_significant": true
        },
        "motion_weight": 60.0
      },
      "Mars": {
        "planet": "Mars",
        "breakdown": {
          "speed": -0.3,
          "motion_type": "Retrograde",
          "motion_modifier": 10,
          "is_significant": true
        },
        "motion_weight": 60.0
      },
      "Jupiter": {
        "planet": "Jupiter",
        "breakdown": {
          "speed": 0.08,
          "motion_type": "Normal",
          "motion_modifier": 0,
          "is_significant": false
        },
        "motion_weight": 50.0
      }
    }
  }
}
```

### 2. Get Motion for Current Time

```bash
curl http://localhost:8000/motion/04ecf146-d0e1-4e72-8c30-fb8bba03e2e5
```

### 3. Get Motion for Specific Planet

```bash
curl http://localhost:8000/motion/04ecf146-d0e1-4e72-8c30-fb8bba03e2e5/planet/Moon
```

---

## Implementation Details

### Motion Significance Logic

```python
SIGNIFICANT_PLANETS = {Planet.MOON, Planet.MARS, Planet.MERCURY}

def is_motion_significant(planet):
    return planet in SIGNIFICANT_PLANETS
```

### Motion Weight Examples

**Moon (Fast):**
- Speed: 14.5°/day (above normal 13.2°/day)
- Motion Type: Fast
- Modifier: +10
- Significant: Yes
- Weight: W_motion = 50 + 10 = **60.0**

**Mars (Retrograde):**
- Speed: -0.3°/day (negative = retrograde)
- Motion Type: Retrograde
- Modifier: +10
- Significant: Yes
- Weight: W_motion = 50 + 10 = **60.0**

**Mercury (Stationary):**
- Speed: 0.05°/day (nearly stationary)
- Motion Type: Stationary
- Modifier: +15
- Significant: Yes
- Weight: W_motion = 50 + 15 = **65.0**

**Jupiter (Normal, Not Significant):**
- Speed: 0.08°/day
- Motion Type: Normal
- Modifier: 0
- Significant: No
- Weight: W_motion = **50.0** (baseline for non-significant)

---

## Testing

**File:** `tests/test_motion_service.py`

**Test Coverage:**
- ✅ Service initialization
- ✅ Motion significance detection
- ✅ Motion breakdown (fast, stationary, retrograde, normal)
- ✅ Motion breakdown for non-significant planets
- ✅ Motion weight calculation (all motion types)
- ✅ Motion weight for non-significant planets
- ✅ Planet motion calculation
- ✅ Chart motions calculation
- ✅ Motion modifiers validation
- ✅ Motion weight bounds (50-65)
- ✅ Significant planets list validation

**Test Results:**
```bash
./venv/bin/python -m pytest tests/test_motion_service.py -v
# 16 passed in 2.75s
```

---

## Files Created/Modified

### Created Files:
1. ✅ `api/models/motion.py` - Motion data models
2. ✅ `api/services/motion_service.py` - Motion calculation service
3. ✅ `api/routes/motion.py` - REST API endpoints
4. ✅ `tests/test_motion_service.py` - Unit tests
5. ✅ `readme/PHASE7_COMPLETE.md` - This documentation

### Modified Files:
1. ✅ `api/models/__init__.py` - Export motion models
2. ✅ `main.py` - Register motion router

---

## Integration with Scoring Engine

The motion weight (`W_motion`) is one of five components in the planet influence model:

```
P(p, S_k) = W_dasha + W_transit + W_aspect + W_strength + W_motion
```

**Component Weights:**
- Dasha: 35%
- Transit: 25%
- Strength: 20%
- Aspect: 12%
- **Motion: 8%**

**Motion Impact:**

Motion represents the dynamic factor of a planet. Fast-moving or stationary planets have heightened influence, while slow-moving planets maintain baseline influence.

**Example:**
```
Moon (Fast): W_motion = 60
- Contributes 60 × 0.08 = 4.8 points to raw planet score

Jupiter (Normal, Not Significant): W_motion = 50
- Contributes 50 × 0.08 = 4.0 points to raw planet score
```

The difference is subtle (0.8 points) but meaningful for fast-moving planets like Moon, Mars, and Mercury.

---

## Next Steps: Phase 8

Phase 8 will implement the **Core Scoring Engine**:
- Orchestrate all services (dasha, transit, aspect, strength, motion)
- Calculate raw planet scores using weighted formula
- Normalize scores across all planets (sum to 100%)
- Calculate scores for time segments
- Aggregate across full time range

---

## Summary

✅ **Phase 7 Complete**

All motion/speed features are implemented and tested:
- ✅ Motion classification (fast, stationary, slow, normal, retrograde)
- ✅ Significance detection (Moon, Mars, Mercury)
- ✅ Motion weight calculation (W_motion, 50-65)
- ✅ Integration with transit service
- ✅ REST API endpoints (3 endpoints)
- ✅ Comprehensive unit tests (16 tests passing)
- ✅ Complete documentation

The motion service is ready for integration with the scoring engine in Phase 8.

