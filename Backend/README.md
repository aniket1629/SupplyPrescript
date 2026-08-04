# SupplyPrescript Backend

This backend is built using **FastAPI**. It loads the trained XGBoost model and predicts whether a shipment will be delayed.

## Files

- `api.py` – Main FastAPI application
- `requirements.txt` – Required Python packages
- `README.md` – Project information

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
cd Backend
python -m uvicorn api:app --reload
```

## Open in Browser

- Home: http://127.0.0.1:8000/
- API Docs: http://127.0.0.1:8000/docs

## Endpoints

- `GET /` – Home page
- `POST /predict` – Predict shipment delay
- `GET /test` – Test the model
- `GET /columns` – Show model features
- `GET /compare` – Compare dataset and model columns