# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal weightlifting tracker that syncs workout data from JSON files to an Excel log and generates visualizations for progress analysis. Built with Python, Jupyter notebooks, pandas, and matplotlib/seaborn.

## Architecture

### Data Flow
1. **Workout sessions** are recorded as JSON files in `data/` (filename format: `YYYYMMDD_HHMMSS.json`)
2. **Sync function** (`sync_json_to_excel`) reads JSON files, deduplicates by timestamp, calculates e1RM, and appends to `data/workout_log.xlsx`
3. **Analysis notebook** (`notebooks/update_log.ipynb`) loads the Excel file and generates visualizations

### Data Schema (JSON/Excel)
- `Movement`: Exercise name (e.g., "Overhead Press", "Zercher Deadlift")
- `Load_kg`: Weight in kilograms
- `Reps`: Number of repetitions
- `Volume_Load`: Load_kg × Reps (pre-calculated)
- `Intensity_RPE`: Rate of Perceived Exertion (1-10 scale)
- `Notes`: Optional text
- `Timestamp`: Session timestamp (used for deduplication)
- `e1RM`: Estimated 1-rep max, calculated as `Load_kg * (1 + Reps / 30)`

### Movement Family Mapping
Exercises are grouped into families via `FAMILY_MAP` (exact match) with `FAMILY_KEYWORDS` fallback (case-insensitive substring match). The `map_movement_to_family()` function tries exact match first, then keywords, then returns "Other" with a warning.
- **Squat**: Front Squat, Back Squat, Zercher Squat, Pause Squat
- **Hinge**: Deadlift, Zercher Deadlift, Romanian Deadlift, Kettlebell Swings
- **Push (H)**: Bench Press, Incline Press, DB Press, Dips, Pullover, Chest Fly
- **Push (V)**: Standing OHP, Overhead Press, DB Shoulder Press, Behind the Neck Press
- **Pull (H)**: Bent over Rows, Cable Rows, Seated Row, Rear Delt Fly
- **Pull (V)**: Pull Ups, Lat Pulldown, Assisted Pullups
- **Arms**: Bicep Curl, Tricep Pushdown, Tricep Extension, Dumbbell Curls
- **Core**: Cable Crunches
- **Cardio**: Run

## Running the Notebook

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # Unix

# Run Jupyter
jupyter notebook notebooks/update_log.ipynb
```

## Notebook Structure

Run all cells sequentially:
1. **Imports & Config** - Dependencies, FAMILY_MAP, FAMILY_KEYWORDS, map_movement_to_family(), MILESTONES, ANTAGONISTIC_PAIRS, MOVEMENT_PATTERNS
2. **Sync JSON to Excel** - Reads `data/*.json`, deduplicates by timestamp (extracted from filename if missing), appends to Excel
3. **Load & Prepare Data** - Loads Excel, adds Date/Family/e1RM columns, warns on unmapped movements
4. **Session Tonnage Over Time** - Bar chart with 3-session moving average + RPE trend
5. **Latest Session Analysis** - Volume pie chart by family + Load vs RPE scatter
6. **Strength Matrix** - Horizontal bar chart of current e1RM by movement
7. **e1RM Progression Over Time** - Line chart of session-best e1RM per key compound
8. **Movement Pattern Balance** - Radar charts comparing latest session vs all-time
9. **Volume Composition** - Stacked area chart by family over time
10. **Set Quality & Training Intensity** - Volume vs RPE scatter + RPE distribution histogram
11. **Training Style Analysis** - Rep range distribution + volume per set efficiency
12. **2026 Milestone Progress** - Progress bars toward strength goals with summary table
13. **Relative Strength & Lift Ratios** - Actual vs expected lift ratios + balance radar
14. **PR Timeline & Records** - Personal records scatter + cumulative PR count
15. **Rate of Progression** - e1RM trendlines with kg/week slope per compound (uses scipy)
16. **Effective Volume** - Stacked bar of RPE>=7 sets per session by family
17. **Volume-Strength Relationship** - Weekly tonnage vs e1RM change scatter per family
18. **Stall Detection** - Color-coded table: Progressing/Plateaued/Regressing per compound
19. **Training Frequency Heatmap** - Calendar heatmap of training days + rest gap stats
20. **Fatigue Accumulation** - Dual-axis: fatigue index (sets x RPE) vs session-best e1RM
21. **RPE Drift Within Sessions** - First-half vs second-half RPE comparison per session
22. **Recommended Next Session** - Rule-based recommender: priority scoring, progressive loading, accessories + arms
