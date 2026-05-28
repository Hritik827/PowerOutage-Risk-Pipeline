from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from power_outage_mlops.components.data_ingestion import parse_damage


STATE_MAP = {
    "ALABAMA": "AL",
    "ALASKA": "AK",
    "ARIZONA": "AZ",
    "ARKANSAS": "AR",
    "CALIFORNIA": "CA",
    "COLORADO": "CO",
    "CONNECTICUT": "CT",
    "DELAWARE": "DE",
    "FLORIDA": "FL",
    "GEORGIA": "GA",
    "ILLINOIS": "IL",
    "NEW YORK": "NY",
    "TEXAS": "TX",
}


def merge_power_outage_sources(data_folder: Path, output_path: Path) -> pd.DataFrame:
    utility_file = data_folder / "Utility_Data_2024.xlsx"
    territory_file = data_folder / "Service_Territory_2024.xlsx"
    reliability_file = data_folder / "Reliability_2024.xlsx"
    storm_file = data_folder / "StormEvents_details-ftp_v1.0_d2024_c20260116.csv"

    utility = pd.read_excel(utility_file, sheet_name="States", header=1, dtype={"Utility Number": str})
    utility = utility[utility["Data Year"].notna()].copy()
    utility["Utility Number"] = utility["Utility Number"].astype(str).str.strip()
    utility["State"] = utility["State"].astype(str).str.strip()
    utility.rename(columns={"Ownership Type": "Ownership"}, inplace=True)

    territory = pd.read_excel(territory_file, sheet_name="Counties_States", dtype={"Utility Number": str})
    territory["Utility Number"] = territory["Utility Number"].astype(str).str.strip()
    territory["State"] = territory["State"].astype(str).str.strip()
    county_agg = (
        territory.groupby(["Utility Number", "State"])
        .agg(
            county_count=("County", "count"),
            counties_served=("County", lambda x: "; ".join(sorted(x.dropna().astype(str)))),
        )
        .reset_index()
    )

    reliability_raw = pd.read_excel(reliability_file, sheet_name="Reliability_States", header=None, dtype=str)
    reliability = reliability_raw.iloc[3:, :8].copy()
    reliability.columns = [
        "Data Year",
        "Utility Number",
        "Utility Name",
        "State",
        "Ownership",
        "saidi_minutes",
        "saifi_interruptions",
        "caidi_minutes",
    ]
    reliability["Utility Number"] = reliability["Utility Number"].astype(str).str.strip()
    reliability["State"] = reliability["State"].astype(str).str.strip()
    for column in ["saidi_minutes", "saifi_interruptions", "caidi_minutes"]:
        reliability[column] = pd.to_numeric(reliability[column], errors="coerce")

    storms = pd.read_csv(storm_file, dtype=str, low_memory=False)
    storms["State"] = storms["STATE"].str.upper().map(STATE_MAP)
    storms["damage_property_usd"] = storms["DAMAGE_PROPERTY"].apply(parse_damage)
    storms["damage_crops_usd"] = storms["DAMAGE_CROPS"].apply(parse_damage)
    storm_agg = (
        storms.dropna(subset=["State"])
        .groupby("State")
        .agg(
            storm_event_count=("EVENT_ID", "count"),
            primary_storm_type=("EVENT_TYPE", lambda x: x.mode().iat[0] if not x.mode().empty else "Unknown"),
            total_property_damage_usd=("damage_property_usd", "sum"),
            total_crop_damage_usd=("damage_crops_usd", "sum"),
        )
        .reset_index()
    )

    merged = utility.merge(county_agg, on=["Utility Number", "State"], how="left")
    merged = merged.merge(
        reliability.drop(columns=["Data Year", "Utility Name", "Ownership"], errors="ignore"),
        on=["Utility Number", "State"],
        how="left",
    )
    merged = merged.merge(storm_agg, on="State", how="left")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge utility, territory, reliability, and storm files.")
    parser.add_argument("--data-folder", required=True, type=Path)
    parser.add_argument("--output", default=Path("data/processed/merged_power_outage_2024.csv"), type=Path)
    args = parser.parse_args()
    merged = merge_power_outage_sources(args.data_folder, args.output)
    print(f"Saved {len(merged):,} rows to {args.output}")


if __name__ == "__main__":
    main()
