from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from power_outage_mlops.config import MODEL_PATH
from power_outage_mlops.form_options import get_form_options
from power_outage_mlops.payload import coerce_payload
from power_outage_mlops.pipeline.prediction_pipeline import predict_outage_risk


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../../templates", static_folder="../../static")

    @app.get("/")
    def index():
        return render_template("index.html", options=get_form_options())

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "model_loaded": MODEL_PATH.exists()})

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True) or request.form.to_dict()
        typed_payload = coerce_payload(payload)
        result = predict_outage_risk(typed_payload)
        if request.is_json:
            return jsonify(result)
        return render_template("index.html", result=result, form=typed_payload, options=get_form_options())

    return app
