from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from power_outage_mlops.config import TARGET_COLUMN


@dataclass(frozen=True)
class FeatureSchema:
    numeric_features: list[str]
    categorical_features: list[str]


DEFAULT_SCHEMA = FeatureSchema(
    numeric_features=[
        "storm_event_count",
        "total_property_damage_usd",
        "total_crop_damage_usd",
        "county_count",
        "saidi_minutes",
        "saifi_interruptions",
        "caidi_minutes",
        "population_served",
    ],
    categorical_features=["state", "ownership", "primary_storm_type"],
)


def build_preprocessor(schema: FeatureSchema = DEFAULT_SCHEMA) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, schema.numeric_features),
            ("cat", categorical_pipeline, schema.categorical_features),
        ]
    )


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    missing = [col for col in DEFAULT_SCHEMA.numeric_features + DEFAULT_SCHEMA.categorical_features + [TARGET_COLUMN] if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df[DEFAULT_SCHEMA.numeric_features + DEFAULT_SCHEMA.categorical_features], df[TARGET_COLUMN]
