import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


DATA_FILE = "vav_oat_brick_clean.csv"
FIG_DIR = Path("figures")


def load_data(path: str = DATA_FILE) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Parse timestamp and set as index
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").set_index("timestamp")
    return df


def ensure_fig_dir():
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def basic_overview(df: pd.DataFrame):
    print("=== BASIC OVERVIEW ===")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"Time range: {df.index.min()} -> {df.index.max()}")

    # Try to infer sampling frequency
    freq = pd.infer_freq(df.index)
    print(f"Inferred frequency: {freq}")

    # Missing data
    missing = df.isna().mean().sort_values(ascending=False)
    print("\n=== MISSING FRACTION PER COLUMN ===")
    print((missing * 100).round(2).astype(str) + " %")


def check_time_gaps(df: pd.DataFrame):
    print("\n=== TIME GAP CHECK ===")
    # Use the most common difference as "expected" step
    diffs = df.index.to_series().diff().dropna()
    if diffs.empty:
        print("Not enough data to check gaps.")
        return

    most_common_delta = diffs.mode().iloc[0]
    print(f"Most common step: {most_common_delta}")

    full_index = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq=most_common_delta,
    )

    missing_timestamps = full_index.difference(df.index)
    print(f"Expected points: {len(full_index)}")
    print(f"Actual points:   {len(df.index)}")
    print(f"Missing points:  {len(missing_timestamps)}")

    if len(missing_timestamps) > 0:
        print("Example missing timestamps (up to 10):")
        print(missing_timestamps[:10])


def zscore_outliers(df: pd.DataFrame, z_thresh: float = 4.0):
    print("\n=== OUTLIER CHECK (|z| > {:.1f}) ===".format(z_thresh))

    numeric = df.select_dtypes(include=[np.number])
    means = numeric.mean()
    stds = numeric.std(ddof=0).replace(0, np.nan)

    z = (numeric - means) / stds
    outlier_mask = z.abs() > z_thresh

    # Count outliers per column
    outlier_counts = outlier_mask.sum().sort_values(ascending=False)

    print("Outliers per numeric column:")
    print(outlier_counts[outlier_counts > 0])

    return outlier_mask


def plot_timeseries(df: pd.DataFrame):
    """
    Drastically trimmed:

    1) Temps: OA vs Zone temperature
    2) VAV flow: sensor + setpoint (if both exist)
    """
    print("Generating trimmed time-series plots...")

    ensure_fig_dir()

    # ---- 1) OA vs Zone Temperature ----
    temp_cols = [
        "brick:Outside_Air_Temperature_Sensor_degF",
        "brick:Zone_Air_Temperature_Sensor_degF",
    ]
    temp_existing = [c for c in temp_cols if c in df.columns]

    if temp_existing:
        plt.figure()
        for c in temp_existing:
            plt.plot(df.index, df[c], label=c)
        plt.xlabel("Time")
        plt.ylabel("Temperature (degF)")
        plt.title("OA vs Zone Temperature")
        plt.legend()
        plt.tight_layout()
        plt.savefig(FIG_DIR / "timeseries_temps_oa_zone.png")
        plt.close()
    else:
        print("No OA/Zone temp columns found for temp time-series plot.")

    # ---- 2) VAV Flow (sensor + setpoint) ----
    flow_cols = [
        "brick:Discharge_Air_Flow_Sensor_cfm",
        "brick:Discharge_Air_Flow_Setpoint_cfm",
    ]
    flow_existing = [c for c in flow_cols if c in df.columns]

    if flow_existing:
        plt.figure()
        for c in flow_existing:
            plt.plot(df.index, df[c], label=c)
        plt.xlabel("Time")
        plt.ylabel("Flow (cfm)")
        plt.title("VAV Air Flow (Sensor / Setpoint)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(FIG_DIR / "timeseries_vav_flow.png")
        plt.close()
    else:
        print("No VAV flow columns found for flow time-series plot.")


def plot_histograms(df: pd.DataFrame):
    print("Generating histograms...")

    ensure_fig_dir()

    numeric = df.select_dtypes(include=[np.number])
    for col in numeric.columns:
        plt.figure()
        plt.hist(numeric[col].dropna(), bins=50)
        plt.xlabel(col)
        plt.ylabel("Count")
        plt.title(f"Histogram of {col}")
        plt.tight_layout()
        plt.savefig(FIG_DIR / f"hist_{col.replace(':', '_').replace('/', '_')}.png")
        plt.close()


def plot_correlation(df: pd.DataFrame):
    print("Generating correlation heatmap...")

    ensure_fig_dir()

    numeric = df.select_dtypes(include=[np.number]).drop(
        columns=["t_minutes", "Excel Time"], errors="ignore"
    )

    corr = numeric.corr()

    plt.figure(figsize=(8, 6))
    im = plt.imshow(corr, aspect="auto")
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "correlation_matrix.png")
    plt.close()


def plot_daily_patterns(df: pd.DataFrame):
    print("Generating simple daily/seasonal patterns...")

    ensure_fig_dir()

    # Focus on OA and zone temperature
    cols = [
        "brick:Outside_Air_Temperature_Sensor_degF",
        "brick:Zone_Air_Temperature_Sensor_degF",
    ]
    cols = [c for c in cols if c in df.columns]
    if not cols:
        print("No OA/Zone temp columns found for daily patterns.")
        return

    # Daily average
    daily = df[cols].resample("D").mean()

    plt.figure()
    for c in cols:
        plt.plot(daily.index, daily[c], label=c)
    plt.xlabel("Day")
    plt.ylabel("Daily Mean (degF)")
    plt.title("Daily Mean OA & Zone Temperatures")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "daily_means_oa_zone.png")
    plt.close()

    # Hour-of-day pattern
    df["hour"] = df.index.hour
    hourly = df.groupby("hour")[cols].mean()

    plt.figure()
    for c in cols:
        plt.plot(hourly.index, hourly[c], marker="o", label=c)
    plt.xlabel("Hour of Day")
    plt.ylabel("Mean (degF)")
    plt.title("Hour-of-Day Profiles (All Days Combined)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "hourly_profiles_oa_zone.png")
    plt.close()

    # Clean up helper column
    df.drop(columns=["hour"], inplace=True)


def hvac_on_off_stats(
    df: pd.DataFrame,
    flow_col: str = "brick:Discharge_Air_Flow_Sensor_cfm",
    threshold_cfm: float = 100.0,
):
    """
    Estimate % of time HVAC is ON vs OFF based on VAV flow.

    - HVAC ON when flow > threshold_cfm
    - HVAC OFF when flow <= threshold_cfm

    Uses fraction of rows as approximation for fraction of time
    (sampling is nearly regular).
    """
    print("\n=== HVAC ON/OFF (Flow-Based) ===")

    if flow_col not in df.columns:
        print(f"Flow column '{flow_col}' not found. Cannot compute HVAC ON/OFF.")
        return

    series = df[flow_col].dropna()

    if series.empty:
        print("No data in flow column after dropping NaNs.")
        return

    hvac_on = series > threshold_cfm
    hvac_off = ~hvac_on

    total = len(series)
    on_pct = hvac_on.sum() / total * 100.0
    off_pct = hvac_off.sum() / total * 100.0

    print(f"Using flow column: {flow_col}")
    print(f"Threshold: {threshold_cfm} cfm")
    print(f"Total points considered: {total}")
    print(f"HVAC ON:  {on_pct:.2f} %")
    print(f"HVAC OFF: {off_pct:.2f} %")

    # Optional: daily breakdown of % ON
    daily_on = hvac_on.groupby(df.loc[series.index].index.date).mean() * 100.0
    print("\nDaily % HVAC ON (based on flow > threshold):")
    print(daily_on.round(2))


def main():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Cannot find {DATA_FILE} in current directory.")

    df = load_data(DATA_FILE)

    basic_overview(df)
    check_time_gaps(df)
    outlier_mask = zscore_outliers(df)
    print("outlier_mask ",outlier_mask)

    # NEW: HVAC on/off stats based on VAV flow
    hvac_on_off_stats(df)

    plot_timeseries(df)
    #plot_histograms(df)
    #plot_correlation(df)
    #plot_daily_patterns(df)

    print("\nDone. Figures saved in:", FIG_DIR.resolve())


if __name__ == "__main__":
    main()
