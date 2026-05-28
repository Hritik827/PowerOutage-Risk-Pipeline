from __future__ import annotations

import pandas as pd

from power_outage_mlops.config import MODEL_PATH
from power_outage_mlops.utils import load_object


def predict_outage_risk(payload: dict) -> dict:
    model = load_object(MODEL_PATH)
    frame = pd.DataFrame([payload])
    prediction = int(model.predict(frame)[0])
    probability = float(model.predict_proba(frame)[0][prediction])
    label = "High outage risk" if prediction == 1 else "Lower outage risk"
    return {
        "prediction": prediction,
        "label": label,
        "confidence": round(probability, 4),
    }
