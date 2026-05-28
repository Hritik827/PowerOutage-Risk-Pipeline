from __future__ import annotations

import pandas as pd

from power_outage_mlops.config import RAW_SAMPLE_PATH, TRAINING_SOURCE_PATH


FALLBACK_OPTIONS = {
    "states": ["TX", "FL", "CA", "NY", "IL", "AL"],
    "ownerships": ["Investor Owned", "Municipal", "Cooperative", "Federal"],
    "storm_types": ["Thunderstorm Wind", "Hurricane", "Winter Storm", "Tornado", "Flood", "Heat"],
}


def get_form_options() -> dict[str, list[str]]:
    data_path = TRAINING_SOURCE_PATH if TRAINING_SOURCE_PATH.exists() else RAW_SAMPLE_PATH
    if not data_path.exists():
        return FALLBACK_OPTIONS

    df = pd.read_csv(data_path, usecols=lambda column: column in {"state", "ownership", "primary_storm_type"})
    return {
        "states": _clean_options(df.get("state"), FALLBACK_OPTIONS["states"]),
        "ownerships": _clean_options(df.get("ownership"), FALLBACK_OPTIONS["ownerships"]),
        "storm_types": _clean_options(df.get("primary_storm_type"), FALLBACK_OPTIONS["storm_types"]),
    }


def _clean_options(series: pd.Series | None, fallback: list[str]) -> list[str]:
    if series is None:
        return fallback
    values = sorted({str(value).strip() for value in series.dropna() if str(value).strip()})
    return values or fallback
