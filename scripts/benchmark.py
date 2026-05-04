import csv
import json
import sqlite3
import duckdb
import time
import tracemalloc
import resource
from pathlib import Path
from config import(
    BENCHMARK_RUNS,
    DUCKDB_DB,
    SQLITE_DB,
    METRICS_DIR,
    PLANS_DIR,
    SCALE_SIZES,
)
from queries import QUERIES

def ensure_dirs():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    PLANS_DIR.mkdir(parents=True, exist_ok=True)

def format_query(sql, table_name):
    return sql.format(table=table_name)

def resource_snapshot():
    usage=resource.getrusage(resource.RUSAGE_SELF)
    return {
        "inblock":usage.ru_inblock,
        "oublock":usage.ru_oublock,
    }

def write_plan(engine, query_name, scale, plan_type, rows):
    file_path=PLANS_DIR/f"{engine}_{query_name}_{scale}_{plan_type}.txt"
    with open(file_path,"w", encoding="utf-8") as f:
        for row in rows:
            if isinstance(row,(list, tuple)):
                f.write(" | ".join(str(item) for item in row))
            else:
                f.write(str(row))
            f.write("\n")

def get_sqlite_explain(conn, sql):
    cursor=conn.execute(f"EXPLAIN QUERY PLAN {sql}")
    return cursor.fetchall()

def get_sqlite_explain_analyze(conn, sql):
    try:
        cursor=conn.execute(f"EXPLAIN ANALYZE {sql}")
        return cursor.fetchall()
    except sqlite3.OperationalError as exc:
        return [(f"EXPLAIN ANALYZE not available: {exc}",)]

def get_duckdb_explain(conn, sql):
    return conn.execute(f"EXPLAIN {sql}").fetchall()

def get_duckdb_explain_analyze(conn, sql):
    return conn.execute(f"EXPLAIN ANALYZE {sql}").fetchall()

def run_sqlite_query(conn, sql):
    cursor=conn.execute(sql)
    return cursor.fetchall()

def run_duckdb_query(conn, sql):
    return conn.execute(sql).fetchall()

def benchmark_query(engine, conn, query_name, sql, scale):
    results=[]
    if engine=="sqlite":
        run_sqlite_query(conn, sql)
    else:
        run_duckdb_query(conn, sql)

    before_plan=get_sqlite_explain(conn, sql) if engine=="sqlite" else get_duckdb_explain(conn, sql)
    before_analyze=get_sqlite_explain_analyze(conn, sql) if engine=="sqlite" else get_duckdb_explain_analyze(conn, sql)

    write_plan(engine, query_name, scale, "explain", before_plan)
    write_plan(engine, query_name, scale, "explain_analyze", before_analyze)

    for run_id in range(1, BENCHMARK_RUNS+1):
        tracemalloc.start()
        io_before=resource_snapshot()
        start=time.perf_counter()

        if engine=="sqlite":
            rows=run_sqlite_query(conn, sql)
        else:
            rows=run_duckdb_query(conn, sql)

        end= time.perf_counter()
        io_after=resource_snapshot()
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        results.append({
            "engine":engine,
            "scale_rows":scale,
            "query_name":query_name,
            "run_id":run_id,
            "latency_ms": round((end-start)*1000,3),
            "peak_python_mem_kb": round(peak_mem/1024,3),
            "io_in_blocks": io_after["inblock"]-io_before["inblock"],
            "io_out_blocks": io_after["oublock"]-io_before["oublock"],
            "result_row_count":len(rows),
        })

    return results

def save_csv(results):
    output_file=METRICS_DIR/"benchmark_results.csv"
    fieldnames=[
        "engine",
        "scale_rows",
        "query_name",
        "run_id",
        "latency_ms",
        "peak_python_mem_kb",
        "io_in_blocks",
        "io_out_blocks",
        "result_row_count",
    ]

    with open(output_file,"w", newline="", encoding="utf-8") as f:
        writer=csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader(),
        writer.writerows(results)

def save_json(results):
    output_file=METRICS_DIR/"benchmark_results.json"
    with open(output_file,"w",encoding="utf-8") as f:
        json.dump(results,f,indent=2)

def main():
    ensure_dirs()
    sqlite_conn=sqlite3.connect(SQLITE_DB)
    duckdb_conn=duckdb.connect(str(DUCKDB_DB))

    all_results=[]

    for scale in SCALE_SIZES:
        table_name=f"trips_{scale}"
        for query_name, query_template in QUERIES.items():
            sql=format_query(query_template, table_name)

            print(f"Running SQLite | {table_name} | {query_name}")
            sqlite_results=benchmark_query("sqlite", sqlite_conn, query_name, sql, scale)
            all_results.extend(sqlite_results)

            print(f"Running DuckDB | {table_name} | {query_name}")
            duckdb_results=benchmark_query("duckdb", duckdb_conn, query_name, sql, scale)
            all_results.extend(duckdb_results)

    sqlite_conn.close()
    duckdb_conn.close()

    save_csv(all_results)
    save_json(all_results)

    print("Benchmark complete.")
    print(f"CSV saved to: {METRICS_DIR/'benchmark_results.csv'}")
    print(f"JSON saved to: {METRICS_DIR/'benchmark_results.json'}")

if __name__=="__main__":
    main()