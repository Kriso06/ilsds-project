# SQLite vs DuckDB for Analytical Queries

This project benchmarks **SQLite** and **DuckDB** on analytical workloads using the **NYC TLC Yellow Taxi** dataset. The comparison focuses on:

- query execution latency
- Python-side memory consumption
- I/O behavior
- query optimizer and execution plans
- scalability from **1M to 10M rows**

## Objective

SQLite is a lightweight row-store database, while DuckDB is a columnar analytical database. This project evaluates how their different storage and execution models affect analytical query performance on the same workload and data.

## Dataset

This project uses monthly **Yellow Taxi Trip Records** from the official NYC Taxi & Limousine Commission (TLC) trip data portal, along with the taxi zone lookup table.

### Files Used

- `yellow_tripdata_2026-01.parquet`
- `yellow_tripdata_2026-02.parquet`
- `yellow_tripdata_2026-03.parquet`
- `taxi_zone_lookup.csv`

### Official Sources

- NYC TLC Trip Record Data portal: <https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>
- TLC Trip Record User Guide: <https://www.nyc.gov/assets/tlc/downloads/pdf/trip_record_user_guide.pdf>
- Yellow Taxi Data Dictionary: <https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf>

### Dataset Notes

- TLC publishes trip data monthly in **Parquet** format.
- The trip files include timestamps, trip distance, payment type, fare components, and pickup/dropoff location IDs.
- `taxi_zone_lookup.csv` maps `PULocationID` and `DOLocationID` to human-readable zones and boroughs.
- The three monthly files used here contain a combined total of **11,077,206 rows**.

## Project Structure

```text
ilsds-project/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ data/
│  ├─ raw/
│  │  ├─ yellow_tripdata_2026-01.parquet
│  │  ├─ yellow_tripdata_2026-02.parquet
│  │  ├─ yellow_tripdata_2026-03.parquet
│  │  └─ taxi_zone_lookup.csv
│  ├─ sqlite/
│  └─ duckdb/
├─ outputs/
│  ├─ metrics/
│  ├─ plans/
│  └─ plots/
└─ scripts/
   ├─ check_schema.py
   ├─ config.py
   ├─ load_duckdb.py
   ├─ load_sqlite.py
   ├─ queries.py
   ├─ benchmark.py
   └─ visualize.py
```

## Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Data Placement

Put the downloaded files inside:

```text
data/raw/
```

Expected files:

- `data/raw/yellow_tripdata_2026-01.parquet`
- `data/raw/yellow_tripdata_2026-02.parquet`
- `data/raw/yellow_tripdata_2026-03.parquet`
- `data/raw/taxi_zone_lookup.csv`

## Methodology

### Databases Compared

**SQLite**
- row-oriented embedded database
- suitable for lightweight and transactional workloads

**DuckDB**
- columnar analytical database
- optimized for OLAP-style scans, aggregations, and vectorized execution

### Workload Design

The benchmark includes 10 analytical queries covering:

- `GROUP BY`
- aggregations
- multi-table joins
- window functions
- top-k route and zone analysis
- filtered analytical queries

### Dataset Scales

The combined dataset was split into the following benchmark scales:

- `1,000,000`
- `3,000,000`
- `5,000,000`
- `10,000,000`

### Tables Created

For both SQLite and DuckDB:

- `trips_all`
- `trips_1000000`
- `trips_3000000`
- `trips_5000000`
- `trips_10000000`
- `zones`

### Metrics Collected

For each query, engine, and scale, the benchmark records:

- **Latency (`latency_ms`)**
  - total time taken to execute the query
- **Peak Python memory (`peak_python_mem_kb`)**
  - peak memory observed by Python using `tracemalloc`
- **I/O input blocks (`io_in_blocks`)**
  - block input operations reported by `resource.getrusage`
- **I/O output blocks (`io_out_blocks`)**
  - block output operations reported by `resource.getrusage`
- **Query plans**
  - `EXPLAIN`
  - `EXPLAIN ANALYZE`

### Important Limitations

- `tracemalloc` measures **Python-managed memory**, not the full native memory used internally by SQLite or DuckDB.
- `resource.getrusage()` I/O counters can be approximate, especially on macOS.
- SQLite and DuckDB are architecturally different, so the comparison should be interpreted as a practical performance study rather than a perfectly controlled engine-internals experiment.

## Schema Used

The benchmark uses the common schema found across all three monthly files:

- `VendorID`
- `tpep_pickup_datetime`
- `tpep_dropoff_datetime`
- `passenger_count`
- `trip_distance`
- `RatecodeID`
- `store_and_fwd_flag`
- `PULocationID`
- `DOLocationID`
- `payment_type`
- `fare_amount`
- `extra`
- `mta_tax`
- `tip_amount`
- `tolls_amount`
- `improvement_surcharge`
- `total_amount`
- `congestion_surcharge`
- `Airport_fee`
- `cbd_congestion_fee`

## Queries Benchmarked

The project benchmarks 10 queries:

1. Monthly trip counts
2. Revenue by payment type
3. Average fare and tip by passenger count
4. Top 10 pickup zones
5. Top 10 routes
6. Revenue by borough
7. Zone revenue ranking
8. Running daily revenue
9. Join-heavy payment/rate/borough analysis
10. Long and high-value trips by pickup hour

## Execution Order

Run the scripts in this order:

### 1. Check schema consistency

```bash
python3 scripts/check_schema.py
```

Purpose:
- confirms that all monthly parquet files have matching columns
- helps define the final `TRIP_COLUMNS` in `config.py`

### 2. Load data into DuckDB

```bash
python3 scripts/load_duckdb.py
```

Purpose:
- loads the combined trip dataset into DuckDB
- creates scaled benchmark tables
- loads the zone lookup table

### 3. Load data into SQLite

```bash
python3 scripts/load_sqlite.py
```

Purpose:
- loads the same data into SQLite
- creates equivalent scaled tables
- creates indexes for common filter and join columns

### 4. Run benchmark

```bash
python3 scripts/benchmark.py
```

Purpose:
- executes all benchmark queries on both engines
- captures latency, memory, I/O, and query plans
- writes metrics to CSV and JSON

### 5. Generate plots

```bash
python3 scripts/visualize.py
```

Purpose:
- reads the benchmark metrics
- aggregates repeated runs
- produces comparison plots

## Outputs

### 1. Metrics

Location:

```text
outputs/metrics/
```

Files:

- `benchmark_results.csv`
- `benchmark_results.json`

Meaning:
- these files contain the raw benchmark measurements for every run

Typical columns:

- `engine`
  - database used: `sqlite` or `duckdb`
- `scale_rows`
  - dataset size used for that run
- `query_name`
  - query identifier from `queries.py`
- `run_id`
  - benchmark repetition number
- `latency_ms`
  - execution time in milliseconds
- `peak_python_mem_kb`
  - peak Python memory during the run
- `io_in_blocks`
  - input block operations
- `io_out_blocks`
  - output block operations
- `result_row_count`
  - number of rows returned by the query

How to interpret:

- lower `latency_ms` means faster execution
- lower `peak_python_mem_kb` means lower Python-side memory overhead
- I/O values help indicate how block activity changes across engines and scales

### 2. Query Plans

Location:

```text
outputs/plans/
```

Files follow patterns like:

- `sqlite_q1_monthly_trip_counts_1000000_explain.txt`
- `sqlite_q1_monthly_trip_counts_1000000_explain_analyze.txt`
- `duckdb_q1_monthly_trip_counts_1000000_explain.txt`
- `duckdb_q1_monthly_trip_counts_1000000_explain_analyze.txt`

Meaning:

- these files show how each engine plans and executes the same SQL query
- they help compare optimizer behavior, scan strategy, and execution flow

How to interpret:

- check whether a query uses full scans, indexed access, joins, grouping steps, or specialized analytical operators
- DuckDB plans are generally more analytics-oriented
- SQLite plans may show index usage but can still be less efficient for large analytical scans

### 3. Plots

Location:

```text
outputs/plots/
```

Files:

- `latency_bar.png`
- `latency_vs_scale.png`
- `memory_vs_scale.png`
- `io_vs_scale.png`

Meaning of each plot:

#### `latency_bar.png`

- compares average query latency between SQLite and DuckDB
- usually shown for the largest dataset scale
- useful for identifying which specific queries benefit most from DuckDB

#### `latency_vs_scale.png`

- shows how query latency changes as row count increases
- useful for scalability analysis
- steeper growth indicates poorer scaling

#### `memory_vs_scale.png`

- compares Python-side memory usage across engines and dataset sizes
- useful for observing whether some workloads trigger larger temporary allocations

#### `io_vs_scale.png`

- compares total I/O block usage across scales
- useful for understanding how much block activity is associated with the benchmarked queries

## Expected Findings

Typical conclusions for this type of benchmark are:

- DuckDB generally performs better on analytical workloads, especially at larger scales.
- SQLite can be competitive on smaller datasets and simpler queries.
- Join-heavy and aggregation-heavy workloads usually show a clearer DuckDB advantage.
- Window functions and large scans often scale better in DuckDB because of its analytical execution model.
- SQLite benefits from indexes, but its row-store design is not optimized for large OLAP-style workloads.

## Reproducibility Notes

To reproduce results consistently:

- use the same three monthly Yellow Taxi files
- keep the same `TRIP_COLUMNS`
- use the same scale sizes
- run benchmarks on the same machine
- avoid heavy background processes during execution
- use the same number of benchmark repetitions

## GitHub Notes

Large raw data files and generated database files should **not** be committed to GitHub.

Recommended `.gitignore` entries:

```gitignore
data/raw/
data/sqlite/
data/duckdb/
outputs/
.env
.venv/
__pycache__/
*.pyc
.DS_Store
```

## References

- NYC TLC Trip Record Data portal: <https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>
- TLC Trip Record User Guide: <https://www.nyc.gov/assets/tlc/downloads/pdf/trip_record_user_guide.pdf>
- Yellow Taxi Data Dictionary: <https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf>
