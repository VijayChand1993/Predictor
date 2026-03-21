# Domain Analysis Implementation Plan

## Overview

This document outlines the implementation plan for adding **Life Domain Analysis** to the Vedic Astrology Scoring Engine. This feature will translate astrological data (planet scores and house activations) into actionable insights about 7 key life domains.

---

## 🎯 Goal

Create a system that analyzes and visualizes how planetary positions and house activations affect specific life domains:

1. **Career / Work** (job, promotion, workload, pressure)
2. **Wealth / Finance** (income, savings, gains)
3. **Health / Physical** (illness, recovery, stamina)
4. **Relationships** (spouse, romance, conflicts)
5. **Learning / Growth** (education, wisdom, luck)
6. **Mental State** (stress, clarity, focus)
7. **Transformation / Uncertainty** (sudden change, instability)

---

## 📋 Implementation Steps

### Phase 1: Data Models & Configuration

#### Step 1.1: Create Domain Configuration File

**File:** `api/core/domain_config.py`

**Content:**
- Domain-to-house mappings with weights
- Planet-to-domain influence mappings
- Subdomain definitions
- Event detection rules

**Key Structures:**
```python
DOMAIN_HOUSE_MAPPING = {
    "Career / Work": {
        "primary_houses": [10],
        "secondary_houses": [6],
        "weights": {10: 0.7, 6: 0.3}
    },
    # ... other domains
}

PLANET_DOMAIN_INFLUENCE = {
    "Sun": {
        "Career / Work": 0.9,
        "Health / Physical": 0.7,
        # ... other domains
    },
    # ... other planets
}

SUBDOMAIN_MAPPING = {
    "job": {
        "houses": {10: 0.8, 6: 0.2},
        "planets": {"Sun": 0.7, "Saturn": 0.6}
    },
    # ... other subdomains
}
```

#### Step 1.2: Create Domain Data Models

**File:** `api/models/domain_analysis.py`

**Models to create:**
- `DomainScore` - Score for a single domain
- `SubdomainScore` - Score for a subdomain
- `PlanetContribution` - How much a planet contributes to a domain
- `DomainAnalysis` - Complete analysis for all domains
- `DomainTimePoint` - Domain scores at a specific time
- `DomainTimeline` - Timeline of domain scores
- `SignificantEvent` - Astrological events affecting domains
- `DomainAnalysisRequest` - API request model
- `DomainAnalysisResponse` - API response model

**Example:**
```python
class DomainScore(BaseModel):
    domain: str
    score: float  # 0-100
    house_contribution: float
    planet_contribution: float
    driving_planets: List[Tuple[Planet, float]]
    subdomains: Dict[str, SubdomainScore]
    
class DomainAnalysis(BaseModel):
    chart_id: str
    calculation_date: datetime
    domains: Dict[str, DomainScore]
    overall_life_quality: float
    strongest_domain: str
    weakest_domain: str
```

---

### Phase 2: Domain Service

#### Step 2.1: Create Domain Service

**File:** `api/services/domain_service.py`

**Methods to implement:**

1. **`calculate_domain_score()`**
   - Input: domain name, house activations, planet scores
   - Output: DomainScore
   - Logic: Combine house activation (60%) + planet influence (40%)

2. **`calculate_subdomain_score()`**
   - Input: subdomain name, house activations, planet scores
   - Output: SubdomainScore
   - Logic: More granular calculation using subdomain mappings

3. **`identify_driving_planets()`**
   - Input: domain name, planet scores
   - Output: List of (planet, contribution) sorted by impact
   - Logic: Calculate which planets most influence the domain

4. **`calculate_all_domains()`**
   - Input: natal chart, calculation date
   - Output: DomainAnalysis
   - Logic: Calculate scores for all 7 domains

5. **`detect_significant_events()`**
   - Input: natal chart, start date, end date
   - Output: List of SignificantEvent
   - Logic: Identify planet sign changes, aspects, retrogrades

6. **`calculate_domain_timeline()`**
   - Input: natal chart, start date, end date, interval
   - Output: DomainTimeline
   - Logic: Calculate domain scores at regular intervals

**Core Formula:**
```python
Domain_Score = (
    Σ(House_Activation[h] × House_Weight[d, h]) × 0.6 +
    Σ(Planet_Score[p] × Planet_Influence[p, d]) × 0.4
)
```

---

### Phase 3: API Endpoints

#### Step 3.1: Create Domain Analysis Routes

**File:** `api/routes/domain_analysis.py`

**Endpoints to create:**

1. **`POST /domain-analysis/calculate`**
   - Calculate domain scores for a specific date
   - Request: `{ "chart_id": "...", "calculation_date": "..." }`
   - Response: Complete domain analysis with all 7 domains

2. **`GET /domain-analysis/{chart_id}/timeline`**
   - Get domain scores over a time range
   - Query params: `start_date`, `end_date`, `interval_days`
   - Response: Timeline data for all domains

3. **`GET /domain-analysis/{chart_id}/domain/{domain_name}`**
   - Get detailed analysis for a specific domain
   - Response: Domain score with subdomain breakdown

4. **`GET /domain-analysis/{chart_id}/events`**
   - Get significant astrological events
   - Query params: `start_date`, `end_date`
   - Response: List of events with affected domains

5. **`GET /domain-analysis/{chart_id}/drivers`**
   - Get planet drivers for all domains at current time
   - Response: Which planets are driving which domains

#### Step 3.2: Register Router

**File:** `main.py`

Add:
```python
from api.routes import domain_analysis
app.include_router(domain_analysis.router)
```

---

### Phase 4: Streamlit Visualizations

#### Step 4.1: Add Domain Analysis Tab

**File:** `streamlit_app.py`

**Add new tab:** "🎯 Domain Analysis"

**Visualizations to create:**

1. **Multi-Line Timeline Chart**
   - X-axis: Time
   - Y-axis: Score (0-100)
   - 7 lines (one per domain)
   - Shows trends over time

2. **Domain Heatmap**
   - Rows: 7 domains
   - Columns: Time periods
   - Color: Score intensity
   - Shows patterns at a glance

3. **Current State Radar Chart**
   - 7 axes (one per domain)
   - Shows current life balance
   - Identifies strengths/weaknesses

4. **Planet Drivers Panel**
   - For each domain, show top 3 driving planets
   - Use metric cards with contributions
   - Helps understand "why" scores are what they are

5. **Subdomain Breakdown**
   - Expandable sections for each domain
   - Show 4 subdomains per domain
   - Bar charts or progress bars

6. **Event Timeline**
   - Vertical markers on timeline
   - Annotations for significant events
   - Links events to domain changes

7. **Domain Comparison Table**
   - Sortable table with all domains
   - Current score, trend, driving planets
   - Formatted with color coding

#### Step 4.2: Add Interactive Features

- **Date range selector** for timeline
- **Domain filter** (select which domains to show)
- **Event toggle** (show/hide event markers)
- **Export functionality** (download domain data as CSV)

---

### Phase 5: Testing

#### Step 5.1: Create Unit Tests

**File:** `tests/test_domain_service.py`

**Tests to write:**
- Test domain score calculation
- Test subdomain score calculation
- Test planet driver identification
- Test event detection
- Test timeline generation
- Test edge cases (all planets weak, all houses inactive)

#### Step 5.2: Create Integration Tests

**File:** `tests/test_domain_analysis_routes.py`

**Tests to write:**
- Test all API endpoints
- Test with real chart data
- Test timeline with different intervals
- Test error handling

---

### Phase 6: Documentation

#### Step 6.1: Update API Documentation

Add examples to Swagger docs for all new endpoints

#### Step 6.2: Create User Guide

**File:** `readme/DOMAIN_ANALYSIS_GUIDE.md`

**Content:**
- What is domain analysis?
- How to interpret domain scores
- Understanding planet drivers
- Using the timeline visualization
- Interpreting events
- Best practices

#### Step 6.3: Update Main README

Add section about domain analysis feature

---

## 📊 Data Flow

```
User Request
    ↓
API Endpoint (/domain-analysis/calculate)
    ↓
Domain Service
    ├─→ Get House Activations (from HouseActivationService)
    ├─→ Get Planet Scores (from ScoringEngine)
    ├─→ Apply Domain Mappings (from domain_config.py)
    └─→ Calculate Domain Scores
    ↓
Return DomainAnalysisResponse
    ↓
Streamlit Dashboard
    ├─→ Timeline Chart
    ├─→ Heatmap
    ├─→ Radar Chart
    └─→ Tables & Metrics
```

---

## 🎨 Visualization Examples

### 1. Multi-Line Timeline
```
Score
100 |     Career ──────
 80 |           ╱╲    ╱
 60 |    ╱────╱  ╲  ╱  Wealth ─ ─ ─
 40 |   ╱          ╲╱
 20 | ─╱            Health ·····
  0 |_________________________
    Jan  Feb  Mar  Apr  May
```

### 2. Radar Chart (Current State)
```
        Career (85)
            ╱│╲
           ╱ │ ╲
    Mental│  │  │Learning
      (60)│  │  │(75)
          │  │  │
    ──────┼──┼──┼──────
          │  │  │
   Wealth │  │  │Health
     (70) │  │  │(65)
           ╲ │ ╱
            ╲│╱
       Relationships (55)
```

### 3. Event Markers
```
Timeline with events:
─────●─────────●──────────●─────
     │         │          │
  Jupiter   Saturn    Mars
  enters    aspects   retro
  10th      7th       begins
```

---

## 🔑 Key Formulas

### Domain Score Calculation
```
Domain_Score(d, t) = 
    House_Component + Planet_Component

House_Component = 
    Σ(House_Activation[h, t] × House_Weight[d, h]) × 0.6

Planet_Component = 
    Σ(Planet_Score[p, t] × Planet_Influence[p, d]) × 0.4
    ─────────────────────────────────────────────────
    Σ(Planet_Influence[p, d])  [normalization]
```

### Subdomain Score
```
Subdomain_Score(sd, t) = 
    Σ(House_Activation[h, t] × Subdomain_House_Weight[sd, h]) × 0.5 +
    Σ(Planet_Score[p, t] × Subdomain_Planet_Weight[sd, p]) × 0.5
```

### Planet Contribution
```
Planet_Contribution(p, d, t) = 
    Planet_Score[p, t] × Planet_Influence[p, d]
```

---

## 📁 Files to Create/Modify

### New Files
1. ✅ `api/core/domain_config.py` - Configuration and mappings
2. ✅ `api/models/domain_analysis.py` - Data models
3. ✅ `api/services/domain_service.py` - Business logic
4. ✅ `api/routes/domain_analysis.py` - API endpoints
5. ✅ `tests/test_domain_service.py` - Unit tests
6. ✅ `tests/test_domain_analysis_routes.py` - Integration tests
7. ✅ `readme/DOMAIN_ANALYSIS_GUIDE.md` - User documentation
8. ✅ `readme/DOMAIN_ANALYSIS_IMPLEMENTATION.md` - This file

### Modified Files
1. ✅ `main.py` - Register new router
2. ✅ `api/models/__init__.py` - Export new models
3. ✅ `streamlit_app.py` - Add domain analysis tab
4. ✅ `README.md` - Add feature description

---

## ⏱️ Estimated Timeline

- **Phase 1** (Models & Config): 2-3 hours
- **Phase 2** (Domain Service): 4-5 hours
- **Phase 3** (API Endpoints): 2-3 hours
- **Phase 4** (Streamlit UI): 4-6 hours
- **Phase 5** (Testing): 3-4 hours
- **Phase 6** (Documentation): 2-3 hours

**Total: 17-24 hours** (2-3 days of focused work)

---

## 🚀 Next Steps

1. Review and approve this implementation plan
2. Start with Phase 1 (create configuration and models)
3. Implement Phase 2 (domain service with core logic)
4. Add Phase 3 (API endpoints)
5. Build Phase 4 (visualizations)
6. Complete Phase 5 (testing)
7. Finish Phase 6 (documentation)

---

## 💡 Future Enhancements

After initial implementation, consider:

- **AI-powered insights**: Generate natural language explanations
- **Recommendations**: Suggest remedies for weak domains
- **Comparative analysis**: Compare multiple time periods
- **Goal tracking**: Set domain targets and track progress
- **Alerts**: Notify when domains cross thresholds
- **Custom domains**: Allow users to define their own domains
- **Dasha integration**: Show how dasha periods affect domains
- **Predictive analysis**: Forecast future domain trends

---

## 📚 References

- Vedic Astrology house significations
- Planet karakas (natural significations)
- Existing scoring engine (Phase 8)
- House activation system (Phase 9)
- Visualization service (Phase 10)

---

**Status:** 📝 Planning Phase  
**Last Updated:** 2026-03-21  
**Author:** Augment Agent

