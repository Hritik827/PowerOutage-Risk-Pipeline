from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from power_outage_mlops.config import MERGED_DATASET_PATH, MERGED_TRAINING_DATA_PATH


USE_COLUMNS = [
    "Utility Number",
    "Utility Name",
    "State",
    "Ownership",
    "County_Count",
    "IEEE_AllEvents_SAIDI_min_per_yr",
    "IEEE_AllEvents_SAIFI_times_per_yr",
    "IEEE_AllEvents_CAIDI_min_per_interruption",
    "Other_AllEvents_SAIDI_min_per_yr",
    "Other_AllEvents_SAIFI_times_per_yr",
    "Other_AllEvents_CAIDI_min_per_interruption",
    "EVENT_ID",
    "EVENT_TYPE",
    "DAMAGE_PROPERTY_USD",
    "DAMAGE_CROPS_USD",
]


def _number(value: object) -> float:
    if pd.isna(value) or str(value).strip() in {"", "."}:
        return 0.0
    parsed = pd.to_numeric(value, errors="coerce")
    return 0.0 if pd.isna(parsed) else float(parsed)


def _first_non_empty(current: object, candidate: object) -> object:
    if current not in (None, "", ".") and not pd.isna(current):
        return current
    if pd.isna(candidate):
        return current
    return candidate


def prepare_from_merged_dataset(
    merged_path: Path = MERGED_DATASET_PATH,
    output_path: Path = MERGED_TRAINING_DATA_PATH,
    chunksize: int = 100_000,
) -> pd.DataFrame:
    records: dict[tuple[str, str], dict] = {}
    event_ids: dict[tuple[str, str], set[str]] = defaultdict(set)
    storm_types: dict[tuple[str, str], Counter] = defaultdict(Counter)

    for chunk in pd.read_csv(merged_path, usecols=USE_COLUMNS, dtype=str, chunksize=chunksize, low_memory=False):
        for column in [
            "County_Count",
            "IEEE_AllEvents_SAIDI_min_per_yr",
            "IEEE_AllEvents_SAIFI_times_per_yr",
            "IEEE_AllEvents_CAIDI_min_per_interruption",
            "Other_AllEvents_SAIDI_min_per_yr",
            "Other_AllEvents_SAIFI_times_per_yr",
            "Other_AllEvents_CAIDI_min_per_interruption",
            "DAMAGE_PROPERTY_USD",
            "DAMAGE_CROPS_USD",
        ]:
            chunk[column] = pd.to_numeric(chunk[column].replace(".", pd.NA), errors="coerce")

        for row in chunk.itertuples(index=False):
            key = (str(row[0]).strip(), str(row[2]).strip())
            if key not in records:
                records[key] = {
                    "utility_number": key[0],
                    "utility_name": row[1],
                    "state": key[1],
                    "ownership": row[3],
                    "county_count": 0.0,
                    "saidi_minutes": 0.0,
                    "saifi_interruptions": 0.0,
                    "caidi_minutes": 0.0,
                    "population_served": 0.0,
                    "total_property_damage_usd": 0.0,
                    "total_crop_damage_usd": 0.0,
                }

            record = records[key]
            record["utility_name"] = _first_non_empty(record["utility_name"], row[1])
            record["ownership"] = _first_non_empty(record["ownership"], row[3])
            record["county_count"] = max(record["county_count"], _number(row[4]))
            record["saidi_minutes"] = max(record["saidi_minutes"], _number(row[5]) or _number(row[8]))
            record["saifi_interruptions"] = max(record["saifi_interruptions"], _number(row[6]) or _number(row[9]))
            record["caidi_minutes"] = max(record["caidi_minutes"], _number(row[7]) or _number(row[10]))

            event_id = "" if pd.isna(row[11]) else str(row[11]).strip()
            if event_id and event_id not in event_ids[key]:
                event_ids[key].add(event_id)
                record["total_property_damage_usd"] += _number(row[13])
                record["total_crop_damage_usd"] += _number(row[14])

            event_type = "" if pd.isna(row[12]) else str(row[12]).strip()
            if event_type:
                storm_types[key][event_type] += 1

    dataset = pd.DataFrame(records.values())
    dataset["storm_event_count"] = dataset.apply(
        lambda row: len(event_ids[(str(row["utility_number"]), str(row["state"]))]),
        axis=1,
    )
    dataset["primary_storm_type"] = dataset.apply(
        lambda row: storm_types[(str(row["utility_number"]), str(row["state"]))].most_common(1)[0][0]
        if storm_types[(str(row["utility_number"]), str(row["state"]))]
        else "Unknown",
        axis=1,
    )

    saidi_cutoff = dataset.loc[dataset["saidi_minutes"] > 0, "saidi_minutes"].median()
    storm_cutoff = dataset["storm_event_count"].quantile(0.75)
    damage_cutoff = dataset["total_property_damage_usd"].quantile(0.75)
    dataset["outage_risk"] = (
        (dataset["saidi_minutes"] >= saidi_cutoff)
        | (dataset["storm_event_count"] >= storm_cutoff)
        | (dataset["total_property_damage_usd"] >= damage_cutoff)
    ).astype(int)

    ordered_columns = [
        "utility_number",
        "utility_name",
        "state",
        "ownership",
        "county_count",
        "saidi_minutes",
        "saifi_interruptions",
        "caidi_minutes",
        "population_served",
        "storm_event_count",
        "primary_storm_type",
        "total_property_damage_usd",
        "total_crop_damage_usd",
        "outage_risk",
    ]
    dataset = dataset[ordered_columns].sort_values(["state", "utility_name"]).reset_index(drop=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_path, index=False)
    return dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Create model-ready training data from merged_utility_storm_2024.csv.")
    parser.add_argument("--input", type=Path, default=MERGED_DATASET_PATH)
    parser.add_argument("--output", type=Path, default=MERGED_TRAINING_DATA_PATH)
    parser.add_argument("--chunksize", type=int, default=100_000)
    args = parser.parse_args()

    dataset = prepare_from_merged_dataset(args.input, args.output, args.chunksize)
    print(f"Saved {len(dataset):,} rows and {len(dataset.columns):,} columns to {args.output}")
    print(dataset["outage_risk"].value_counts().sort_index().to_dict())


if __name__ == "__main__":
    main()
