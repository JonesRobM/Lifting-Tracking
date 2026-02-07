# Analytics & Session Recommender Design

## Goals

Add programming effectiveness analysis, recovery monitoring, and a session recommender to the lifting tracker notebook. Primary objectives are the 2026 strength milestones:

| Lift | Target A | Target B |
|------|----------|----------|
| Deadlift | 200kg x 1 | 160kg x 5 |
| Squat | 160kg x 1 | 100kg x 20 |
| OHP | 60kg x 3 | 40kg x 12 |
| Bench | 100kg x 1 | 60kg x 10 |

## Section 1: Programming Effectiveness

### 1.1 Rate of Progression

- **Chart type**: Line chart, one series per key compound (Deadlift, Squat, OHP, Bench)
- **Data**: Session-best e1RM per compound over time
- **Overlay**: Linear regression trendline per lift
- **Annotation**: Slope displayed as kg/week on each trendline
- **Purpose**: At-a-glance view of which lifts are progressing and how fast
- **Key movements matched via**: `str.contains(case=False)` for "Deadlift", "Squat", "Overhead Press|OHP", "Bench"

### 1.2 Effective Volume

- **Chart type**: Stacked bar chart per session
- **Data**: Count of sets where RPE >= 7, grouped by family
- **Overlay**: Horizontal line at overall average effective sets per session
- **Purpose**: Answers whether enough hard work is being done per pattern. Sets below RPE 7 are warm-ups or junk volume and don't drive meaningful adaptation.

### 1.3 Volume-Strength Relationship

- **Chart type**: Scatter plot, one subplot per compound family (Squat, Hinge, Push H, Push V)
- **Data**: X-axis = weekly total tonnage for that family. Y-axis = e1RM change for that family that week (best e1RM this week minus best e1RM last week)
- **Overlay**: LOWESS or linear trendline if enough data points
- **Purpose**: Identify the volume sweet spot per lift — the range of weekly tonnage that correlates with the best strength gains. Too little = no stimulus, too much = accumulated fatigue.
- **Note**: Requires grouping data by ISO week. With 9 sessions over ~2 weeks, this will be sparse initially but becomes more useful over time.

### 1.4 Stall Detection

- **Format**: Printed table with color-coded status
- **Columns**: Movement, Current Best e1RM, Best e1RM (3 sessions ago), Delta (kg), Status
- **Status logic**:
  - **Progressing** (green): delta > 0
  - **Plateaued** (amber): delta == 0 or within +/- 1kg
  - **Regressing** (red): delta < -1kg
- **Scope**: Key compounds only (Deadlift, Squat, OHP, Bench, Row)
- **Purpose**: Quick health check. Stalling lifts need programming changes.

## Section 2: Recovery & Fatigue Monitoring

### 2.1 Training Frequency Heatmap

- **Chart type**: Calendar heatmap (days as columns, weeks as rows)
- **Color**: Intensity based on session tonnage or average RPE
- **Blank cells**: Rest days (no JSON file for that date)
- **Summary stats printed below**:
  - Average days between sessions
  - Average days between training the same family
  - Longest rest gap
- **Purpose**: Visualise training rhythm. Reveals clustering (too many hard sessions in a row) or excessive rest.

### 2.2 Fatigue Accumulation Index

- **Chart type**: Dual-axis line chart
- **Left axis**: Fatigue index per session = total sets x mean RPE. Plotted with a 3-session rolling average.
- **Right axis**: Session-best e1RM for a reference compound (highest-priority based on milestones)
- **Purpose**: When fatigue is climbing but e1RM is flat or dropping, that signals overreaching. The divergence between the two lines is the actionable insight — time for a deload or reduced volume.

### 2.3 RPE Drift Within Sessions

- **Chart type**: Paired bar or slope chart, one pair per session date
- **Data**: Mean RPE of first half of sets vs mean RPE of second half of sets (by order recorded)
- **Purpose**: Steep RPE climb within a session suggests too much volume per session or insufficient rest between sets. Flat RPE drift indicates good session management.

## Section 3: Session Recommender

### Overview

A single cell that analyses current state and prints a recommended next session as a formatted table. No ML — rule-based logic using the data already tracked.

### Algorithm

**Step 1: Score each compound family for priority**

```
priority_score = milestone_gap_weight * days_since_last_trained
```

- `milestone_gap_weight`: `(target_e1rm - current_e1rm) / target_e1rm` — how far from the goal (0 = achieved, 1 = no progress). Use the closest milestone target per lift.
- `days_since_last_trained`: Calendar days since the family was last hit.
- Higher score = higher priority.

**Step 2: Select main lifts (1-2 compounds)**

- Pick the family with the highest priority score. Select the most frequently used movement from that family as the main lift.
- Optionally pick a second compound if it is antagonistic to the first AND has a priority score above the median. Antagonistic pairings:
  - Squat + Push (V)
  - Hinge + Push (H)
  - Push (H) + Pull (H)
  - Push (V) + Pull (V)
- Never pair two lifts from the same family.

**Step 3: Suggest working weight & reps**

- Look up the most recent session data for the selected movement.
- If the stall detector shows "Progressing": suggest last session's top working weight + 2.5kg at the same reps, OR same weight + 1 rep.
- If "Plateaued" or "Regressing": suggest switching rep range. If the lifter was doing heavy singles (1-3 reps), suggest a moderate block (5x5 at ~80% of e1RM). If doing moderate reps, suggest heavy work.
- Include warm-up sets: suggest 2-3 ramp-up sets at ~50%, ~70%, ~85% of working weight.

**Step 4: Add accessories (2-3 movements)**

- Select from families that complement the compounds and were under-represented in recent sessions.
- Prefer movements the lifter has done before (exists in the data).
- Always include one arm movement.
- Suggest 3 sets of 8-12 reps at the last-used weight for each accessory.

**Step 5: Output**

Printed table:

```
=== Recommended Next Session ===
Focus: Squat progression + Pull (V) catch-up

Movement              | Sets x Reps | Load (kg) | Rationale
-------------------------------------------------------------------
Squat (warm-up)       | 1 x 8       | 40        | Ramp-up
Squat (warm-up)       | 1 x 5       | 70        | Ramp-up
Squat (working)       | 5 x 5       | 85        | +2.5kg from last
Pull Ups              | 3 x 8       | BW        | Pattern catch-up
Tricep Pushdown       | 3 x 12      | 35        | Accessory
Bicep Curl            | 3 x 12      | 25        | Accessory

Estimated tonnage: ~4,850 kg
```

### Edge Cases

- **First session ever for a movement**: Cannot suggest progression. Default to a conservative starting point or skip.
- **All milestones achieved for a lift**: Deprioritise that family; it still appears but only as maintenance volume.
- **Negative loads (assisted movements)**: Exclude from e1RM and tonnage calculations. Track separately as bodyweight progression (decreasing assistance = progress).

## Implementation Notes

- All new analysis goes into new cells at the end of the existing notebook, following the current section pattern (markdown header cell + code cell).
- Update `MILESTONES` dict to reflect the revised targets (Deadlift 160x5, Squat 160x1/100x20).
- The recommender should be the final cell so it always reflects the latest synced data.
- No external dependencies beyond what's already used (pandas, numpy, matplotlib, seaborn).

## Cell Order (new cells)

1. `## Programming Effectiveness: Rate of Progression` (markdown + code)
2. `## Programming Effectiveness: Effective Volume` (markdown + code)
3. `## Programming Effectiveness: Volume-Strength Relationship` (markdown + code)
4. `## Programming Effectiveness: Stall Detection` (markdown + code)
5. `## Recovery: Training Frequency Heatmap` (markdown + code)
6. `## Recovery: Fatigue Accumulation` (markdown + code)
7. `## Recovery: RPE Drift Within Sessions` (markdown + code)
8. `## Recommended Next Session` (markdown + code)
