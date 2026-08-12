# SupplyPrescript — Technical Documentation

This document explains how the system works internally — architecture, 
data flow, and known limitations. For setup/run instructions, see 
README.md.

## Architecture

1. **Data pipeline** (Notebooks 01–11): raw shipment data is cleaned, 
   feature-engineered, and used to train an XGBoost classifier that 
   predicts whether a shipment will be delayed (`Is Delayed`).
2. **Backend** (FastAPI, `Backend/api.py`): loads the trained model 
   (`Models/xgboost_best_model.pkl`) and exposes it via REST endpoints.
3. **Frontend** (`Frontend/index.html`, `script.js`, `style.css`): a 
   dashboard where users enter shipment details and get a live 
   prediction, plus a fixed-row demo endpoint for quick backend 
   health checks.

## Data Flow — How a Prediction Actually Happens

1. User fills in Country, Shipment Mode, Weight, and Freight Cost on 
   the dashboard and clicks "Predict This Shipment."
2. `script.js` validates the inputs client-side (non-empty, positive 
   numbers) and sends them as JSON to `POST /predict_custom`.
3. In `api.py`, `build_feature_row()` builds a full 157-column row:
   - Starts from a "typical shipment" baseline — median values for 
     numeric columns, most common category for each one-hot group — 
     computed once at startup from `x_train.csv` (see 
     `_compute_training_defaults()`).
   - Overrides the columns the user actually provided (weight, 
     freight cost, and the one-hot columns matching the chosen 
     country/shipment mode).
4. The completed row is passed to `model.predict()`, and the result 
   (0 = on time, 1 = delayed) is returned as JSON.
5. `script.js` renders the result with a color-coded message.

## API Endpoints

### `GET /`
Health check. Returns a welcome message.

### `POST /predict`
Raw prediction endpoint. Expects all 157 one-hot-encoded model 
columns as a dict. Used for internal testing, not by the dashboard.

### `POST /predict_custom`
User-facing prediction endpoint. Expects:
- `country` (string)
- `shipmentMode` (string)
- `weight` (number, must be > 0)
- `freightCost` (number, must be > 0)

Fields not collected from the user fall back to training-data 
defaults (see `build_feature_row()` in `api.py`). Unknown category 
values (e.g. a country not in the training data) are silently 
skipped, falling back to the default for that group rather than 
raising an error.

### `GET /test`
Fixed demo endpoint — always predicts on row 0 of `x_test.csv`. 
Labeled on the dashboard as a demo, not a real prediction tool.

### `GET /columns`
Returns the full list of 157 feature columns the model expects, 
useful for debugging what `/predict` needs.

### `GET /compare`
Debug endpoint comparing the model's expected columns against the 
dataset's actual columns — flags any mismatch.

## Known Limitations

- `/predict_custom` only exposes 4 of 157 model features; the rest 
  use training-data defaults, which may not reflect a specific 
  shipment's true characteristics (e.g. actual vendor, product type).
- No authentication on any endpoint — anyone who can reach the API 
  can call it.
- CORS is hardcoded to `http://127.0.0.1:5500` in `api.py` — must be 
  updated if the frontend is ever served from a different port or 
  domain, or requests will be silently blocked by the browser.
- Model performance: Recall 0.34 (see `10_Model_Evaluation.ipynb`), 
  meaning it misses roughly two-thirds of actual delayed shipments. 
  This reflects the real difficulty of predicting a rare event 
  (~11.5% delay rate) with the available features, not a bug.
- Client-side validation (non-empty, positive numbers) can be 
  bypassed by calling the API directly — the backend does not 
  independently re-validate that weight/freight cost are positive.

## Reproducing the Model

Run notebooks 01 through 11 in order (see README.md for the full 
pipeline table). Each notebook saves its output to `Dataset/` or 
`Models/` for the next step to use. The final model is saved to 
`Models/xgboost_best_model.pkl` and loaded by `api.py` at startup.