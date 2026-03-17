We’re getting into the **real engine design**. 

I’ll give you a **clean mathematical model** you can implement directly.

---

# 🎯 Goal

For a given time range:

```id="g1"
T = [start, end]
```

Output:

```id="g2"
Planet Influence Score P_i ∈ [0,100]
House Activation Score H_j ∈ [0,100]
```

---

# 🧱 Core Idea

Everything is a **weighted sum of signals**.

```id="g3"
Score = Σ (Signal × Weight)
```

We define signals → normalize → combine.

---

# 1️⃣ Define Time Segments

Split the range based on **change points**:

```id="g4"
Moon sign change
Sun sign change
Mars change
Mercury change
```

Let segments be:

```id="g5"
S_k = [t_k, t_k+1]
```

Each segment has constant planetary positions.

---

# 2️⃣ Planet Influence Model

For each planet `p`, define:

```id="g6"
P(p, S_k) = W_dasha + W_transit + W_aspect + W_strength + W_motion
```

---

## 2.1 Dasha Contribution

Let:

```id="g7"
D_md(p) = 1 if planet is Mahadasha else 0
D_ad(p) = 1 if Antardasha
D_pd(p) = 1 if Pratyantar
D_sd(p) = 1 if Sookshma
```

Weights (on 0-100 scale):

```id="g8"
W_md = 40
W_ad = 30
W_pd = 20
W_sd = 10
```

Formula:

```id="g9"
W_dasha(p) = 40·D_md + 30·D_ad + 20·D_pd + 10·D_sd
```

**Note**: Removed the 100× multiplier to keep values on 0-100 scale. A planet in Mahadasha gets 40 points, in Antardasha gets 30 points, etc. Planets not in any dasha get 0.

---

## 2.2 Transit Contribution

Define importance per planet:

```id="g10"
Sun = 0.6
Moon = 0.8
Mars = 0.7
Mercury = 0.5
Jupiter = 1.0
Saturn = 1.0
Rahu/Ketu = 0.9
```

Define house importance:

```id="g11"
Kendra (1,4,7,10) = 1.0
Trikona (1,5,9) = 0.9
Upachaya (3,6,10,11) = 0.8
Dusthana (6,8,12) = 0.6
Other houses = 0.7
```

Then:

```id="g12"
W_transit(p) = 100 × PlanetWeight(p) × HouseWeight(h_transit)
```

**Range**: 30 (Mercury in Dusthana) to 100 (Jupiter/Saturn in Kendra)

**Note**: This component is scaled to 0-100 to match other components before final weighting.

---

## 2.3 Aspect Contribution

For each aspect:

```id="g13"
A(p → h) = 1 if aspect exists else 0
```

Weight per aspect type:

```id="g14"
Full aspect (7th) = 1.0
Special aspects:
  - Mars (4th, 8th) = 0.8
  - Jupiter (5th, 9th) = 0.8
  - Saturn (3rd, 10th) = 0.8
```

Formula:

```id="g15"
W_aspect(p) = Σ [A(p→h) × AspectWeight × HouseWeight(h)] × 20
```

**Scaling rationale**:
- A planet can aspect 1-4 houses
- Max sum ≈ 4 × 1.0 × 1.0 = 4 (all full aspects on Kendras)
- × 20 = 80 (reasonable upper bound on 0-100 scale)
- Typical range: 20-60

---

## 2.4 Planet Strength (Natal + Transit)

Define strength score:

```id="g16"
S(p) = dignity + retrograde + combustion
```

Breakdown:

### Dignity (based on sign placement)

```id="g17"
Exalted = +25
Own sign = +20
Friendly = +10
Neutral = 0
Enemy = -10
Debilitated = -25
```

### Retrograde

```id="g18"
Retrograde = +10
Direct = 0
```

### Combust

```id="g19"
Combust = -15
Not combust = 0
```

Normalize to 0-100 scale:

```id="g20"
W_strength(p) = max(0, min(100, 50 + S(p)))
```

**Range**:
- Min: 50 + (-25 - 15) = 10 (debilitated + combust)
- Max: 50 + (25 + 10) = 85 (exalted + retrograde)
- Typical: 40-60 (most planets)

---

## 2.5 Motion / Speed (Dynamic Factor)

Most important for:

```id="g21"
Moon, Mars, Mercury (fast-moving planets)
```

Define motion modifiers:

```id="g22"
Fast moving = +10
Stationary (near station) = +15
Slow = +5
Normal speed = 0
Not applicable = 0
```

Normalize to 0-100 scale with 50 as baseline:

```id="g22b"
W_motion(p) = 50 + motion_modifier(p)
```

**Range**:
- Fast: 60
- Stationary: 65
- Slow: 55
- Normal/Not applicable: 50 (neutral baseline)

**Note**: For planets where motion is not significant (Jupiter, Saturn), use baseline value of 50.

---

# 3️⃣ Final Planet Score

Combine all components with weights:

```id="g23"
P_raw(p) =
  0.35 × W_dasha(p)
+ 0.25 × W_transit(p)
+ 0.20 × W_strength(p)
+ 0.12 × W_aspect(p)
+ 0.08 × W_motion(p)
```

**Weight rationale**:
- Dasha (35%): Primary time-period indicator
- Transit (25%): Current planetary position
- Strength (20%): Inherent planet power (increased from 15%)
- Aspect (12%): Indirect influences (decreased from 15%)
- Motion (8%): Dynamic factor (decreased from 10%)

**Note**: Weights sum to 1.0. All W_* components are on 0-100 scale.

Normalize across all planets:

```id="g24"
P(p) = 100 × P_raw(p) / Σ P_raw(all planets)
```

This ensures all planet scores sum to 100%.

---

# 4️⃣ House Activation Model

Each planet contributes to houses:

```id="g25"
Transit house
Natal house
Owned houses
Aspected houses
```

---

## 4.1 Contribution Distribution

For planet `p` with total score:

```id="g26"
C_total = P(p)
```

Split the contribution:

```id="g27"
Transit house = 30%
Owned houses = 30%
Natal placement = 20%
Aspected houses = 20%
```

**Distribution details**:

### Owned houses
```
If planet owns 1 house: 30% to that house
If planet owns 2 houses: 15% to each house
```

### Aspected houses
```
Split 20% equally among all aspected houses
Example: If planet aspects 3 houses → 6.67% to each
```

### Example calculation
```
Saturn with P(Saturn) = 34:
- Transit house (7th): 34 × 0.30 = 10.2
- Owned houses (2nd, 3rd): 34 × 0.15 = 5.1 each
- Natal placement (10th): 34 × 0.20 = 6.8
- Aspected houses (5th, 9th, 12th): 34 × 0.20 / 3 = 2.27 each
```

---

## 4.2 Apply Ashtakavarga Modifier

Let:

```id="g28"
AV(h) = Ashtakavarga points for house h
```

Normalize (with cap at 1.0):

```id="g29"
AV_norm(h) = min(1.0, AV(h) / 40)
```

**Note**: Ashtakavarga points typically range from 0-48, but we normalize to 40 as the "strong" threshold. Houses with 40+ points get maximum modifier of 1.0.

**Interpretation**:
- 0-20 points: 0.0-0.5 (weak house)
- 21-28 points: 0.525-0.7 (moderate)
- 29-36 points: 0.725-0.9 (strong)
- 37-40 points: 0.925-1.0 (very strong)
- 40+ points: 1.0 (maximum strength)

Final house contribution:

```id="g30"
C(p → h) = BaseContribution × AV_norm(h)
```

**Fallback**: If Ashtakavarga data is unavailable, use AV_norm(h) = 1.0 (no modification).

---

# 5️⃣ Final House Score

```id="g31"
H_raw(h) = Σ C(p → h)
```

Normalize:

```id="g32"
H(h) = 100 × H_raw(h) / Σ H_raw(all houses)
```

---

# 6️⃣ Time Aggregation

For full range:

```id="g33"
P_total(p) =
Σ [P(p, S_k) × duration(S_k)] / total_time
```

Same for houses.

---

# 7️⃣ Output Structure

Final output with detailed breakdown:

```json id="g34"
{
  "time_range": {
    "start": "2026-02-01",
    "end": "2026-02-28"
  },
  "planets": {
    "Saturn": {
      "score": 34,
      "breakdown": {
        "dasha": 40,
        "transit": 80,
        "strength": 45,
        "aspect": 60,
        "motion": 50
      },
      "weighted_components": {
        "dasha": 14.0,
        "transit": 20.0,
        "strength": 9.0,
        "aspect": 7.2,
        "motion": 4.0
      }
    },
    "Moon": {
      "score": 22,
      "breakdown": {...}
    },
    "Mars": {
      "score": 15,
      "breakdown": {...}
    }
  },
  "houses": {
    "10": {
      "score": 28,
      "contributors": {
        "Saturn": 10.2,
        "Sun": 8.5,
        "Mars": 6.8,
        "Jupiter": 2.5
      }
    },
    "6": {
      "score": 18,
      "contributors": {...}
    },
    "3": {
      "score": 15,
      "contributors": {...}
    }
  }
}
```

---

# 🧠 Why This Model Works

It is:

* **deterministic** → same input = same output
* **explainable** → each score traceable with full breakdown
* **modular** → you can tweak weights independently
* **extendable** → add D9, nakshatra, yogas later
* **normalized** → all scores sum to 100%
* **time-aware** → properly handles varying time segments

---

# 🔧 Implementation Notes

## Edge Cases to Handle

1. **Missing Dasha**: Validate that at least Mahadasha exists
2. **Missing Ashtakavarga**: Use default modifier of 1.0
3. **Transit calculation failure**: Fallback to natal house
4. **Zero total scores**: Add small epsilon to avoid division by zero

## Configuration Management

All weights should be configurable:

```python
CONFIG = {
    "dasha_weights": {
        "mahadasha": 40,
        "antardasha": 30,
        "pratyantar": 20,
        "sookshma": 10
    },
    "planet_importance": {
        "Sun": 0.6, "Moon": 0.8, "Mars": 0.7,
        "Mercury": 0.5, "Jupiter": 1.0, "Saturn": 1.0,
        "Rahu": 0.9, "Ketu": 0.9
    },
    "house_importance": {
        "kendra": 1.0,      # 1,4,7,10
        "trikona": 0.9,     # 1,5,9
        "upachaya": 0.8,    # 3,6,10,11
        "dusthana": 0.6,    # 6,8,12
        "other": 0.7
    },
    "component_weights": {
        "dasha": 0.35,
        "transit": 0.25,
        "strength": 0.20,
        "aspect": 0.12,
        "motion": 0.08
    },
    "house_distribution": {
        "transit": 0.30,
        "owned": 0.30,
        "natal": 0.20,
        "aspected": 0.20
    }
}
```

## Validation Strategy

1. **Unit tests**: Test each component (dasha, transit, aspect, etc.) independently
2. **Integration tests**: Test full scoring with known charts
3. **Normalization tests**: Verify all scores sum to 100%
4. **Sensitivity tests**: Change one parameter, verify expected changes
5. **Time aggregation tests**: Use simple 2-segment examples

---