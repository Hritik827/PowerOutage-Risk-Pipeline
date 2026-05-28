# Azure Docker Deployment Flow

This project follows the complete deployment flow:

```text
Flask application
  -> Docker image
  -> Azure Container Registry
  -> Azure Web App for Containers
  -> GitHub Deployment Center / GitHub Actions
  -> Continuous deployment
  -> Live Azure web application
```

## Local training

```bash
pip install -r requirements.txt
pip install -e .
python main.py
```

MLflow writes experiment runs to `mlruns/` by default.

## DVC workflow

```bash
dvc init
dvc add data/raw/power_outage_sample.csv
dvc repro
dvc metrics show
```

Use a real remote for team projects:

```bash
dvc remote add -d azure_remote azure://<container-name>/<path>
dvc push
```

## Docker commands

```bash
docker build -t testdockerhri.azurecr.io/mltest:latest .
docker login testdockerhri.azurecr.io
docker push testdockerhri.azurecr.io/mltest:latest
```

## Azure setup

Create an Azure Container Registry:

| Setting | Value |
| --- | --- |
| Registry name | `testdockerhri` |
| Region | `Central US` |
| Admin user | Enabled |

Create an Azure Web App:

| Setting | Value |
| --- | --- |
| Name | `testdockerhri` |
| Publish | Container |
| Image source | Azure Container Registry |
| Image | `mltest:latest` |

## GitHub secrets

Add these repository secrets:

```text
AZURE_CREDENTIALS
ACR_USERNAME
ACR_PASSWORD
```

After that, each push to `main` builds the Docker image, pushes it to ACR, and deploys it to Azure Web App.
