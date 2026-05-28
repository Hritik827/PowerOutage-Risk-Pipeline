from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from power_outage_mlops.components.data_ingestion import parse_damage
from power_outage_mlops.config import ORIGINAL_DATASET_DIR, ORIGINAL_TRAINING_DATA_PATH


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
    "HAWAII": "HI",
    "IDAHO": "ID",
    "ILLINOIS": "IL",
    "INDIANA": "IN",
    "IOWA": "IA",
    "KANSAS": "KS",
    "KENTUCKY": "KY",
    "LOUISIANA": "LA",
    "MAINE": "ME",
    "MARYLAND": "MD",
    "MASSACHUSETTS": "MA",
    "MICHIGAN": "MI",
    "MINNESOTA": "MN",
    "MISSISSIPPI": "MS",
    "MISSOURI": "MO",
    "MONTANA": "MT",
    "NEBRASKA": "NE",
    "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH",
    "NEW JERSEY": "NJ",
    "NEW MEXICO": "NM",
    "NEW YORK": "NY",
    "NORTH CAROLINA": "NC",
    "NORTH DAKOTA": "ND",
    "OHIO": "OH",
    "OKLAHOMA": "OK",
    "OREGON": "OR",
    "PENNSYLVANIA": "PA",
    "RHODE ISLAND": "RI",
    "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD",
    "TENNESSEE": "TN",
    "TEXAS": "TX",
    "UTAH": "UT",
    "VERMONT": "VT",
    "VIRGINIA": "VA",
    "WASHINGTON": "WA",
    "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI",
    "WYOMING": "WY",
    "DISTRICT OF COLUMBIA": "DC",
    "PUERTO RICO": "PR",
}


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace(".", pd.NA), errors="coerce")


def load_utility(data_folder: Path) -> pd.DataFrame:
    utility = pd.read_excel(
        data_folder / "Utility_Data_2024.xlsx",
        sheet_name="States",
        header=1,
        dtype={"Utility Number": str},
    )
    utility = utility[utility["Data Year"].notna()].copy()
    utility["Utility Number"] = utility["Utility Number"].astype(str).str.strip()
    utility["State"] = utility["State"].astype(str).str.strip()
    utility.rename(
        columns={
            "Utility Number": "utility_number",
            "Utility Name": "utility_name",
            "State": "state",
            "Ownership Type": "ownership",
        },
        inplace=True,
    )
    return utility[["utility_number", "utility_name", "state", "ownership"]]


def load_territory(data_folder: Path) -> pd.DataFrame:
    territory = pd.read_excel(
        data_folder / "Service_Territory_2024.xlsx",
        sheet_name="Counties_States",
        dtype={"Utility Number": str},
    )
    territory["Utility Number"] = territory["Utility Number"].astype(str).str.strip()
    territory["State"] = territory["State"].astype(str).str.strip()
    return (
        territory.groupby(["Utility Number", "State"])
        .agg(county_count=("County", "count"))
        .reset_index()
        .rename(columns={"Utility Number": "utility_number", "State": "state"})
    )


def load_reliability(data_folder: Path) -> pd.DataFrame:
    raw = pd.read_excel(data_folder / "Reliability_2024.xlsx", sheet_name="Reliability_States", header=None, dtype=str)
    reliability = raw.iloc[3:, [1, 3, 5, 6, 7, 14, 17, 18, 19, 23]].copy()
    reliability.columns = [
        "utility_number",
        "state",
        "ieee_saidi",
        "ieee_saifi",
        "ieee_caidi",
        "ieee_customers",
        "other_saidi",
        "other_saifi",
        "other_caidi",
        "other_customers",
    ]
    reliability["utility_number"] = reliability["utility_number"].astype(str).str.strip()
    reliability["state"] = reliability["state"].astype(str).str.strip()
    for column in reliability.columns.difference(["utility_number", "state"]):
        reliability[column] = _numeric(reliability[column])

    reliability["saidi_minutes"] = reliability["ieee_saidi"].fillna(reliability["other_saidi"])
    reliability["saifi_interruptions"] = reliability["ieee_saifi"].fillna(reliability["other_saifi"])
    reliability["caidi_minutes"] = reliability["ieee_caidi"].fillna(reliability["other_caidi"])
    reliability["population_served"] = reliability["ieee_customers"].fillna(reliability["other_customers"])
    return reliability[["utility_number", "state", "saidi_minutes", "saifi_interruptions", "caidi_minutes", "population_served"]]


def load_storms(data_folder: Path) -> pd.DataFrame:
    usecols = ["STATE", "EVENT_ID", "EVENT_TYPE", "DAMAGE_PROPERTY", "DAMAGE_CROPS"]
    storms = pd.read_csv(data_folder / "StormEvents_details-ftp_v1.0_d2024_c20260116.csv", usecols=usecols, dtype=str)
    storms["state"] = storms["STATE"].str.upper().map(STATE_MAP)
    storms["damage_property_usd"] = storms["DAMAGE_PROPERTY"].apply(parse_damage)
    storms["damage_crops_usd"] = storms["DAMAGE_CROPS"].apply(parse_damage)
    storms = storms.dropna(subset=["state"])
    return (
        storms.groupby("state")
        .agg(
            storm_event_count=("EVENT_ID", "count"),
            primary_storm_type=("EVENT_TYPE", lambda x: x.mode().iat[0] if not x.mode().empty else "Unknown"),
            total_property_damage_usd=("damage_property_usd", "sum"),
            total_crop_damage_usd=("damage_crops_usd", "sum"),
        )
        .reset_index()
    )


def prepare_original_dataset(data_folder: Path = ORIGINAL_DATASET_DIR, output_path: Path = ORIGINAL_TRAINING_DATA_PATH) -> pd.DataFrame:
    utility = load_utility(data_folder)
    territory = load_territory(data_folder)
    reliability = load_reliability(data_folder)
    storms = load_storms(data_folder)

    dataset = utility.merge(territory, on=["utility_number", "state"], how="left")
    dataset = dataset.merge(reliability, on=["utility_number", "state"], how="left")
    dataset = dataset.merge(storms, on="state", how="left")

    numeric_columns = [
        "county_count",
        "saidi_minutes",
        "saifi_interruptions",
        "caidi_minutes",
        "population_served",
        "storm_event_count",
        "total_property_damage_usd",
        "total_crop_damage_usd",
    ]
    for column in numeric_columns:
        dataset[column] = pd.to_numeric(dataset[column], errors="coerce").fillna(0)
    dataset["primary_storm_type"] = dataset["primary_storm_type"].fillna("Unknown")
    dataset["ownership"] = dataset["ownership"].fillna("Unknown")

    saidi_cutoff = dataset.loc[dataset["saidi_minutes"] > 0, "saidi_minutes"].median()
    storm_cutoff = dataset["storm_event_count"].quantile(0.75)
    damage_cutoff = dataset["total_property_damage_usd"].quantile(0.75)
    dataset["outage_risk"] = (
        (dataset["saidi_minutes"] >= saidi_cutoff)
        | (dataset["storm_event_count"] >= storm_cutoff)
        | (dataset["total_property_damage_usd"] >= damage_cutoff)
    ).astype(int)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_path, index=False)
    return dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Create model-ready training data from the original outage files.")
    parser.add_argument("--data-folder", type=Path, default=ORIGINAL_DATASET_DIR)
    parser.add_argument("--output", type=Path, default=ORIGINAL_TRAINING_DATA_PATH)
    args = parser.parse_args()
    dataset = prepare_original_dataset(args.data_folder, args.output)
    print(f"Saved {len(dataset):,} rows and {len(dataset.columns):,} columns to {args.output}")
    print(dataset["outage_risk"].value_counts().sort_index().to_dict())


if __name__ == "__main__":
    main()
