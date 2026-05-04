from pathlib import Path
import pandas as pd

files = [
    Path("data/raw/yellow_tripdata_2026-01.parquet"),
    Path("data/raw/yellow_tripdata_2026-02.parquet"),
    Path("data/raw/yellow_tripdata_2026-03.parquet"),
]

all_columns = {}

for file in files:
    df = pd.read_parquet(file)
    cols = df.columns.tolist()
    all_columns[file.name] = cols

for name, cols in all_columns.items():
    print(f"\n{name}")
    print(cols)

common_columns = set(all_columns[files[0].name])
for file in files[1:]:
    common_columns &= set(all_columns[file.name])

print("\nCommon columns in all files:")
print(sorted(common_columns))

total = 0
for file in files:
    df = pd.read_parquet(file, columns=["VendorID"])
    count = len(df)
    total += count
    print(file.name, count)

print("Total rows:", total)