import pandas as pd
import numpy as np
import json
import glob
import os
from datetime import datetime

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/")
EXCEL_FILE = "workout_log.xlsx"
LOOKBACK_SESSIONS = 5

FAMILY_MAP = {
    "Front Squat": "Squat", "Back Squat": "Squat", "Zercher Squat": "Squat",
    "Squat": "Squat", "Squats": "Squat", "Pause Squat": "Squat",
    "Deadlift": "Hinge", "Zercher Deadlift": "Hinge", "Romanian Deadlift": "Hinge",
    "RDL": "Hinge", "Kettlebell Swings": "Hinge",
    "Barbell Bench Press": "Push (H)", "Bench Press": "Push (H)",
    "Incline BB Press": "Push (H)", "DB Press": "Push (H)",
    "Incline DB Press": "Push (H)", "Incline DB Fly": "Push (H)", "Incline DB Flys": "Push (H)",
    "Incline Dumbbell Press": "Push (H)", "Dumbbell Press": "Push (H)",
    "Dips": "Push (H)", "Assisted Dip": "Push (H)", "Assisted Dips": "Push (H)",
    "Dumbbell Pullover": "Push (H)", "Chest Fly": "Push (H)",
    "Standing BTN Press": "Push (V)", "BTN Standing Press": "Push (V)",
    "Behind the Neck Press": "Push (V)", "Behind the Neck Standing Overhead Press": "Push (V)",
    "Standing OHP": "Push (V)", "Overhead Press": "Push (V)", "DB Shoulder Press": "Push (V)",
    "Standing Overhead Press": "Push (V)",
    "Bent over Barbell Rows": "Pull (H)", "Bent over barbell row": "Pull (H)", "Cable Rows": "Pull (H)",
    "Bent Over Row": "Pull (H)", "Seated Cable Rows": "Pull (H)", "Seated Row": "Pull (H)",
    "Dumbbell Rows": "Pull (H)", "Rear Delt Fly": "Pull (H)",
    "Pull Ups": "Pull (V)", "Lat Pulldown": "Pull (V)",
    "Assisted Pullup": "Pull (V)", "Assisted Pullups": "Pull (V)",
    "Incline Bicep Curl": "Arms", "Barbell Bicep Curl": "Arms",
    "Cable Bicep Curl": "Arms", "Cable Tricep Pushdown": "Arms",
    "Bicep Curl": "Arms", "Bicep Curls": "Arms", "Dumbbell Curls": "Arms",
    "Overhead Tricep Ext": "Arms", "Tricep Extension": "Arms", "Tricep Pushdown": "Arms",
    "Cable Crunches": "Core",
    "Run": "Cardio"
}

FAMILY_KEYWORDS = [
    ("Behind the Neck", "Push (V)"), ("BTN", "Push (V)"),
    ("OHP", "Push (V)"), ("Shoulder Press", "Push (V)"),
    ("Deadlift", "Hinge"), ("RDL", "Hinge"), ("Romanian", "Hinge"),
    ("Kettlebell", "Hinge"), ("Swing", "Hinge"),
    ("Squat", "Squat"),
    ("Bench", "Push (H)"), ("Chest Fly", "Push (H)"),
    ("Pullover", "Push (H)"), ("Dip", "Push (H)"),
    ("Rear Delt", "Pull (H)"), ("Row", "Pull (H)"),
    ("Pull Up", "Pull (V)"), ("Pullup", "Pull (V)"),
    ("Pulldown", "Pull (V)"), ("Lat Pull", "Pull (V)"),
    ("Overhead Press", "Push (V)"),
    ("Press", "Push (H)"), ("Fly", "Push (H)"),
    ("Curl", "Arms"), ("Bicep", "Arms"), ("Tricep", "Arms"),
    ("Crunch", "Core"), ("Ab ", "Core"),
    ("Run", "Cardio"), ("Cardio", "Cardio"),
]

MILESTONES = {
    "Squat": [(160, 1), (100, 20)],
    "Deadlift": [(200, 1), (160, 5)],
    "Overhead Press": [(60, 3), (40, 12)],
    "Bench Press": [(100, 1), (60, 10)],
    "barbell row": [(80, 6), (60, 12)],
    "Kettlebell": [(24, 80)]
}

ANTAGONISTIC_PAIRS = {
    "Squat": "Push (V)", "Push (V)": "Squat",
    "Hinge": "Push (H)", "Push (H)": "Hinge",
    "Pull (H)": "Push (H)", "Pull (V)": "Push (V)",
}

MOVEMENT_PATTERNS = ["Squat", "Hinge", "Push (H)", "Push (V)", "Pull (H)", "Pull (V)"]

# ==========================================
# FUNCTIONS
# ==========================================

def map_movement_to_family(movement):
    if movement in FAMILY_MAP:
        return FAMILY_MAP[movement]
    for keyword, family in FAMILY_KEYWORDS:
        if keyword.lower() in movement.lower():
            return family
    return "Other"

def sync_json_to_excel(data_dir=DATA_DIR, excel_filename=EXCEL_FILE):
    excel_path = os.path.join(data_dir, excel_filename)
    existing_timestamps = set()
    
    if os.path.exists(excel_path):
        try:
            df_existing = pd.read_excel(excel_path)
            if not df_existing.empty:
                existing_timestamps = set(df_existing["Timestamp"].astype(str).str.strip().unique())
        except Exception as e:
            print(f"Warning reading Excel: {e}")
            df_existing = pd.DataFrame()
    else:
        df_existing = pd.DataFrame()

    new_records = []
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    for file in json_files:
        basename = os.path.splitext(os.path.basename(file))[0]
        try:
            file_ts = datetime.strptime(basename, "%Y%m%d_%H%M%S")
            file_ts_str = file_ts.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            file_ts_str = None
        
        try:
            with open(file, "r") as f:
                session_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        
        if not session_data: continue
            
        session_ts = str(session_data[0].get("Timestamp") or file_ts_str).strip()
        
        if session_ts not in existing_timestamps and session_ts != "None":
            for record in session_data:
                if not record.get("Timestamp") and file_ts_str:
                    record["Timestamp"] = file_ts_str
            new_records.extend(session_data)
            existing_timestamps.add(session_ts)

    if new_records:
        df_new = pd.DataFrame(new_records)
        if "Load_kg" in df_new.columns and "Reps" in df_new.columns:
            df_new["e1RM"] = df_new["Load_kg"] * (1 + df_new["Reps"] / 30)
        
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
        # Ensure correct column order if possible, but keep all
        df_final.to_excel(excel_path, index=False)
        print(f"Synced {len(new_records)} new records.")
    else:
        print("No new data to sync.")

def load_and_prepare_data(data_dir=DATA_DIR, excel_filename=EXCEL_FILE):
    excel_path = os.path.join(data_dir, excel_filename)
    df = pd.read_excel(excel_path)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Date"] = df["Timestamp"].dt.date
    df["Family"] = df["Movement"].apply(map_movement_to_family)
    df["e1RM"] = df["Load_kg"] * (1 + df["Reps"] / 30)
    return df

def recommend_session(df):
    today = df["Date"].max()
    
    # --- Step 1: Score each compound family by priority ---
    milestone_families = {
        "Squat": "Squat",
        "Deadlift": "Hinge",
        "Overhead Press": "Push (V)",
        "Bench Press": "Push (H)",
    }
    family_scores = {}
    family_milestone_gap = {}
    
    for search_term, family in milestone_families.items():
        matches = df[df["Movement"].str.contains(search_term, case=False, na=False)]
        current_e1rm = matches["e1RM"].max() if not matches.empty else 0
        
        if search_term in MILESTONES:
            target_e1rms = [w * (1 + r / 30) for w, r in MILESTONES[search_term]]
            closest_target = min(target_e1rms, key=lambda t: abs(t - current_e1rm))
            gap = max(0, (closest_target - current_e1rm) / closest_target) if closest_target > 0 else 0
        else:
            gap = 0.5
            
        fam_dates = df[df["Family"] == family]["Date"]
        days_since = (today - fam_dates.max()).days if not fam_dates.empty else 14
        family_scores[family] = gap * max(days_since, 1)
        family_milestone_gap[family] = gap

    # --- Step 2: Select 1-2 main compound lifts ---
    sorted_families = sorted(family_scores, key=family_scores.get, reverse=True)
    primary_family = sorted_families[0]
    
    secondary_family = None
    if primary_family in ANTAGONISTIC_PAIRS:
        candidate = ANTAGONISTIC_PAIRS[primary_family]
        median_score = np.median(list(family_scores.values()))
        if candidate in family_scores and family_scores[candidate] >= median_score * 0.5:
            secondary_family = candidate

    # --- Step 3: Pick specific movements and suggest weights ---
    recommendations = []
    for family in [primary_family] + ([secondary_family] if secondary_family else []):
        fam_df = df[df["Family"] == family]
        if fam_df.empty: continue
        
        top_movement = fam_df["Movement"].value_counts().index[0]
        move_df = fam_df[fam_df["Movement"] == top_movement].sort_values("Timestamp")
        
        working = move_df[move_df["Intensity_RPE"] >= 6]
        if working.empty: working = move_df
        
        last_weight = working.iloc[-1]["Load_kg"]
        last_reps = int(working.iloc[-1]["Reps"])
        
        best_per_session = move_df.groupby("Date")["e1RM"].max()
        if len(best_per_session) > LOOKBACK_SESSIONS:
            delta = best_per_session.iloc[-1] - best_per_session.iloc[:-LOOKBACK_SESSIONS].max()
        else:
            delta = best_per_session.iloc[-1] - best_per_session.iloc[0] if len(best_per_session) > 1 else 1
        is_stalling = delta <= 1

        if is_stalling and last_reps <= 5:
            work_weight = round(last_weight * 0.8 / 2.5) * 2.5
            work_reps = 5
            work_sets = 5
            rationale = "Stalling on heavy work -> volume block"
        elif is_stalling:
            work_weight = round(last_weight * 1.1 / 2.5) * 2.5
            work_reps = 3
            work_sets = 5
            rationale = "Stalling on volume -> heavy block"
        else:
            if last_reps >= 8:
                work_weight = last_weight + 2.5
                work_reps = last_reps
                work_sets = 3
                rationale = f"+2.5kg from last ({last_weight}kg x {last_reps})"
            else:
                work_weight = last_weight
                work_reps = last_reps + 1
                work_sets = 4
                rationale = f"+1 rep from last ({last_weight}kg x {last_reps})"

        warmup_loads = [
            round(work_weight * 0.5 / 2.5) * 2.5,
            round(work_weight * 0.7 / 2.5) * 2.5,
        ]
        
        if work_weight > 20:
            for wl in warmup_loads:
                if wl >= 20:
                    recommendations.append({
                        "Movement": f"{top_movement} (warm-up)",
                        "Sets x Reps": f"1 x {max(5, work_reps)}",
                        "Load (kg)": f"{wl:.0f}",
                        "Rationale": "Ramp-up"
                    })
        
        recommendations.append({
            "Movement": f"{top_movement} (working)",
            "Sets x Reps": f"{work_sets} x {work_reps}",
            "Load (kg)": f"{work_weight:.1f}",
            "Rationale": rationale
        })

    # --- Step 4: Add accessories ---
    recent_dates = sorted(df["Date"].unique())[-3:]
    recent_df = df[df["Date"].isin(recent_dates)]
    recent_family_counts = recent_df.groupby("Family").size()
    
    used_families = {primary_family, secondary_family} if secondary_family else {primary_family}
    accessory_families = [f for f in MOVEMENT_PATTERNS if f not in used_families]
    accessory_families.sort(key=lambda f: recent_family_counts.get(f, 0))
    
    for family in accessory_families[:2]:
        fam_df = df[df["Family"] == family]
        if fam_df.empty: continue
        top_move = fam_df["Movement"].value_counts().index[0]
        last_load = fam_df[fam_df["Movement"] == top_move].iloc[-1]["Load_kg"]
        recommendations.append({
            "Movement": top_move,
            "Sets x Reps": "3 x 10",
            "Load (kg)": f"{last_load:.0f}",
            "Rationale": f"{family} accessory"
        })

    arm_df = df[df["Family"] == "Arms"]
    if not arm_df.empty:
        arm_moves = arm_df["Movement"].value_counts().index[:2]
        for arm_move in arm_moves:
            last_arm = arm_df[arm_df["Movement"] == arm_move].iloc[-1]
            recommendations.append({
                "Movement": arm_move,
                "Sets x Reps": f"3 x {int(last_arm['Reps'])}",
                "Load (kg)": f"{last_arm['Load_kg']:.0f}",
                "Rationale": "Arms accessory"
            })

    # --- Step 5: Output ---
    focus_parts = [primary_family]
    if secondary_family:
        focus_parts.append(secondary_family)
        
    est_tonnage = 0
    for r in recommendations:
        try:
            sets_reps = r["Sets x Reps"].split(" x ")
            s, rp = int(sets_reps[0]), int(sets_reps[1])
            load = float(r["Load (kg)"])
            est_tonnage += s * rp * load
        except (ValueError, IndexError):
            pass

    print("=" * 70)
    print(f" RECOMMENDED NEXT SESSION")
    print(f" Focus: {' + '.join(focus_parts)}")
    print("=" * 70)
    print(f" {'Movement':<30} {'Sets x Reps':<14} {'Load (kg)':<12} {'Rationale'}")
    print("-" * 70)
    for r in recommendations:
        print(f"{r['Movement']:<30} {r['Sets x Reps']:<14} {r['Load (kg)']:<12} {r['Rationale']}")
    print("-" * 70)
    print(f" Estimated session tonnage: ~{est_tonnage:,.0f} kg")
    
    # Priority reasoning
    print(f" --- Priority Reasoning ---")
    for family in sorted_families:
        gap_pct = family_milestone_gap.get(family, 0) * 100
        fam_dates = df[df["Family"] == family]["Date"]
        days = (today - fam_dates.max()).days if not fam_dates.empty else 99
        print(f" {family:<10} score={family_scores[family]:.2f} (gap={gap_pct:.0f}%, {days}d since last)")

if __name__ == "__main__":
    sync_json_to_excel()
    df = load_and_prepare_data()
    recommend_session(df)
