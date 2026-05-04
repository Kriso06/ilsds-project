from pathlib import Path
import duckdb
from config import (
    DUCKDB_DB,
    DUCKDB_DIR,
    RAW_PARQUET_FILES,
    SCALE_SIZES,
    TRIP_COLUMNS,
    ZONE_LOOKUP_FILE,
)

def ensure_dirs():
    DUCKDB_DIR.mkdir(parents=True, exist_ok=True)

def main():
    ensure_dirs()
    con=duckdb.connect(str(DUCKDB_DB))
    parquet_list=", ".join([f"'{str(path)}'" for path in RAW_PARQUET_FILES])
    trip_cols_sql=", ".join(TRIP_COLUMNS)

    con.execute(f"""
        CREATE OR REPLACE TABLE trips_all AS
        SELECT {trip_cols_sql}
        FROM read_parquet([{parquet_list}])
        ORDER BY tpep_pickup_datetime
    """)

    con.execute(f"""
        CREATE OR REPLACE TABLE zones AS 
        SELECT * 
        FROM read_csv_auto('{str(ZONE_LOOKUP_FILE)}', HEADER=TRUE)
    """)

    total_rows=con.execute("SELECT COUNT(*) FROM trips_all").fetchone()[0]
    print("Total rows in trips_all:", total_rows)

    for scale in SCALE_SIZES:
        if scale<=total_rows:
            table_name=f"trips_{scale}"
            con.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT *
                FROM trips_all
                LIMIT {scale}
            """)
            print(f"Created table: {table_name}")
        
    con.close()

if __name__=="__main__":
    main()