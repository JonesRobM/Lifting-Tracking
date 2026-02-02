# Lifting Tracker

Personal weightlifting progress tracker that syncs workout data from JSON files to Excel, calculates training metrics, and generates visualizations for strength analysis.

## Quick Start

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix

# Launch notebook
jupyter notebook notebooks/update_log.ipynb

# Run all cells sequentially
```

## How It Works

### Workflow

1. **Record workouts** as JSON files in `data/` (one file per session)
2. **Run the notebook** to sync JSON to Excel and generate visualizations
3. **Review progress** through charts tracking volume, strength, and balance

### Data Flow

```
data/*.json  -->  sync_json_to_excel()  -->  data/workout_log.xlsx
                                                      |
                                                      v
                                            load_and_prepare_data()
                                                      |
                                                      v
                                              Visualizations
```

## Recording Workouts

Create a JSON file in `data/` with filename format `YYYYMMDD_HHMMSS.json`:

```json
[
  {
    "Movement": "Back Squat",
    "Load_kg": 100,
    "Reps": 5,
    "Volume_Load": 500,
    "Intensity_RPE": 8,
    "Notes": "Felt strong"
  }
]
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `Movement` | string | Exercise name (must match FAMILY_MAP for grouping) |
| `Load_kg` | number | Weight in kilograms |
| `Reps` | integer | Repetitions performed (use 0 for failed attempts) |
| `Volume_Load` | number | Load_kg x Reps (pre-calculated) |
| `Intensity_RPE` | number | Rate of Perceived Exertion (1-10 scale) |
| `Notes` | string | Optional context |

The `Timestamp` field is auto-extracted from the filename if not provided.

### Movement Naming

Use consistent naming to ensure proper family grouping:

| Family | Movements |
|--------|-----------|
| Squat | Front Squat, Back Squat, Zercher Squat |
| Hinge | Deadlift, Zercher Deadlift, Romanian Deadlift, RDL, Kettlebell Swings |
| Push (H) | Barbell Bench Press, Incline BB Press, DB Press, Incline DB Press, Dips, Dumbbell Pullover |
| Push (V) | Standing OHP, Overhead Press, DB Shoulder Press |
| Pull (H) | Bent over Barbell Rows, Cable Rows |
| Pull (V) | Pull Ups, Lat Pulldown |
| Isolation | Incline Bicep Curl, Barbell Bicep Curl, Cable Bicep Curl, Cable Tricep Pushdown |
| Core | Cable Crunches |

Movements not in `FAMILY_MAP` are assigned to "Other".

## Notebook Sections

Run cells sequentially. Each section builds on previous data.

### 1. Imports & Config

- Sets plot styling (matplotlib/seaborn)
- Defines `FAMILY_MAP` for movement grouping
- Defines `MILESTONES` for 2026 strength goals
- Defines `MOVEMENT_PATTERNS` for radar charts

### 2. Sync JSON to Excel

`sync_json_to_excel()` reads all `data/*.json` files:
- Deduplicates by timestamp (prevents re-importing same session)
- Calculates e1RM: `Load_kg * (1 + Reps / 30)`
- Appends new sets to `data/workout_log.xlsx`

### 3. Load & Prepare Data

`load_and_prepare_data()` loads Excel and adds derived columns:
- `Date`: Extracted from Timestamp
- `Family`: Mapped from Movement via FAMILY_MAP
- `e1RM`: Estimated 1-rep max

### 4. Session Tonnage Over Time

**Bar chart + line chart** showing:
- Session volume (total kg lifted)
- 3-session moving average trend
- Average RPE per session

Use this to track training load progression and fatigue.

### 5. Latest Session Analysis

**Pie charts + scatter plot** showing:
- Volume distribution by family (latest session vs all-time)
- Top sets: Load vs RPE scatter

Identifies session focus and set quality.

### 6. Strength Matrix

**Horizontal bar chart** of current best e1RM for each movement, grouped by family.

Quick view of current strength levels across all lifts.

### 7. e1RM Progression Over Time

**Line chart** tracking estimated 1RM progression for key compound movements (Deadlift, Squat, Press, Bench, Row).

Shows strength gains over time.

### 8. Movement Pattern Balance

**Radar charts** comparing volume distribution across movement patterns:
- Latest session balance
- All-time balance

Identifies training imbalances (e.g., too much push, not enough pull).

### 9. Volume Composition Over Time

**Stacked area chart** showing how training volume is distributed across families over time.

Reveals training emphasis shifts.

### 10. Set Quality & Training Intensity

**Scatter plot + histogram** showing:
- Volume vs RPE by family
- RPE distribution across all sets

Tracks training intensity and "effective sets" (RPE >= 7).

### 11. Training Style Analysis

**Bar charts** showing:
- Rep range distribution (Strength/Power/Hypertrophy/Endurance/Conditioning)
- Session density (average volume per set)

Reveals dominant training style.

### 12. 2026 Milestone Progress

**Progress bars** showing current e1RM vs target goals defined in `MILESTONES`.

Configured goals:
- Squat: 100kg x 20, 140kg x 5
- Deadlift: 200kg x 1, 140kg x 8
- Overhead Press: 60kg x 3, 40kg x 12
- Bench Press: 100kg x 2, 60kg x 10
- Barbell Row: 80kg x 6, 60kg x 12
- Kettlebell Swings: 24kg x 80

### 13. Relative Strength & Lift Ratios

**Bar chart + radar chart** comparing actual strength ratios to biomechanical benchmarks:
- Deadlift = 1.0 (reference)
- Squat = 0.85
- Bench Press = 0.65
- Row = 0.65
- Overhead Press = 0.42

Identifies weak points in strength balance.

### 14. PR Timeline & Records

**Scatter plot + cumulative chart** showing:
- All personal records over time
- PR accumulation rate

Lists current PRs for each movement.

## Key Formulas

### Estimated 1-Rep Max (e1RM)

```
e1RM = Load_kg * (1 + Reps / 30)
```

Epley formula variant. Used for strength comparisons across different rep ranges.

### Volume Load

```
Volume_Load = Load_kg * Reps
```

Total work per set. Summed for session tonnage.

## File Structure

```
Lifting-Tracking/
├── data/
│   ├── YYYYMMDD_HHMMSS.json   # Workout session files
│   └── workout_log.xlsx        # Consolidated data (auto-generated)
├── notebooks/
│   └── update_log.ipynb        # Main analysis notebook
├── .venv/                      # Python virtual environment
├── CLAUDE.md                   # AI assistant instructions
└── README.md                   # This file
```

## Modifying Goals & Configuration

Edit the notebook's config cell to customize:

```python
# Add new movement mappings
FAMILY_MAP["Your New Movement"] = "Squat"

# Add/modify 2026 milestones
MILESTONES["Your Movement"] = [(weight_kg, reps), ...]

# Change patterns for radar charts
MOVEMENT_PATTERNS = ["Squat", "Hinge", ...]
```

## Troubleshooting

**"No new data to sync"**: All JSON files already imported. Check timestamps.

**Movement shows as "Other"**: Add it to `FAMILY_MAP` with correct family.

**Charts look wrong after editing data**: Re-run all cells from the top.

**Missing e1RM values**: Ensure both `Load_kg` and `Reps` are present in JSON.
