# Strength Calculation & Segmentation Update

## Summary

This update fixes two critical issues in the scoring engine:

1. **Strength calculation now uses TRANSIT positions** instead of natal positions
2. **Time segmentation now tracks ALL 9 planets** instead of just 4 fast planets

## Problem Statement

### Issue 1: Static Strength Calculation
Previously, the strength component (20% of total score) was calculated using **natal chart positions**, which meant:
- Planet strength never changed over time
- Dignity changes during transits were ignored
- Example: Jupiter transiting from Gemini (Neutral) to Cancer (Exalted) showed no strength change

### Issue 2: Incomplete Segmentation
The time segmentation logic only tracked 4 "fast planets" (Moon, Sun, Mars, Mercury), which meant:
- Slow planet sign changes (Jupiter, Saturn, Rahu, Ketu) were missed
- Strength calculations could be inaccurate when slow planets changed signs mid-segment
- Example: Jupiter changing from Gemini to Cancer wouldn't create a new segment

## Changes Made

### 1. Created Dignity Calculator Utility (`api/utils/dignity_calculator.py`)

A comprehensive Vedic astrology dignity calculation system:

**Features:**
- Exaltation/Debilitation tables for all 9 planets
- Own Sign (Rulership) mappings
- Moolatrikona sign identification
- Friendship/Enmity relationships

**Function:**
```python
def calculate_dignity(planet: Planet, sign: Sign) -> Dignity
```

**Priority Order:**
1. Exaltation
2. Debilitation
3. Own Sign / Moolatrikona
4. Friendly
5. Enemy
6. Neutral (default)

**Examples:**
- Jupiter in Cancer → EXALTED (+25 points)
- Jupiter in Capricorn → DEBILITATED (-25 points)
- Jupiter in Sagittarius → MOOLATRIKONA (+20 points)
- Jupiter in Pisces → OWN_SIGN (+20 points)

### 2. Updated Strength Service (`api/services/strength_service.py`)

**New Method:**
```python
def calculate_strength_from_transit(
    planet: Planet,
    transit_placement: TransitPlacement,
    sun_transit: TransitPlacement
) -> PlanetStrength
```

**What it does:**
- Calculates dignity from transit sign (using `calculate_dignity`)
- Uses transit retrograde status for bonus
- Checks combustion using transit positions
- Returns dynamic strength that changes with transits

**Strength Formula:**
```
Total Strength = Dignity Score + Retrograde Bonus + Combustion Penalty
Strength Weight = max(0, min(100, 50 + Total Strength))
```

### 3. Updated Scoring Engine (`api/services/scoring_engine.py`)

**Changed:** Line 100-120 in `calculate_component_breakdown`

**Before:**
```python
# Used natal positions
sun_placement = natal_chart.planets[Planet.SUN]
planet_placement = natal_chart.planets[planet]
planet_strength = self.strength_service.calculate_planet_strength(...)
```

**After:**
```python
# Uses transit positions
if planet in transit_data.planets and Planet.SUN in transit_data.planets:
    transit_placement = transit_data.planets[planet]
    sun_transit = transit_data.planets[Planet.SUN]
    planet_strength = self.strength_service.calculate_strength_from_transit(...)
```

### 4. Updated Transit Service (`api/services/transit_service.py`)

**Changed:** `get_time_segments` method (Line 180-210)

**Before:**
```python
if fast_planets is None:
    fast_planets = [Planet.MOON, Planet.SUN, Planet.MARS, Planet.MERCURY]
```

**After:**
```python
if fast_planets is None:
    # Track ALL planets to catch dignity changes for strength calculation
    fast_planets = [
        Planet.MOON, Planet.SUN, Planet.MARS, Planet.MERCURY,
        Planet.JUPITER, Planet.VENUS, Planet.SATURN,
        Planet.RAHU, Planet.KETU
    ]
```

## Impact

### Strength Calculation
- ✅ Strength now changes dynamically with transits
- ✅ Dignity changes are captured (e.g., Jupiter entering Cancer)
- ✅ Retrograde status affects strength in real-time
- ✅ Combustion is calculated based on current positions

### Time Segmentation
- ✅ All planet sign changes create new segments
- ✅ Slow planet dignity changes are captured
- ✅ More accurate strength calculations across time ranges
- ⚠️ More segments may be created (but more accurate)

## Example Scenario

**Jupiter Transit from Gemini to Cancer (June 2026)**

### Before Update:
- Strength: 50 (based on natal position, never changes)
- Segments: No new segment created when Jupiter changes sign

### After Update:
- March 2026: Jupiter in Gemini (Neutral) → Strength = 50
- June 2026: Jupiter enters Cancer (Exalted) → Strength = 75
- New segment created at sign change boundary
- Strength component accurately reflects Jupiter's exaltation

## Testing

The changes maintain backward compatibility:
- Existing tests should pass
- Natal-based strength calculation still available as fallback
- API endpoints unchanged

## Files Modified

1. `api/utils/dignity_calculator.py` (NEW)
2. `api/utils/__init__.py` (NEW)
3. `api/services/strength_service.py` (MODIFIED)
4. `api/services/scoring_engine.py` (MODIFIED)
5. `api/services/transit_service.py` (MODIFIED)

## Next Steps

1. Run existing tests to verify no regressions
2. Test with real chart data to verify accuracy
3. Consider adding tests for transit-based strength calculation
4. Monitor segment count for long date ranges (may need optimization)

