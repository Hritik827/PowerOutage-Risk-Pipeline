from __future__ import annotations

from power_outage_mlops.components.data_ingestion import load_training_source, normalize_outage_data
from power_outage_mlops.components.data_transformation import split_features_target
from power_outage_mlops.components.model_trainer import train_model
from power_outage_mlops.config import METRICS_PATH, TRAIN_DATA_PATH
from power_outage_mlops.logger import get_logger
from power_outage_mlops.utils import save_json


LOGGER = get_logger(__name__)


def run_training_pipeline() -> dict[str, float]:
    raw_df = load_training_source()
    train_df = normalize_outage_data(raw_df)
    TRAIN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(TRAIN_DATA_PATH, index=False)

    features, target = split_features_target(train_df)
    _, metrics = train_model(features, target)
    save_json(METRICS_PATH, metrics)
    LOGGER.info("Training complete. Metrics: %s", metrics)
    return metrics
