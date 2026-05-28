from __future__ import annotations


NUMERIC_FIELDS = {
    "storm_event_count",
    "total_property_damage_usd",
    "total_crop_damage_usd",
    "county_count",
    "saidi_minutes",
    "saifi_interruptions",
    "caidi_minutes",
    "population_served",
}


def coerce_payload(payload: dict) -> dict:
    coerced = {}
    for key, value in payload.items():
        if key in NUMERIC_FIELDS:
            coerced[key] = float(value)
        else:
            coerced[key] = value
    return coerced
