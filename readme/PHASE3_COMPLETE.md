# Phase 3: Dasha Calculation Service ✅ COMPLETE

## Overview
Phase 3 has been successfully implemented. The Dasha Calculation Service can now calculate Vimshottari dasha periods, identify active dashas for any date, and calculate dasha weights for scoring purposes.

## What Was Implemented

### 1. Dasha Data Models (`api/models/dasha.py`)

#### DashaPeriod
Represents a single Vimshottari dasha period at any level:
```python
class DashaPeriod(BaseModel):
    planet: Planet              # Planet ruling this period
    start_date: Date           # Start date
    end_date: Date             # End date
    level: str                 # 'mahadasha', 'antardasha', 'pratyantar', 'sookshma'
```

#### ActiveDashas
Active dasha periods at a specific point in time:
```python
class ActiveDashas(BaseModel):
    date: Date                          # Date for calculation
    mahadasha: DashaPeriod             # Current Mahadasha
    antardasha: DashaPeriod            # Current Antardasha
    pratyantar: Optional[DashaPeriod]  # Current Pratyantar
    sookshma: Optional[DashaPeriod]    # Current Sookshma
```

#### DashaWeight
Dasha weight calculation for scoring:
```python
class DashaWeight(BaseModel):
    planet: Planet                              # Planet being scored
    date: Date                                  # Date for calculation
    mahadasha_planet: Planet                    # Current MD lord
    antardasha_planet: Planet                   # Current AD lord
    pratyantardasha_planet: Optional[Planet]    # Current PD lord
    sookshmadasha_planet: Optional[Planet]      # Current SD lord
    mahadasha_score: float                      # 40 if match, 0 otherwise
    antardasha_score: float                     # 30 if match, 0 otherwise
    pratyantardasha_score: float                # 20 if match, 0 otherwise
    sookshmadasha_score: float                  # 10 if match, 0 otherwise
    total_weight: float                         # Sum of all scores (0-100)
```

### 2. Dasha Service (`api/services/dasha_service.py`)

#### Core Functionality
- ✅ **Parse Dasha Data**: Extract hierarchical dasha periods from jyotishganit JSON
- ✅ **Find Active Dashas**: Identify which dashas are active on any given date
- ✅ **Calculate Weights**: Score planets based on dasha lordship
- ✅ **Get All Mahadashas**: Retrieve all 9 mahadasha periods

#### Key Methods

```python
get_active_dashas(chart_json, target_date) -> ActiveDashas
```
- Finds active Mahadasha, Antardasha, Pratyantar, and Sookshma for a date
- Recursively searches through nested dasha structure
- Returns complete ActiveDashas object

```python
calculate_dasha_weight(planet, active_dashas) -> DashaWeight
```
- Calculates dasha weight using formula: **Score = 40·D_md + 30·D_ad + 20·D_pd + 10·D_sd**
- Where D_x = 1 if planet matches dasha lord, 0 otherwise
- Returns score between 0-100

```python
get_all_mahadashas(chart_json) -> Dict[Planet, DashaPeriod]
```
- Extracts all 9 mahadasha periods from birth to 120 years
- Returns dictionary mapping each planet to its mahadasha period

```python
_parse_date(date_str) -> date
```
- Parses dates from multiple formats (YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD)
- Handles jyotishganit date strings

### 3. REST API Routes (`api/routes/dasha.py`)

#### Endpoints

**POST /dasha/active**
- Get active dashas for a specific date
- Request: `{ chart_id, target_date }`
- Response: `ActiveDashas` object

**GET /dasha/{chart_id}/active**
- Get active dashas using GET method
- Query param: `target_date` (optional, defaults to today)
- Response: `ActiveDashas` object

**POST /dasha/weight**
- Calculate dasha weight for a planet
- Request: `{ chart_id, planet, target_date }`
- Response: `DashaWeight` object with detailed scoring

**GET /dasha/{chart_id}/mahadashas**
- Get all mahadasha periods for a chart
- Response: List of all 9 mahadasha periods

### 4. Unit Tests (`tests/test_dasha_service.py`)
Comprehensive test suite with 8 tests:

- ✅ `test_service_initialization` - Verifies service setup
- ✅ `test_parse_date` - Tests date parsing from multiple formats
- ✅ `test_get_active_dashas` - Tests finding active dashas for birth date
- ✅ `test_get_active_dashas_current` - Tests finding active dashas for today
- ✅ `test_calculate_dasha_weight_match` - Tests weight when planet matches
- ✅ `test_calculate_dasha_weight_no_match` - Tests weight when planet doesn't match
- ✅ `test_get_all_mahadashas` - Tests extracting all 9 mahadashas
- ✅ `test_dasha_period_structure` - Tests dasha period hierarchy

**Test Results**: All 8 tests passing ✅

## Dasha Weight Calculation Formula

The dasha weight is calculated using a weighted sum:

```
Score = 40·D_md + 30·D_ad + 20·D_pd + 10·D_sd
```

Where:
- **D_md** = 1 if planet is Mahadasha lord, 0 otherwise → contributes **40 points**
- **D_ad** = 1 if planet is Antardasha lord, 0 otherwise → contributes **30 points**
- **D_pd** = 1 if planet is Pratyantar lord, 0 otherwise → contributes **20 points**
- **D_sd** = 1 if planet is Sookshma lord, 0 otherwise → contributes **10 points**

**Total possible score**: 0-100 (if a planet rules all 4 levels simultaneously, which is impossible)

### Example Calculation

For date 2026-03-17 with active dashas:
- Mahadasha: Ketu
- Antardasha: Saturn
- Pratyantar: Moon
- Sookshma: None

**Ketu's weight**: 40 + 0 + 0 + 0 = **40**
**Saturn's weight**: 0 + 30 + 0 + 0 = **30**
**Moon's weight**: 0 + 0 + 20 + 0 = **20**
**Sun's weight**: 0 + 0 + 0 + 0 = **0** (not ruling any dasha)

## Data Extracted from jyotishganit

### Dasha Structure
The service extracts from `chart_json["dashas"]`:

```json
{
  "dashas": {
    "balance": { "Saturn": 10.3465 },
    "all": {
      "mahadashas": {
        "Saturn": {
          "start": "1984-08-06",
          "end": "2003-08-07",
          "antardashas": {
            "Saturn": {
              "start": "1984-08-06",
              "end": "1987-08-10",
              "pratyantardashas": { ... }
            }
          }
        }
      }
    }
  }
}
```

## Usage Examples

### 1. Get Active Dashas via API

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/dasha/active' \
  -H 'Content-Type: application/json' \
  -d '{
  "chart_id": "26eb1bff-d667-46ad-8a7f-7715abd632f4",
  "target_date": "2026-03-17"
}'
```

**Response:**
```json
{
  "date": "2026-03-17",
  "mahadasha": {
    "planet": "Ketu",
    "start_date": "2022-08-07",
    "end_date": "2029-08-07",
    "level": "mahadasha"
  },
  "antardasha": {
    "planet": "Saturn",
    "start_date": "2025-08-14",
    "end_date": "2026-09-22",
    "level": "antardasha"
  },
  "pratyantar": {
    "planet": "Moon",
    "start_date": "2026-02-19",
    "end_date": "2026-03-24",
    "level": "pratyantar"
  },
  "sookshma": null
}
```

### 2. Calculate Dasha Weight via API

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/dasha/weight' \
  -H 'Content-Type: application/json' \
  -d '{
  "chart_id": "26eb1bff-d667-46ad-8a7f-7715abd632f4",
  "planet": "Ketu",
  "target_date": "2026-03-17"
}'
```

**Response:**
```json
{
  "planet": "Ketu",
  "date": "2026-03-17",
  "mahadasha_planet": "Ketu",
  "antardasha_planet": "Saturn",
  "pratyantardasha_planet": "Moon",
  "sookshmadasha_planet": null,
  "mahadasha_score": 40,
  "antardasha_score": 0,
  "pratyantardasha_score": 0,
  "sookshmadasha_score": 0,
  "total_weight": 40
}
```

### 3. Use in Python Code

```python
from datetime import date
from api.services.dasha_service import DashaService
from api.models import Planet
import json

# Load chart JSON
with open('output/chart_<uuid>.json', 'r') as f:
    chart_json = json.load(f)

# Initialize service
service = DashaService()

# Get active dashas
active_dashas = service.get_active_dashas(chart_json, date(2026, 3, 17))
print(f"Mahadasha: {active_dashas.mahadasha.planet}")
print(f"Antardasha: {active_dashas.antardasha.planet}")

# Calculate weight for a planet
weight = service.calculate_dasha_weight(Planet.KETU, active_dashas)
print(f"Ketu weight: {weight.total_weight}")

# Get all mahadashas
all_mds = service.get_all_mahadashas(chart_json)
for planet, period in all_mds.items():
    print(f"{planet}: {period.start_date} to {period.end_date}")
```

## Files Created/Modified

### New Files
- ✅ `api/models/dasha.py` (108 lines)
- ✅ `api/services/dasha_service.py` (257 lines)
- ✅ `api/routes/dasha.py` (169 lines)
- ✅ `tests/test_dasha_service.py` (155 lines)
- ✅ `readme/PHASE3_COMPLETE.md` (this file)

### Modified Files
- ✅ `api/models/__init__.py` - Added DashaWeight export
- ✅ `main.py` - Registered dasha router

## Integration with Swagger UI

All dasha endpoints are available in Swagger UI at `http://localhost:8000/docs`:

- **Dasha** tag with 4 endpoints
- Interactive API testing
- Request/response schemas
- Example values

## Key Technical Decisions

### 1. Date Field Naming
- Changed field name from `date` to `Date` (imported as `from datetime import date as Date`)
- Avoids Pydantic validation error where field name conflicts with type annotation
- Maintains clean API with `date` field in JSON responses

### 2. Weight Calculation
- Weights are on 0-100 scale (40, 30, 20, 10)
- Binary match (1 or 0) multiplied by weight
- Total is sum of all matched weights
- Maximum possible: 100 (if planet ruled all 4 levels, which can't happen)

### 3. Hierarchical Dasha Search
- Recursive search through nested dasha structure
- Checks date ranges at each level
- Returns all 4 levels (MD, AD, PD, SD) when available

### 4. Date Parsing Flexibility
- Supports multiple date formats from jyotishganit
- Handles YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD
- Robust error handling

## Configuration

Dasha weights are configurable via `ScoringConfig`:

```python
class DashaWeights(BaseModel):
    mahadasha: float = 40    # Mahadasha weight
    antardasha: float = 30   # Antardasha weight
    pratyantar: float = 20   # Pratyantar weight
    sookshma: float = 10     # Sookshma weight
```

These can be adjusted to change the relative importance of each dasha level.

## Next Steps: Phase 4

Phase 4 will implement the **Transit Calculation Service**:
- Calculate current planetary positions
- Determine transit effects on natal chart
- Calculate transit weights for scoring
- Integration with ephemeris data

## Notes

- All dasha data comes from jyotishganit's Vimshottari dasha calculations
- The service handles missing Sookshma dasha gracefully (often not calculated)
- Dasha periods are deterministic - same birth data always produces same dashas
- The 120-year cycle includes all 9 planets as Mahadasha lords
- Active dasha search is efficient using binary date comparisons
- All endpoints require a valid chart_id (UUID from natal chart generation)


