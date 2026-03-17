Design **a scoring engine** that consumes astrology signals and outputs **weights for planets and houses over a time range**. The trick is to turn traditional Jyotish ideas (dasha, gochar, strengths) into **structured signals** you can score.

Below is a **manual checklist + algorithm design** we can implement
---

# 1️⃣ Define the Time Resolution First

Before calculations, decide **granularity**.

Typical options:

```
daily resolution
12-hour resolution
hourly resolution
```

For most astrology analysis:

```
1 day resolution is enough
```

Reason: only the **Moon changes signs quickly** (~2.25 days).

---

# 2️⃣ Gather Natal Chart Data (Baseline)

This never changes and forms the **reference frame**.

You must extract from the **birth chart (Lagna chart)**:

### Planet placements

From the natal chart:

```
planet sign
planet house
planet nakshatra
```

### Planet roles

Determine:

```
which houses each planet rules
```

Example (Sagittarius Lagna):

```
Jupiter → 1st + 4th lord
Mars → 5th + 12th lord
Saturn → 2nd + 3rd lord
```

This tells you **which houses a planet activates when it becomes strong**.

---

# 3️⃣ Determine Current Dasha Periods

From **Vimshottari Dasha**.

Extract:

```
Mahadasha
Antardasha
Pratyantar
```

For example:

```
Mahadasha: Ketu
Antardasha: Saturn
Pratyantar: Mars
```

These are **always active drivers**.

### Convert them into weights

Example scoring:

```
Mahadasha → 40%
Antardasha → 30%
Pratyantar → 20%
Sookshma → 10%
```

These weights feed your **planet strength model**.

---

# 4️⃣ Collect Transit Data for the Time Range

Now compute planetary positions for each date.

For each day between:

```
1 Feb 2026 → 28 Feb 2026
```

get:

```
Sun sign
Moon sign
Mars sign
Mercury sign
Jupiter sign
Saturn sign
Rahu/Ketu sign
```

Libraries like VedAstro will give this.

---

# 5️⃣ Detect Transit Change Boundaries

You don't actually need **every day**.

Instead detect **events**:

```
Moon sign change
Sun sign change
Mars sign change
Mercury sign change
```

These create segments.

Example output:

```
1–3 Feb → Moon in Scorpio
3–5 Feb → Moon in Sagittarius
5–7 Feb → Moon in Capricorn
```

So your algorithm divides the range into **sub-intervals**.

---

# 6️⃣ Convert Transit Positions Into Houses

Using Lagna:

```
transit sign → house number
```

Example:

```
Sagittarius Lagna
Moon in Pisces → 4th house
Mars in Gemini → 7th house
```

Now you know **which houses are activated**.

---

# 7️⃣ Identify Aspects

Planets also influence houses via **drishti (aspects)**.

Important ones:

```
Mars → 4, 7, 8
Saturn → 3, 7, 10
Jupiter → 5, 7, 9
```

Example:

```
Mars in 7th
aspect 10th house
```

Now that house also gets activation.

---

# 8️⃣ Use Ashtakavarga Strength

From the **Ashtakavarga table** in the natal chart.

Each house has points:

```
0–20 weak
21–25 moderate
26–30 strong
30+ very strong
```

Convert to percentage.

Example mapping:

```
23 → 50%
26 → 70%
30 → 85%
37 → 100%
```

This modifies house activation.

---

# 9️⃣ Consider Planet Strength

Planet strength depends on:

```
exaltation / debilitation
retrograde
combustion
house placement
```

Example scoring:

```
Exalted → +25%
Own sign → +20%
Friendly sign → +10%
Enemy sign → -10%
Debilitated → -25%
```

This adjusts **planet influence weight**.

---

# 🔟 Calculate Planet Activation Score

For each planet:

```
planet_score =
dasha_weight
+ transit_weight
+ aspect_weight
+ strength_modifier
```

Example:

```
Saturn

Dasha = 30
Transit influence = 15
Aspect influence = 10
Strength modifier = +5

Total = 60%
```

---

# 1️⃣1️⃣ Convert Planet Scores Into House Scores

Each planet activates:

```
its natal house
houses it rules
houses it transits
houses it aspects
```

Example:

```
Saturn activates

2nd
3rd
transit house
aspect houses
```

Distribute score across them.

---

# 1️⃣2️⃣ Aggregate Scores for Each Interval

Now combine contributions from all planets.

Example:

```
1–3 Feb

Moon = 30
Saturn = 60
Mars = 20
Jupiter = 25
```

Normalize totals to **100%**.

Output:

```
planet influence distribution
house activation distribution
```

---

# Example Final Output

For **5–7 Feb**:

Planet influence:

```
Saturn → 35%
Moon → 25%
Mars → 15%
Jupiter → 10%
Sun → 8%
Others → 7%
```

House activation:

```
10th house → 30%
6th house → 20%
3rd house → 18%
7th house → 15%
Others → 17%
```

---

# Important Factors You Haven’t Included Yet

You should also consider:

### 1️⃣ Moon transit from Moon sign

Many predictions use:

```
transits from Lagna
AND
transits from Moon
```

---

### 2️⃣ Divisional charts

Especially:

```
D9 (Navamsa)
D10 (career)
```

These refine planet strength.

---

### 3️⃣ Nakshatra transits

Moon nakshatra transitions create **micro periods**.

---

### 4️⃣ Retrograde phases

Retrograde planets often gain strength.

---

# A More Complete Signal Model

Your scoring engine could combine:

```
Dasha influence
Transit house placement
Planet strength
Aspects
Ashtakavarga strength
Moon transit
Retrograde state
Divisional chart confirmation
```

---

# My Honest Advice

Your idea of:

```
planet influence %
house activation %
```

is **very powerful**.

It basically converts astrology into a **time-series signal model**.

If designed well, you could generate things like:

```
monthly influence graphs
planet activity timelines
house activation heatmaps
```

---
