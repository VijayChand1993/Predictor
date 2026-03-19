# ✅ Phase 4: Transit Calculation Service - COMPLETE

## Overview

Phase 4 implements a complete transit calculation service using the `kerykeion` library to calculate planetary positions for any date/time and determine their impact on the natal chart.

## 📦 What Was Built

### 1. Transit Service (`api/services/transit_service.py`)

A comprehensive service for calculating planetary transits with the following features:

#### Core Functions

```python
get_transit_data(target_date, natal_chart, save_json=False) -> TransitData
```
- Calculates planetary positions for a specific date/time
- Uses kerykeion with Sidereal/Lahiri ayanamsa
- Determines house placement relative to natal ascendant
- Returns all 9 planets with complete transit data

```python
calculate_transit_weight(planet, transit_house) -> float
```
- Calculates transit weight using the formula: `W_transit(p) = 100 × PlanetWeight(p) × HouseWeight(h_transit)`
- Returns weight in 0-100 range
- Uses configurable planet and house importance weights

```python
get_time_segments(start_date, end_date, natal_chart, fast_planets=None) -> List[TimeSegment]
```
- Generates time segments based on transit changes
- Detects sign changes for fast-moving planets (Moon, Sun, Mars, Mercury)
- Creates segments where planetary positions are constant
- Optimizes scoring calculations by reducing redundant computations

### 2. House Calculation Logic

Implements **Whole Sign House System** for calculating transit houses (traditional Vedic approach):

```python
def _calculate_house(transit_sign_num, transit_degree, natal_chart) -> int
```

**Algorithm:**
- Each zodiac sign = one complete house
- House 1 starts at the ascendant sign (regardless of degree)
- Formula: `house = ((transit_sign_num - natal_lagna_sign_num) % 12) + 1`

**Example:**
- Natal Ascendant: Sagittarius (sign 9)
- Transit Sun: Pisces (sign 12)
- House: ((12 - 9) % 12) + 1 = 4th house

**Why Whole Sign?**
- Traditional Vedic astrology standard for transit (Gochar) analysis
- Simpler and more consistent than Equal House
- Each sign = one house, making calculations deterministic
- Matches most Vedic astrology software and online resources

### 3. Kerykeion Integration

Uses `AstrologicalSubjectFactory` for offline sidereal calculations:

```python
transit_chart = AstrologicalSubjectFactory.from_birth_data(
    name="Transit",
    year=target_date.year,
    month=target_date.month,
    day=target_date.day,
    hour=target_date.hour,
    minute=target_date.minute,
    lng=location.longitude,
    lat=location.latitude,
    tz_str=location.timezone,
    zodiac_type="Sidereal",
    sidereal_mode="LAHIRI",
    online=False
)
```

**Data Extraction:**
- Planet positions from kerykeion objects (sun, moon, mars, etc.)
- Sign number conversion: `sign_num = 1 if planet_obj.sign_num + 1 == 13 else planet_obj.sign_num + 1`
- Degree within sign: `planet_obj.position`
- Retrograde status: `planet_obj.retrograde`

### 4. Motion Type Classification

Categorizes planetary movement based on speed and retrograde status:

| Planet | Fast | Normal | Slow | Stationary |
|--------|------|--------|------|------------|
| Moon | >14.0°/day | 12-14°/day | <12.0°/day | <0.1°/day |
| Sun | >1.05°/day | 0.95-1.05°/day | <0.95°/day | <0.01°/day |
| Mercury/Venus | >1.5°/day | 0.5-1.5°/day | <0.5°/day | <0.1°/day |
| Mars/Jupiter/Saturn | - | Normal | - | <0.01°/day |

**Retrograde planets** are always classified as `MotionType.RETROGRADE`.

### 5. Average Planetary Speeds

Used for motion type determination:

| Planet | Speed (°/day) |
|--------|---------------|
| Moon | 13.2 |
| Sun | 1.0 |
| Mercury | 1.2 |
| Venus | 1.0 |
| Mars | 0.5 |
| Jupiter | 0.08 |
| Saturn | 0.03 |
| Rahu | 0.05 |
| Ketu | 0.05 |

## 🌐 REST API Endpoints

### 1. Calculate Transit

**POST** `/transit/calculate`

Calculate planetary positions for a specific date/time.

**Request:**
```json
{
  "chart_id": "26eb1bff-d667-46ad-8a7f-7715abd632f4",
  "target_date": "2026-03-19T18:21:59",
  "save_json": false
}
```

**Response:**
```json
{
  "date": "2026-03-19T18:21:59",
  "planets": {
    "Sun": {
      "planet": "Sun",
      "sign": "Pisces",
      "house": 3,
      "degree": 4.7,
      "is_retrograde": false,
      "speed": 1.0,
      "motion_type": "Normal"
    },
    "Moon": {
      "planet": "Moon",
      "sign": "Pisces",
      "house": 3,
      "degree": 10.93,
      "is_retrograde": false,
      "speed": 13.2,
      "motion_type": "Fast"
    }
    // ... all 9 planets
  }
}
```

### 2. Calculate Transit Weight

**POST** `/transit/weight`

Calculate transit weight for a planet in a specific house.

**Request:**
```json
{
  "chart_id": "26eb1bff-d667-46ad-8a7f-7715abd632f4",
  "planet": "Jupiter",
  "transit_house": 1
}
```

**Response:**
```json
{
  "planet": "Jupiter",
  "transit_house": 1,
  "planet_weight": 1.0,
  "house_weight": 1.0,
  "total_weight": 100.0
}
```

### 3. Get Time Segments

**POST** `/transit/segments`

Generate time segments based on transit changes.

**Request:**
```json
{
  "chart_id": "26eb1bff-d667-46ad-8a7f-7715abd632f4",
  "start_date": "2026-03-19T00:00:00",
  "end_date": "2026-03-22T00:00:00",
  "fast_planets": ["Moon", "Sun"]
}
```

**Response:**
```json
[
  {
    "start_date": "2026-03-19T00:00:00",
    "end_date": "2026-03-20T14:30:00",
    "transit_data": {
      "date": "2026-03-19T00:00:00",
      "planets": { /* all 9 planets */ }
    }
  },
  {
    "start_date": "2026-03-20T14:30:00",
    "end_date": "2026-03-22T00:00:00",
    "transit_data": {
      "date": "2026-03-20T14:30:00",
      "planets": { /* all 9 planets */ }
    }
  }
]
```

### 4. Get Current Transit

**GET** `/transit/current/{chart_id}?save_json=false`

Get current planetary transits for a natal chart (convenience endpoint).

**Response:** Same as `/transit/calculate`

## 📊 Transit Weight Formula

The transit weight calculation follows the formula from `scoreLogic.md`:

```
W_transit(p) = 100 × PlanetWeight(p) × HouseWeight(h_transit)
```

### Planet Importance Weights

| Planet | Weight |
|--------|--------|
| Jupiter | 1.0 |
| Saturn | 1.0 |
| Rahu | 0.9 |
| Ketu | 0.9 |
| Moon | 0.8 |
| Mars | 0.7 |
| Sun | 0.6 |
| Venus | 0.6 |
| Mercury | 0.5 |

### House Importance Weights

| House Type | Houses | Weight |
|------------|--------|--------|
| Kendra | 1, 4, 7, 10 | 1.0 |
| Trikona | 1, 5, 9 | 0.9 |
| Upachaya | 3, 6, 10, 11 | 0.8 |
| Other | 2, 11 | 0.7 |
| Dusthana | 6, 8, 12 | 0.6 |

### Weight Range

- **Minimum**: 30 (Mercury in Dusthana: 100 × 0.5 × 0.6 = 30)
- **Maximum**: 100 (Jupiter/Saturn in Kendra: 100 × 1.0 × 1.0 = 100)

## 🧪 Test Coverage

Created comprehensive test suite in `tests/test_transit_service.py`:

### Test Cases (13 tests, all passing)

1. ✅ **test_service_initialization** - Service initializes correctly
2. ✅ **test_get_transit_data** - Transit data calculation
3. ✅ **test_sign_num_to_sign_conversion** - Sign number to enum conversion
4. ✅ **test_sign_to_num_conversion** - Sign enum to number conversion
5. ✅ **test_house_calculation** - House calculation from transit position
6. ✅ **test_calculate_transit_weight** - Transit weight calculation
7. ✅ **test_average_speed** - Average speed retrieval
8. ✅ **test_motion_type_determination** - Motion type classification
9. ✅ **test_get_time_segments** - Time segmentation
10. ✅ **test_save_transit_json** - JSON output saving
11. ✅ **test_transit_weight_formula** - Weight formula verification
12. ✅ **test_all_planets_have_speeds** - All planets have defined speeds
13. ✅ **test_retrograde_planets** - Retrograde planet handling

**Test Results:**
```
13 passed, 20 warnings in 9.13s
```

## 📁 Files Created/Modified

### New Files
- ✅ `api/services/transit_service.py` (384 lines)
- ✅ `api/routes/transit.py` (169 lines)
- ✅ `tests/test_transit_service.py` (283 lines)
- ✅ `readme/PHASE4_COMPLETE.md` (this file)

### Modified Files
- ✅ `api/models/transit.py` - Updated TimeSegment model
- ✅ `main.py` - Added transit router
- ✅ `api/models/__init__.py` - Already had transit models exported

## 🎯 Key Features

### 1. Deterministic Calculations
- Same date/time always produces same transit data
- Uses offline calculations (no internet required)
- Sidereal/Lahiri ayanamsa for Vedic accuracy

### 2. Explainable Results
- All transit data can be saved as JSON for inspection
- Weight calculations show breakdown of planet and house weights
- Clear formula: `100 × PlanetWeight × HouseWeight`

### 3. Type-Safe
- Full Pydantic validation for all models
- Enum-based planet and sign representations
- Validated house numbers (1-12) and degrees (0-30)

### 4. Efficient Time Segmentation
- Detects sign changes for fast-moving planets
- Creates segments with constant planetary positions
- Reduces redundant calculations for scoring

### 5. Configurable Weights
- All weights defined in `ScoringConfig`
- Easy to adjust planet and house importance
- Consistent with scoreLogic.md specifications

## 📝 Usage Example

```python
from datetime import datetime
from api.services.transit_service import TransitService
from api.services.natal_chart_service import NatalChartService

# Load natal chart
chart_service = NatalChartService()
natal_chart = chart_service.load_chart("chart_id_here")

# Initialize transit service
transit_service = TransitService()

# Get current transit
transit_data = transit_service.get_transit_data(
    target_date=datetime.now(),
    natal_chart=natal_chart,
    save_json=True
)

# Access transit data
sun_transit = transit_data.planets[Planet.SUN]
print(f"Sun in {sun_transit.sign}, House {sun_transit.house}")
print(f"Degree: {sun_transit.degree:.2f}")
print(f"Retrograde: {sun_transit.is_retrograde}")
print(f"Motion: {sun_transit.motion_type}")

# Calculate transit weight
weight = transit_service.calculate_transit_weight(
    planet=Planet.JUPITER,
    transit_house=sun_transit.house
)
print(f"Transit weight: {weight:.2f}")

# Get time segments for a date range
segments = transit_service.get_time_segments(
    start_date=datetime(2026, 3, 1),
    end_date=datetime(2026, 3, 31),
    natal_chart=natal_chart,
    fast_planets=[Planet.MOON, Planet.SUN]
)
print(f"Generated {len(segments)} time segments")
```

## 🚀 Next Steps: Phase 5

Phase 4 is complete and ready for integration with Phase 5 (Aspect Calculation Service).

The transit service provides:
- ✅ Accurate planetary positions for any date/time
- ✅ House placements relative to natal chart
- ✅ Transit weight calculations
- ✅ Time segmentation for efficient scoring
- ✅ REST API endpoints for all functionality

All transit data is properly structured and validated, making it easy to build the aspect calculation and final scoring engine on top of this foundation.

