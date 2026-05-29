# Power Outage Risk MLOps on Azure

End-to-end MLOps project for predicting electric power outage risk with a Dockerized Flask application, DVC data versioning, MLflow experiment tracking, Azure Container Registry, Azure Web App for Containers, and GitHub continuous deployment.

## Complete Project Flow

```text
Write Flask Application
        ->
Create Docker Image
        ->
Push Docker Image to Azure Container Registry (ACR)
        ->
Create Azure Web App
        ->
Connect Web App with Container Registry
        ->
Integrate GitHub Deployment Center / GitHub Actions
        ->
Continuous Deployment Enabled
        ->
Application Automatically Deploys
        ->
Live Azure Web Application
```

## Main Concept

This project deploys a machine learning Flask app to Azure using:

- Azure Container Registry for private Docker image storage
- Azure Web App for Containers for hosting
- GitHub Actions for CI/CD
- DVC for dataset and pipeline versioning
- MLflow for experiment tracking and model metrics

## What You Built

- Dockerized Flask application
- Modular ML pipeline for ingestion, transformation, training, and prediction
- Private container image workflow for ACR
- Azure Web App for Containers deployment path
- Continuous deployment pipeline from GitHub
- DVC pipeline definition with reproducible training
- MLflow tracking for parameters, metrics, and model artifact

## Project Structure

```text
.
|-- .github/workflows/azure-webapp-container.yml
|-- data/
|   |-- raw/power_outage_sample.csv
|   `-- processed/original_power_outage_training.csv
|-- models/
|-- src/power_outage_mlops/
|   |-- app.py
|   |-- components/
|   |   |-- data_ingestion.py
|   |   |-- data_transformation.py
|   |   `-- model_trainer.py
|   |-- pipeline/
|   |   |-- prediction_pipeline.py
|   |   `-- training_pipeline.py
|   |-- config.py
|   |-- logger.py
|   `-- utils.py
|-- static/css/styles.css
|-- templates/index.html
|-- tests/test_prediction_payload.py
|-- app.py
|-- main.py
|-- scripts/merge_power_outage_datasets.py
|-- scripts/prepare_original_dataset.py
|-- scripts/prepare_from_merged_dataset.py
|-- Dockerfile
|-- dvc.yaml
|-- requirements.txt
|-- setup.py
`-- DEPLOYMENT.md
```

## Technologies Used

| Category | Tools |
| --- | --- |
| Programming | Python |
| Framework | Flask |
| Machine Learning | scikit-learn |
| Experiment Tracking | MLflow |
| Data Versioning | DVC |
| Containerization | Docker |
| Cloud Platform | Microsoft Azure |
| Container Storage | Azure Container Registry |
| Hosting | Azure Web App for Containers |
| Version Control | GitHub |
| CI/CD | GitHub Actions / Deployment Center |
| Command Line | Terminal / Bash / PowerShell |

## Run Locally

```bash
pip install -r requirements.txt
pip install -e .
python main.py
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Health check:

```text
http://127.0.0.1:5000/health
```

## VS Code CMD End-to-End Steps

Use this section when running the project from the VS Code **CMD** terminal.

### 1. Open project in VS Code

Open this folder:

```text
C:\DA_Project
```

Open terminal:

```text
Terminal -> New Terminal -> Command Prompt
```

### 2. Create conda environment

```cmd
conda create -n poweroutage python=3.11 -y
conda activate poweroutage
```

If you prefer virtual environment instead of conda:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```cmd
pip install -r requirements.txt
pip install -e .
```

If Excel reading fails, install:

```cmd
pip install openpyxl
```

### 4. Prepare dataset from original four files

```cmd
set PYTHONPATH=src
python scripts\prepare_original_dataset.py
```

Output:

```text
data\processed\original_power_outage_training.csv
```

### 5. Optional: prepare dataset from already merged CSV

Use this only if you want to train from `merged_utility_storm_2024.csv`.

```cmd
set PYTHONPATH=src
python scripts\prepare_from_merged_dataset.py
```

Output:

```text
data\processed\merged_power_outage_training.csv
```

To train from this merged prepared file:

```cmd
set TRAINING_SOURCE_PATH=data/processed/merged_power_outage_training.csv
```

### 6. Train model with MLflow

For original four-file prepared data:

```cmd
set PYTHONPATH=src
python main.py
```

For already merged CSV prepared data:

```cmd
set TRAINING_SOURCE_PATH=data/processed/merged_power_outage_training.csv
set PYTHONPATH=src
python main.py
```

Training creates:

```text
models\model.joblib
models\metrics.json
mlruns\
```

### 7. View MLflow UI

```cmd
mlflow ui --backend-store-uri mlruns --port 5001
```

Open:

```text
http://127.0.0.1:5001
```

### 8. Run Flask app locally

```cmd
set PYTHONPATH=src
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Health check:

```text
http://127.0.0.1:5000/health
```

### 9. Run tests

```cmd
set PYTHONPATH=src
python -m unittest discover -s tests
```

### 10. Run DVC

DVC works best after Git is initialized.

```cmd
git init
dvc init
set PYTHONPATH=src
dvc repro
dvc metrics show
```

Expected files:

```text
.dvc\
dvc.lock
dvc.yaml
models\metrics.json
```

Save locally:

```cmd
git add .
git commit -m "add power outage mlops pipeline with dvc"
```

### 11. Build Docker image

Make sure Docker Desktop is running.

```cmd
docker build --no-cache -t testdockerhri.azurecr.io/mltest:latest .
```

Run container locally:

```cmd
docker run -p 5000:5000 testdockerhri.azurecr.io/mltest:latest
```

Open:

```text
http://127.0.0.1:5000
```

If port 5000 is busy:

```cmd
docker run -p 5001:5000 testdockerhri.azurecr.io/mltest:latest
```

### 12. Push Docker image to Azure Container Registry

In Azure Portal:

```text
Container Registry -> testdockerhri -> Access keys -> Enable Admin user
```

Then:

```cmd
docker login testdockerhri.azurecr.io
docker push testdockerhri.azurecr.io/mltest:latest
```

### 13. Create Azure Web App for Containers

In Azure Portal:

```text
Create Resource -> Web App
```

Use:

```text
Publish: Container
Operating System: Linux
Region: Central US
Image Source: Azure Container Registry
Registry: testdockerhri
Image: mltest
Tag: latest
```

After creation, open the Web App URL.

### 14. Connect GitHub continuous deployment

Push project to GitHub:

```cmd
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

In GitHub repository secrets, add:

```text
AZURE_CREDENTIALS
ACR_USERNAME
ACR_PASSWORD
```

Then use:

```text
Azure Web App -> Deployment Center -> GitHub
```

or use the workflow:

```text
.github\workflows\azure-webapp-container.yml
```

### 15. Tomorrow continuation point

If stopping after DVC today, tomorrow continue from:

```cmd
conda activate poweroutage
cd C:\DA_Project
docker login testdockerhri.azurecr.io
docker push testdockerhri.azurecr.io/mltest:latest
```

Then continue Azure Web App setup.

## Merge Original Source Files

The project is now configured to use your original source folder by default:

```text
C:\Users\Public\Hritik\project\Power_outrage\Part_1_phase\output\output\Dataset_original
```

It expects:

- `Utility_Data_2024.xlsx`
- `Service_Territory_2024.xlsx`
- `Reliability_2024.xlsx`
- `StormEvents_details-ftp_v1.0_d2024_c20260116.csv`

Create the model-ready training file:

```bash
set PYTHONPATH=src
python scripts/prepare_original_dataset.py
```

This writes:

```text
data/processed/original_power_outage_training.csv
```

## Use the Already Merged CSV

You can also train from the already merged file:

```text
C:\Users\Public\Hritik\project\Power_outrage\Part_1_phase\output\output\merged_utility_storm_2024.csv
```

That file is about 1.5 GB, so the project reads it in chunks and creates one model-ready row per utility/state.

Prepare it:

```bash
set PYTHONPATH=src
python scripts/prepare_from_merged_dataset.py
```

This writes:

```text
data/processed/merged_power_outage_training.csv
```

Train from the merged prepared file:

```bash
set TRAINING_SOURCE_PATH=data/processed/merged_power_outage_training.csv
set PYTHONPATH=src
python main.py
```

## API Prediction Example

```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "state": "TX",
    "ownership": "Investor Owned",
    "primary_storm_type": "Thunderstorm Wind",
    "storm_event_count": 180,
    "total_property_damage_usd": 7500000,
    "total_crop_damage_usd": 80000,
    "county_count": 35,
    "saidi_minutes": 260,
    "saifi_interruptions": 2.1,
    "caidi_minutes": 124,
    "population_served": 900000
  }'
```

## DVC Commands

```bash
dvc init
dvc add data/raw/power_outage_sample.csv
dvc repro
dvc metrics show
```

## MLflow Commands

```bash
python main.py
mlflow ui --backend-store-uri mlruns
```

Then open:

```text
http://127.0.0.1:5001
```

Recommended:

```bash
mlflow ui --backend-store-uri mlruns --port 5001
```

## Docker Commands

```bash
docker build -t testdockerhri.azurecr.io/mltest:latest .
docker run -p 5000:5000 testdockerhri.azurecr.io/mltest:latest
docker login testdockerhri.azurecr.io
docker push testdockerhri.azurecr.io/mltest:latest
```

## Azure Deployment Summary

Create ACR:

| Setting | Value |
| --- | --- |
| Registry Name | `testdockerhri` |
| Region | `Central US` |
| Access Keys | Enabled |

Create Azure Web App:

| Setting | Value |
| --- | --- |
| Name | `testdockerhri` |
| Region | `Central US` |
| Publish | Container |
| Container Type | Docker |
| Image | `testdockerhri.azurecr.io/mltest:latest` |

## CI/CD Flow

```text
Developer
   ↓
GitHub Repository
   ↓
GitHub Actions builds Docker image
   ↓
Image pushed to Azure Container Registry
   ↓
Azure Web App pulls latest image
   ↓
Container restarts
   ↓
Live application updated
```



'''
project live dasboard for data analyst: https://power-outage-dashboard-phim.onrender.com/


project live url for data science: https://testdockerhritik-hag0c6cnghd5cdca.centralus-01.azurewebsites.net/predict
'''
