from power_outage_mlops.pipeline.training_pipeline import run_training_pipeline


if __name__ == "__main__":
    metrics = run_training_pipeline()
    print(metrics)
