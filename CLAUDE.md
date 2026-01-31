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
Exercises are grouped into families for pattern balance analysis:
- **Squat**: Front Squat, Back Squat, Zercher Squat
- **Hinge**: Deadlift, Zercher Deadlift, Romanian Deadlift, Kettlebell Swings
- **Push (H)**: Bench Press, Incline Press, DB Press, Dips, Pullover
- **Push (V)**: Standing OHP, Overhead Press, DB Shoulder Press
- **Pull (H)**: Bent over Rows, Cable Rows
- **Pull (V)**: Pull Ups, Lat Pulldown
- **Isolation**: Bicep Curl, Tricep Pushdown
- **Core**: Cable Crunches

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
1. **Imports & Config** - Dependencies, FAMILY_MAP, MILESTONES, MOVEMENT_PATTERNS
2. **Sync JSON to Excel** - Reads `data/*.json`, deduplicates by timestamp (extracted from filename if missing), appends to Excel
3. **Load & Prepare Data** - Loads Excel, adds Date/Family/e1RM columns
4. **Session Tonnage Over Time** - Bar chart with 3-session moving average + RPE trend
5. **Latest Session Analysis** - Volume pie chart by family + Load vs RPE scatter
6. **Strength Matrix** - Horizontal bar chart of current e1RM by movement
7. **Movement Pattern Balance** - Radar charts comparing latest session vs all-time
8. **Volume Composition** - Stacked area chart by family over time
9. **2026 Milestone Progress** - Progress bars toward strength goals with summary table
