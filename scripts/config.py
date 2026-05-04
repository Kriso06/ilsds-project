from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parent.parent

DATA_DIR=PROJECT_ROOT/"data"
RAW_DIR=DATA_DIR/"raw"
SQLITE_DIR=DATA_DIR/"sqlite"
DUCKDB_DIR=DATA_DIR/"duckdb"
GENERATED_DIR=DATA_DIR/"generated"

OUTPUTS_DIR=PROJECT_ROOT/"outputs"
METRICS_DIR=OUTPUTS_DIR/"metrics"
PLANS_DIR=OUTPUTS_DIR/"plans"
PLOTS_DIR=OUTPUTS_DIR/"plots"

RAW_PARQUET_FILES=[
    RAW_DIR/"yellow_tripdata_2026-01.parquet",
    RAW_DIR/"yellow_tripdata_2026-02.parquet",
    RAW_DIR/"yellow_tripdata_2026-03.parquet",
]

ZONE_LOOKUP_FILE=RAW_DIR/"taxi_zone_lookup.csv"

SQLITE_DB=SQLITE_DIR/"nyc_taxi_benchmark.sqlite"
DUCKDB_DB=DUCKDB_DIR/"nyc_taxi_benchmark.duckdb"

SCALE_SIZES=[1_000_000, 3_000_000, 5_000_000, 10_000_000]
BENCHMARK_RUNS=3

TRIP_COLUMNS=[
    "VendorID",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "RatecodeID",
    "store_and_fwd_flag",
    "PULocationID",
    "DOLocationID",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "Airport_fee",
    "cbd_congestion_fee",
]