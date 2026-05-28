from __future__ import annotations

from pathlib import Path

import pandas as pd

from power_outage_mlops.config import RAW_SAMPLE_PATH, TRAINING_SOURCE_PATH
from power_outage_mlops.logger import get_logger


LOGGER = get_logger(__name__)

STATE_MAP = {
    "ALABAMA": "AL",
    "CALIFORNIA": "CA",
    "FLORIDA": "FL",
    "ILLINOIS": "IL",
    "NEW YORK": "NY",
    "TEXAS": "TX",
}


def parse_damage(value: object) -> float:
    if pd.isna(value) or str(value).strip() in {"", "."}:
        return 0.0
    raw = str(value).strip().upper()
    multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get(raw[-1], 1)
    number = raw[:-1] if raw[-1] in "KMB" else raw
    try:
        return float(number) * multiplier
    except ValueError:
        return 0.0


def load_training_source(path: Path = TRAINING_SOURCE_PATH) -> pd.DataFrame:
    if not path.exists() and path == TRAINING_SOURCE_PATH:
        path = RAW_SAMPLE_PATH
    if not path.exists():
        raise FileNotFoundError(f"Training source not found: {path}")
    LOGGER.info("Loading training source from %s", path)
    return pd.read_csv(path)


def normalize_outage_data(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    if "STATE" in normalized.columns and "state" not in normalized.columns:
        normalized["state"] = normalized["STATE"].str.upper().map(STATE_MAP).fillna(normalized["STATE"])

    for column in ["damage_property", "damage_crops"]:
        if column in normalized.columns:
            normalized[f"{column}_usd"] = normalized[column].apply(parse_damage)

    numeric_columns = [
        "storm_event_count",
        "total_property_damage_usd",
        "total_crop_damage_usd",
        "county_count",
        "saidi_minutes",
        "saifi_interruptions",
        "caidi_minutes",
        "population_served",
    ]
    for column in numeric_columns:
        if column in normalized.columns:
            normalized[column] = pd.to_numeric(normalized[column], errors="coerce").fillna(0)

    return normalized
