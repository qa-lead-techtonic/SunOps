import json
import pandas as pd
import os

# ============================================================
# CONFIGURATION – EDIT THESE VARIABLES FOR EACH RUN
# ============================================================

# File paths
JSON_FILE = r"C:\Users\c_techtonicstesting2\OneDrive - FTC Solar\sundat-20260507T103506Z-3-001\Sundat_Asbuilt\Tatapower\Tatapower_Akash.json"
EXCEL_FILE = r"C:\Users\c_techtonicstesting2\OneDrive - FTC Solar\sundat-20260507T103506Z-3-001\Sundat_Asbuilt\Asbuilt\TP Akash Block-10_filtered_withcalc.xlsx"
OUTPUT_FILE = r"C:\Users\c_techtonicstesting2\OneDrive - FTC Solar\sundat-20260507T103506Z-3-001\Sundat_Asbuilt\Tatapower\Tatapower_Akash_AI.json"
# Column names in the Excel file
TRACKER_COLUMN = "Tracker No"               # column that matches the JSON tableName
PILE_DISTANCE_COLUMN = "Pile Distance"      # column with pile distances

# Columns for the "original" four fields (TopRight / BottomLeft)
ADJUSTED_LAT_COLUMN = "AdjustedLat"         # column for adjusted latitude
ADJUSTED_LONG_COLUMN = "AdjustedLong"       # column for adjusted longitude

# Columns for the "new" four fields (TopPile / BottomPile)
LATITUDE_COLUMN = "Latitude"                # column for raw latitude
LONGITUDE_COLUMN = "Longitude"              # column for raw longitude

# ============================================================
# SCRIPT – DO NOT EDIT BELOW UNLESS YOU KNOW WHAT YOU'RE DOING
# ============================================================

print(f"\n{'='*60}")
print("Starting update with configuration:")
print(f"  JSON file               : {JSON_FILE}")
print(f"  Excel file              : {EXCEL_FILE}")
print(f"  Output file             : {OUTPUT_FILE}")
print(f"  Tracker column          : {TRACKER_COLUMN}")
print(f"  Pile distance col       : {PILE_DISTANCE_COLUMN}")
print(f"  Adjusted latitude col   : {ADJUSTED_LAT_COLUMN}")
print(f"  Adjusted longitude col  : {ADJUSTED_LONG_COLUMN}")
print(f"  Raw latitude col        : {LATITUDE_COLUMN}")
print(f"  Raw longitude col       : {LONGITUDE_COLUMN}")
print(f"{'='*60}\n")

# ---- Validate JSON file ----
if not os.path.exists(JSON_FILE):
    print(f"❌ JSON file not found: {JSON_FILE}")
    dir_path = os.path.dirname(JSON_FILE)
    if os.path.exists(dir_path):
        print(f"📁 Contents of {dir_path}:")
        for f in os.listdir(dir_path):
            print(f"   - {f}")
    exit(1)

# ---- Validate Excel file ----
if not os.path.exists(EXCEL_FILE):
    print(f"❌ Excel file not found: {EXCEL_FILE}")
    dir_path = os.path.dirname(EXCEL_FILE)
    if os.path.exists(dir_path):
        print(f"📁 Contents of {dir_path}:")
        for f in os.listdir(dir_path):
            print(f"   - {f}")
    exit(1)

# Load JSON
with open(JSON_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Load Excel
df = pd.read_excel(EXCEL_FILE)

# Clean column names (remove non‑breaking spaces and extra spaces)
df.columns = df.columns.str.replace('\u00a0', '').str.strip()

# Ensure required columns exist
required_cols = [
    TRACKER_COLUMN,
    PILE_DISTANCE_COLUMN,
    ADJUSTED_LAT_COLUMN,
    ADJUSTED_LONG_COLUMN,
    LATITUDE_COLUMN,
    LONGITUDE_COLUMN
]
for col in required_cols:
    if col not in df.columns:
        print(f"❌ Column '{col}' not found in Excel file. Available columns: {list(df.columns)}")
        exit(1)

# Convert data types
df[TRACKER_COLUMN] = df[TRACKER_COLUMN].astype(str).str.strip().str.upper()
df[PILE_DISTANCE_COLUMN] = pd.to_numeric(df[PILE_DISTANCE_COLUMN], errors="coerce")
df[ADJUSTED_LAT_COLUMN] = pd.to_numeric(df[ADJUSTED_LAT_COLUMN], errors="coerce")
df[ADJUSTED_LONG_COLUMN] = pd.to_numeric(df[ADJUSTED_LONG_COLUMN], errors="coerce")
df[LATITUDE_COLUMN] = pd.to_numeric(df[LATITUDE_COLUMN], errors="coerce")
df[LONGITUDE_COLUMN] = pd.to_numeric(df[LONGITUDE_COLUMN], errors="coerce")

updated_count = 0
for table in data.get("tableDetails", []):
    tracker_name = str(table.get("tableName", "")).strip().upper()

    # --- Remove unwanted fields ---
    # 1. Remove sundatTablePosition if present
    if "sundatTablePosition" in table:
        del table["sundatTablePosition"]
    # 2. Remove latitude and longitude if present
    if "latitude" in table:
        del table["latitude"]
    if "longitude" in table:
        del table["longitude"]
    # 3. Remove concatenated fields if present
    if "toplatlong" in table:
        del table["toplatlong"]
    if "bottomlatlong" in table:
        del table["bottomlatlong"]

    tracker_rows = df[df[TRACKER_COLUMN] == tracker_name]

    if tracker_rows.empty:
        print(f"⚠️ No Excel match found for tracker: {tracker_name}")
        # Set all eight fields to None
        table["TopRightLatitude"] = None
        table["TopRightLongitude"] = None
        table["BottomLeftLatitude"] = None
        table["BottomLeftLongitude"] = None
        table["TopPileLatitude"] = None
        table["TopPileLongitude"] = None
        table["BottomPileLatitude"] = None
        table["BottomPileLongitude"] = None
        continue

    # ---- TOP PILE (Pile Distance = 0) ----
    top_rows = tracker_rows[tracker_rows[PILE_DISTANCE_COLUMN] == 0]
    if not top_rows.empty:
        top_row = top_rows.iloc[0]
        # Adjusted coordinates for TopRight / BottomLeft fields
        top_adj_lat = round(float(top_row[ADJUSTED_LAT_COLUMN]), 6) if not pd.isna(top_row[ADJUSTED_LAT_COLUMN]) else None
        top_adj_lon = round(float(top_row[ADJUSTED_LONG_COLUMN]), 6) if not pd.isna(top_row[ADJUSTED_LONG_COLUMN]) else None
        # Raw coordinates for TopPile fields
        top_raw_lat = round(float(top_row[LATITUDE_COLUMN]), 6) if not pd.isna(top_row[LATITUDE_COLUMN]) else None
        top_raw_lon = round(float(top_row[LONGITUDE_COLUMN]), 6) if not pd.isna(top_row[LONGITUDE_COLUMN]) else None
    else:
        top_adj_lat, top_adj_lon = None, None
        top_raw_lat, top_raw_lon = None, None

    # ---- BOTTOM PILE (max Pile Distance > 0) ----
    bottom_rows = tracker_rows[tracker_rows[PILE_DISTANCE_COLUMN] > 0]
    if not bottom_rows.empty:
        bottom_row = bottom_rows.loc[bottom_rows[PILE_DISTANCE_COLUMN].idxmax()]
        # Adjusted coordinates for BottomLeft fields
        bottom_adj_lat = round(float(bottom_row[ADJUSTED_LAT_COLUMN]), 6) if not pd.isna(bottom_row[ADJUSTED_LAT_COLUMN]) else None
        bottom_adj_lon = round(float(bottom_row[ADJUSTED_LONG_COLUMN]), 6) if not pd.isna(bottom_row[ADJUSTED_LONG_COLUMN]) else None
        # Raw coordinates for BottomPile fields
        bottom_raw_lat = round(float(bottom_row[LATITUDE_COLUMN]), 6) if not pd.isna(bottom_row[LATITUDE_COLUMN]) else None
        bottom_raw_lon = round(float(bottom_row[LONGITUDE_COLUMN]), 6) if not pd.isna(bottom_row[LONGITUDE_COLUMN]) else None
    else:
        bottom_adj_lat, bottom_adj_lon = None, None
        bottom_raw_lat, bottom_raw_lon = None, None

    # ---- Update fields ----
    # Original four fields using Adjusted coordinates
    table["TopRightLatitude"] = top_adj_lat
    table["TopRightLongitude"] = top_adj_lon
    table["BottomLeftLatitude"] = bottom_adj_lat
    table["BottomLeftLongitude"] = bottom_adj_lon

    # New four fields using Raw coordinates
    table["TopPileLatitude"] = top_raw_lat
    table["TopPileLongitude"] = top_raw_lon
    table["BottomPileLatitude"] = bottom_raw_lat
    table["BottomPileLongitude"] = bottom_raw_lon

    print(f"✅ Updated {tracker_name}")
    updated_count += 1

# Save updated JSON
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, allow_nan=False)

print(f"\n🎯 Update completed. {updated_count} trackers processed.")
print(f"📄 Output saved to: {OUTPUT_FILE}")