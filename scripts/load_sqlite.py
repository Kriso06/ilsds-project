import sqlite3
import pandas as pd
from config import(
    RAW_PARQUET_FILES,
    SCALE_SIZES,
    SQLITE_DB,
    SQLITE_DIR,
    TRIP_COLUMNS,
    ZONE_LOOKUP_FILE,
)

def ensure_dirs():
    SQLITE_DIR.mkdir(parents=True, exist_ok=True)

def main():
    ensure_dirs()
    print("Reading parquet files...")
    dfs=[]
    for file in RAW_PARQUET_FILES:
        df=pd.read_parquet(file, columns=TRIP_COLUMNS)
        dfs.append(df)
        print(f"Loaded {file.name}: {len(df)} rows")
    
    trips_df=pd.concat(dfs, ignore_index=True)
    trips_df=trips_df.sort_values("tpep_pickup_datetime").reset_index(drop=True)

    print("Reading zone lookups...")
    zones_df=pd.read_csv(ZONE_LOOKUP_FILE)

    print("Writing to SQLite...")
    conn=sqlite3.connect(SQLITE_DB)

    trips_df.to_sql("trips_all", conn, if_exists="replace", index=False)
    zones_df.to_sql("zones", conn, if_exists="replace", index=False)

    total_rows=len(trips_df)
    print("Total rows in trip_all:", total_rows)

    for scale in SCALE_SIZES:
        if scale<=total_rows:
            table_name=f"trips_{scale}"
            subset_df=trips_df.iloc[:scale]
            subset_df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"Created table: {table_name}")

    print("Creating indexes...")
    index_statements=[
        "CREATE INDEX IF NOT EXISTS idx_trips_all_pickup_datetime ON trips_all(tpep_pickup_datetime)",
        "CREATE INDEX IF NOT EXISTS idx_trips_all_pu ON trips_all(PULocationID)",
        "CREATE INDEX IF NOT EXISTS idx_trips_all_do ON trips_all(DOLocationID)",
        "CREATE INDEX IF NOT EXISTS idx_trips_all_payment_type ON trips_all(payment_type)",
        "CREATE INDEX IF NOT EXISTS idx_zones_location_id ON zones(LocationID)",
    ]

    for scale in SCALE_SIZES:
        if scale<=total_rows:
            table_name=f"trips_{scale}"
            index_statements.extend([
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_pickup_datetime ON {table_name}(tpep_pickup_datetime)",
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_pu ON {table_name}(PULocationID)",
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_do ON {table_name}(DOLocationID)",
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_payment_type ON {table_name}(payment_type)",
            ])

    for stmt in index_statements:
        conn.execute(stmt)

    conn.commit()
    conn.close()
    print("SQLite loading complete.")

if __name__=="__main__":
    main()

