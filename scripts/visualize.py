import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import METRICS_DIR, PLOTS_DIR

def ensure_dirs():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

def load_results():
    file_path=METRICS_DIR/"benchmark_results.csv"
    return pd.read_csv(file_path)

def aggregate_results(df):
    summary=(
        df.groupby(["engine","scale_rows","query_name"], as_index=False).agg(
            avg_latency_ms=("latency_ms","mean"),
            avg_peak_python_mem_kb=("peak_python_mem_kb","mean"),
            avg_io_in_blocks=("io_in_blocks", "mean"),
            avg_io_out_blocks=("io_out_blocks", "mean"),
        )
    )
    return summary

def plot_latency_bar(summary):
    latest_scale=summary["scale_rows"].max()
    subset=summary[summary["scale_rows"]==latest_scale]

    plt.figure(figsize=(14,7))
    sns.barplot(data=subset, x="query_name", y="avg_latency_ms", hue="engine")
    plt.xticks(rotation=45, ha="right")
    plt.title(f"Average Query Latency by Engine ({latest_scale:,} rows)")
    plt.xlabel("Query")
    plt.ylabel("Average Latency (ms)")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR/"latency_bar.png")
    plt.close()

def plot_latency_vs_scale(summary):
    plt.figure(figsize=(14,7))
    sns.lineplot(
        data=summary,
        x="scale_rows",
        y="avg_latency_ms",
        hue="engine",
        style="query_name",
        markers=True,
        dashes=False,
    )
    plt.title("Latency vs Dataset Scale")
    plt.xlabel("Rows")
    plt.ylabel("Average Latency (ms)")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR/"latency_vs_scale.png")
    plt.close()

def plot_memory_vs_scale(summary):
    plt.figure(figsize=(14, 7))
    sns.lineplot(
        data=summary,
        x="scale_rows",
        y="avg_peak_python_mem_kb",
        hue="engine",
        style="query_name",
        markers=True,
        dashes=False,
    )
    plt.title("Python Memory Usage vs Dataset Scale")
    plt.xlabel("Rows")
    plt.ylabel("Average Peak Python Memory (KB)")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "memory_vs_scale.png")
    plt.close()

def plot_io_vs_scale(summary):
    io_summary = summary.copy()
    io_summary["avg_total_io_blocks"] = (
        io_summary["avg_io_in_blocks"] + io_summary["avg_io_out_blocks"]
    )

    plt.figure(figsize=(14, 7))
    sns.lineplot(
        data=io_summary,
        x="scale_rows",
        y="avg_total_io_blocks",
        hue="engine",
        style="query_name",
        markers=True,
        dashes=False,
    )
    plt.title("I/O Blocks vs Dataset Scale")
    plt.xlabel("Rows")
    plt.ylabel("Average Total I/O Blocks")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "io_vs_scale.png")
    plt.close()

def main():
    ensure_dirs()
    sns.set_theme(style="whitegrid")
    df=load_results()
    summary=aggregate_results(df)

    plot_latency_bar(summary)
    plot_latency_vs_scale(summary)
    plot_memory_vs_scale(summary)
    plot_io_vs_scale(summary)

    print("Plots saved to: ", PLOTS_DIR)

if __name__=="__main__":
    main()