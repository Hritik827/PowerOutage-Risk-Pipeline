from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODEL_DIR = ROOT_DIR / "models"
LOG_DIR = ROOT_DIR / "logs"

RAW_SAMPLE_PATH = RAW_DATA_DIR / "power_outage_sample.csv"
ORIGINAL_DATASET_DIR = Path(
    os.getenv(
        "ORIGINAL_DATASET_DIR",
        r"C:\Users\Public\Hritik\project\Power_outrage\Part_1_phase\output\output\Dataset_original",
    )
)
ORIGINAL_TRAINING_DATA_PATH = PROCESSED_DATA_DIR / "original_power_outage_training.csv"
MERGED_DATASET_PATH = Path(
    os.getenv(
        "MERGED_DATASET_PATH",
        r"C:\Users\Public\Hritik\project\Power_outrage\Part_1_phase\output\output\merged_utility_storm_2024.csv",
    )
)
MERGED_TRAINING_DATA_PATH = PROCESSED_DATA_DIR / "merged_power_outage_training.csv"
TRAINING_SOURCE_PATH = Path(os.getenv("TRAINING_SOURCE_PATH", ORIGINAL_TRAINING_DATA_PATH))
TRAIN_DATA_PATH = PROCESSED_DATA_DIR / "train.csv"
MODEL_PATH = MODEL_DIR / "model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", f"file:{ROOT_DIR / 'mlruns'}")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "power-outage-risk")

TARGET_COLUMN = "outage_risk"
RANDOM_STATE = 42
