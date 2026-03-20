# Sign Changes Feature in Time Segments

## Overview

Added a new `sign_changes` field to the `TimeSegment` model that tracks which planets changed signs at the start of each segment.

## Changes Made

### 1. Updated `TimeSegment` Model (`api/models/transit.py`)

**Added Field:**
```python
sign_changes: Optional[List[Planet]] = Field(
    None,
    description="List of planets that changed signs at the start of this segment"
)
```

**Behavior:**
- `None` for the first segment (no previous segment to compare)
- `[]` (empty list) if no planets changed signs
- `[Planet.MOON, Planet.MARS, ...]` list of planets that changed signs

### 2. Updated `TransitService.get_time_segments()` (`api/services/transit_service.py`)

**Logic:**
- Tracks the previous transit data
- Compares current segment's transit positions with previous segment
- Identifies which planets changed signs between segments
- Populates the `sign_changes` field for each segment

## API Response Example

### Before:
```json
{
  "start_date": "2026-03-20T00:00:00",
  "end_date": "2026-03-22T14:30:00",
  "transit_data": {
    "date": "2026-03-20T00:00:00",
    "planets": { ... }
  }
}
```

### After:
```json
{
  "start_date": "2026-03-20T00:00:00",
  "end_date": "2026-03-22T14:30:00",
  "transit_data": {
    "date": "2026-03-20T00:00:00",
    "planets": { ... }
  },
  "sign_changes": ["Moon", "Mars"]
}
```

## Usage Example

### Request:
```bash
curl -X 'POST' \
  'http://localhost:8000/transit/segments' \
  -H 'Content-Type: application/json' \
  -d '{
  "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
  "start_date": "2026-03-20",
  "end_date": "2026-03-27"
}'
```

### Response:
```json
[
  {
    "start_date": "2026-03-20T00:00:00",
    "end_date": "2026-03-22T14:30:00",
    "sign_changes": null,  // First segment
    "transit_data": { ... }
  },
  {
    "start_date": "2026-03-22T14:30:00",
    "end_date": "2026-03-24T08:15:00",
    "sign_changes": ["Moon"],  // Moon changed sign
    "transit_data": { ... }
  },
  {
    "start_date": "2026-03-24T08:15:00",
    "end_date": "2026-03-27T00:00:00",
    "sign_changes": ["Moon", "Jupiter"],  // Both changed
    "transit_data": { ... }
  }
]
```

## Benefits

1. **Visibility**: Easily see which planets triggered a new segment
2. **Analysis**: Understand why segments were created
3. **Debugging**: Verify that all planet sign changes are being tracked
4. **User Experience**: Provide context for why time periods are divided

## Use Cases

- **Timeline Analysis**: Identify significant transit events
- **Strength Changes**: Know when planet dignity changed (e.g., Jupiter entering Cancer)
- **Event Correlation**: Match life events with specific planetary sign changes
- **Debugging**: Verify segmentation logic is working correctly

## Files Modified

1. `api/models/transit.py` - Added `sign_changes` field to `TimeSegment`
2. `api/services/transit_service.py` - Updated `get_time_segments()` to populate the field

## Backward Compatibility

✅ **Fully backward compatible**
- The field is `Optional`, so existing code will work
- API consumers can ignore the field if not needed
- No breaking changes to existing endpoints

