#!/usr/bin/env python3
"""
extract_startup_events.py

From the VAV + OAT dataset, this script:

1. Computes HVAC ON/OFF from VAV flow.
2. Detects OFF -> ON transitions.
3. For each transition:
   - Determines if it's a heating or cooling event (based on zone vs setpoints).
   - Records:
       * start time
       * mode ("heating" or "cooling")
       * outside air temperature at start
       * initial zone ΔT (degF from relevant setpoint)
       * recovery time in minutes until zone reaches that setpoint
4. Saves an events CSV and generates plots.
"""

import os
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


DATA_FILE = "vav_oat_brick_clean.csv"
FIG_DIR = Path("figures_startup")

# Column names (from the cleaned Brick-ish dataset)
FLOW_COL = "brick:Discharge_Air_Flow_Sensor_cfm"
ZONE_TEMP_COL = "brick:Zone_Air_Temperature_Sensor_degF"
COOL_SPT_COL = "brick:Zone_Air_Temperature_Cooling_Setpoint_degF"
HEAT_SPT_COL = "brick:Zone_Air_Temperature_Heating_Setpoint_degF"
OAT_COL = "brick:Outside_Air_Temperature_Sensor_degF"

# Flow threshold for HVAC "ON"
FLOW_THRESHOLD_CFM = 50.0


def load_data(path: str = DATA_FILE) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").set_index("timestamp")
    return df


def ensure_fig_dir():
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def compute_hvac_on_flag(df: pd.DataFrame) -> pd.Series:
    """
    Returns a boolean Series where True means HVAC is ON
    based on VAV flow > FLOW_THRESHOLD_CFM.
    """
    if FLOW_COL not in df.columns:
        raise KeyError(f"Flow column '{FLOW_COL}' not found in dataframe.")
    hvac_on = df[FLOW_COL] > FLOW_THRESHOLD_CFM
    return hvac_on


def extract_startup_events(df: pd.DataFrame, hvac_on: pd.Series) -> pd.DataFrame:
    """
    Find OFF -> ON transitions and calculate:
    - mode_heating (1/0, cooling baseline)
    - oat_start_degF
    - deltaT_start_degF
    - recovery_minutes (float)

    Add ML-friendly calendar features:
    - dow_1..dow_6  (Mon baseline dummy encoding)
    """

    events: List[Dict] = []

    # Identify OFF -> ON edges
    prev_on = hvac_on.shift(1, fill_value=False)
    on_edges = hvac_on & ~prev_on
    on_times = df.index[on_edges]

    for t_on in on_times:
        try:
            zt = df.at[t_on, ZONE_TEMP_COL]
            cool_sp = df.at[t_on, COOL_SPT_COL]
            heat_sp = df.at[t_on, HEAT_SPT_COL]
            oat = df.at[t_on, OAT_COL]
        except KeyError:
            continue

        if np.isnan(zt) or np.isnan(cool_sp) or np.isnan(heat_sp) or np.isnan(oat):
            continue

        # Determine mode + ΔT
        if zt > cool_sp:
            mode_heating = 0
            deltaT = abs(zt - cool_sp)
        elif zt < heat_sp:
            mode_heating = 1
            deltaT = abs(zt - heat_sp)
        else:
            continue

        start_loc = df.index.get_loc(t_on)
        sub_df = df.iloc[start_loc:]
        sub_on = hvac_on.iloc[start_loc:]

        if mode_heating == 0:   # cooling
            cond = sub_df[ZONE_TEMP_COL] <= sub_df[COOL_SPT_COL]
        else:                   # heating
            cond = sub_df[ZONE_TEMP_COL] >= sub_df[HEAT_SPT_COL]

        cond_true_idx = cond[cond].index
        if len(cond_true_idx) == 0:
            continue

        t_reach = cond_true_idx[0]

        if not sub_on.loc[t_on:t_reach].all():
            continue

        delta_minutes = (t_reach - t_on).total_seconds() / 60.0
        if delta_minutes <= 0:
            continue

        events.append(
            {
                "start_time": t_on,
                "mode_heating": int(mode_heating),
                "oat_start_degF": float(oat),
                "deltaT_start_degF": float(deltaT),
                "recovery_minutes": float(delta_minutes),
            }
        )

    events_df = pd.DataFrame(events)

    if not events_df.empty:
        events_df = events_df.sort_values("start_time").reset_index(drop=True)
        events_df["start_time"] = pd.to_datetime(events_df["start_time"])

        # weekday integer (0=Mon..6=Sun)
        dow = events_df["start_time"].dt.weekday

        # Build dummy columns
        dow_dummies = pd.get_dummies(dow, prefix="dow", drop_first=True)

        # Ensure ALL expected dummy columns exist (Mon baseline removed)
        expected_cols = [f"dow_{i}" for i in range(1, 7)]  # 1..6
        dow_dummies = dow_dummies.reindex(columns=expected_cols, fill_value=0)

        # Attach to dataframe
        events_df = pd.concat([events_df, dow_dummies], axis=1)


    return events_df




def plot_hvac_on_off(df: pd.DataFrame, hvac_on: pd.Series):
    """
    Simple binary plot: HVAC ON (1) vs OFF (0) over time.
    """
    ensure_fig_dir()
    hvac_flag = hvac_on.astype(int)

    plt.figure(figsize=(10, 3))
    plt.step(df.index, hvac_flag, where="post")
    plt.ylim(-0.2, 1.2)
    plt.yticks([0, 1], ["OFF", "ON"])
    plt.xlabel("Time")
    plt.title("HVAC ON/OFF (Flow-based)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "hvac_on_off_flag.png")
    plt.close()


def plot_startup_scatter(events_df: pd.DataFrame):
    """
    Scatter plot: initial deltaT vs recovery time.

    If `mode_heating` exists:
      - plot cooling (mode_heating == 0) and heating (mode_heating == 1) separately
    Otherwise:
      - plot all events together.
    """
    if events_df.empty:
        print("No startup events to plot.")
        return

    ensure_fig_dir()

    # Base scatter: all modes combined
    plt.figure()
    plt.scatter(
        events_df["deltaT_start_degF"],
        events_df["recovery_minutes"],
    )
    plt.xlabel("Initial |ΔT| from Setpoint (degF)")
    plt.ylabel("Recovery Time (minutes)")
    plt.title("Startup Events: ΔT vs Recovery Time (all modes)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "startup_scatter_all_modes.png")
    plt.close()

    # If mode_heating column is present, also plot separated by mode
    if "mode_heating" in events_df.columns:
        # Cooling = 0, Heating = 1
        cooling_df = events_df[events_df["mode_heating"] == 0]
        heating_df = events_df[events_df["mode_heating"] == 1]

        # Combined overlay plot
        plt.figure()
        if not cooling_df.empty:
            plt.scatter(
                cooling_df["deltaT_start_degF"],
                cooling_df["recovery_minutes"],
                label="cooling",
            )
        if not heating_df.empty:
            plt.scatter(
                heating_df["deltaT_start_degF"],
                heating_df["recovery_minutes"],
                label="heating",
            )
        plt.xlabel("Initial |ΔT| from Setpoint (degF)")
        plt.ylabel("Recovery Time (minutes)")
        plt.title("Startup Events: ΔT vs Recovery Time (by mode)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(FIG_DIR / "startup_scatter_by_mode.png")
        plt.close()



def main():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Cannot find {DATA_FILE} in current directory.")

    df = load_data(DATA_FILE)

    # Compute HVAC ON/OFF flag
    hvac_on = compute_hvac_on_flag(df)
    df["HVAC_On_Flag"] = hvac_on.astype(int)

    # Extract startup events with recovery times
    events_df = extract_startup_events(df, hvac_on)

    # Save outputs
    ensure_fig_dir()
    df[["HVAC_On_Flag"]].to_csv(FIG_DIR / "hvac_on_off_timeseries.csv")
    events_path = FIG_DIR / "hvac_startup_events.csv"
    events_df.to_csv(events_path, index=False)

    print(f"Saved HVAC ON/OFF flag timeseries to: {FIG_DIR / 'hvac_on_off_timeseries.csv'}")
    print(f"Saved startup events to: {events_path}")

    # Plots
    plot_hvac_on_off(df, hvac_on)
    plot_startup_scatter(events_df)

    print("\nStartup event extraction complete.")
    print("Figures and CSVs saved under:", FIG_DIR.resolve())


if __name__ == "__main__":
    main()
