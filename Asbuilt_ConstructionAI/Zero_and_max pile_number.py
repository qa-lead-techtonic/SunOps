import pandas as pd

# Input and output file names
input_file = "TP Akash Block-10.csv"
output_file = "TP Akash Block-10_filtered.csv"

# Read CSV
df = pd.read_csv(input_file)

# Forward fill missing Tracker No (blanks belong to the previous tracker)
df["Tracker No"] = df["Tracker No"].replace('', pd.NA).fillna(method='ffill')

# Ensure Pile (Tag nos) is numeric
df["Pile (Tag nos)"] = pd.to_numeric(df["Pile (Tag nos)"], errors="coerce")

# Drop any rows where Tracker No is still missing (if any)
df = df.dropna(subset=["Tracker No"])

# For each tracker, get the rows with min and max pile number
min_rows = df.loc[df.groupby("Tracker No")["Pile (Tag nos)"].idxmin()]
max_rows = df.loc[df.groupby("Tracker No")["Pile (Tag nos)"].idxmax()]

# Combine both sets (min and max) and remove duplicate if a tracker has only one row
filtered_df = pd.concat([min_rows, max_rows]).drop_duplicates()

# Sort for clean output
filtered_df = filtered_df.sort_values(by=["Tracker No", "Pile (Tag nos)"])

# Save to new CSV
filtered_df.to_csv(output_file, index=False)

print("Filtering completed. Output saved as:", output_file)