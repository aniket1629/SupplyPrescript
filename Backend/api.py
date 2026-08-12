from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib

app = FastAPI()    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load trained model
model = joblib.load("../Models/xgboost_best_model.pkl")

MODEL_FEATURES = list(model.feature_names_in_)

# The model was trained on 157 columns, but our form only collects 4
# (country, shipment mode, weight, freight cost). Zero-filling the rest
# creates a row with ~145 one-hot columns simultaneously at 0 -- a pattern
# the model never saw in training (every real row has exactly one 1 per
# category group), so it always fell back to the majority class ("On Time").
#
# Fix: fill the columns the form doesn't collect with realistic defaults
# (median for numeric columns, most common category for one-hot groups)
# computed from the training data, so the row looks like "a typical
# shipment, except for what the user actually changed."

NUMERIC_COLUMNS = [
    "Unit of Measure (Per Pack)", "Line Item Quantity", "Line Item Value",
    "Pack Price", "Unit Price", "Weight (Kilograms)", "Freight Cost (USD)",
    "Line Item Insurance (USD)", "Scheduled Month", "Scheduled Year",
    "Scheduled Weekday",
]

CATEGORICAL_PREFIXES = [
    "Country", "Managed By", "Fulfill Via", "Vendor INCO Term",
    "Shipment Mode", "Product Group", "Sub Classification", "Vendor",
    "Item Description", "Molecule/Test Type", "Brand", "Dosage",
    "Dosage Form", "Manufacturing Site", "First Line Designation",
]


def _compute_training_defaults():
    """Compute median (numeric) / most-common-category (one-hot) defaults
    from x_train.csv, matching the same column-cleaning the model was
    trained with."""
    x_train = pd.read_csv("../Dataset/x_train.csv")
    x_train.columns = (
        x_train.columns
        .str.replace("[", "", regex=False)
        .str.replace("]", "", regex=False)
        .str.replace("<", "", regex=False)
    )

    numeric_defaults = x_train[NUMERIC_COLUMNS].median().to_dict()

    # Group one-hot columns by their category prefix
    dummy_cols = [c for c in MODEL_FEATURES if c not in NUMERIC_COLUMNS]
    groups = {}
    for c in dummy_cols:
        matched = [p for p in CATEGORICAL_PREFIXES if c.startswith(p + "_")]
        prefix = max(matched, key=len)  # longest match handles overlapping prefixes
        groups.setdefault(prefix, []).append(c)

    # For each group, pick whichever is more common: the most frequent
    # category, or the implicit "baseline" (all dummies 0, since the
    # encoding used drop_first=True)
    n_rows = len(x_train)
    categorical_defaults = {}
    for prefix, cols in groups.items():
        counts = x_train[cols].sum()
        baseline_count = n_rows - counts.sum()
        best_col = counts.idxmax()
        categorical_defaults[prefix] = None if baseline_count > counts.max() else best_col

    return numeric_defaults, categorical_defaults, groups


NUMERIC_DEFAULTS, CATEGORICAL_DEFAULTS, CATEGORY_GROUPS = _compute_training_defaults()


def build_feature_row(country, shipment_mode, weight, freight_cost):
    # Start from a "typical shipment" baseline instead of all zeros
    row = {col: 0 for col in MODEL_FEATURES}
    for col, val in NUMERIC_DEFAULTS.items():
        row[col] = val
    for prefix, chosen_col in CATEGORICAL_DEFAULTS.items():
        if chosen_col is not None:
            row[chosen_col] = 1

    # Now override with what the user actually picked
    if "Weight (Kilograms)" in row:
        row["Weight (Kilograms)"] = weight
    if "Freight Cost (USD)" in row:
        row["Freight Cost (USD)"] = freight_cost

    # Clear the default Country selection, then set the user's choice
    for c in CATEGORY_GROUPS.get("Country", []):
        row[c] = 0
    country_col = f"Country_{country}"
    if country_col in row:
        row[country_col] = 1

    # Clear the default Shipment Mode selection, then set the user's choice
    for c in CATEGORY_GROUPS.get("Shipment Mode", []):
        row[c] = 0
    mode_col = f"Shipment Mode_{shipment_mode}"
    if mode_col in row:
        row[mode_col] = 1

    return row


@app.get("/")
def home():
    return {"message": "Supply Prescription Prediction API"}

from pydantic import BaseModel

class InputData(BaseModel):
    data: dict

@app.post("/predict")
def predict(input_data: InputData):

    try:
        # Convert the input dictionary to a DataFrame
        df = pd.DataFrame([input_data.data])

        # Clean column names (remove brackets if present)
        df.columns = (
            df.columns
            .str.replace("[", "", regex=False)
            .str.replace("]", "", regex=False)
            .str.replace("<", "", regex=False)
        )

        # Make prediction
        prediction = model.predict(df)[0]

        return {
            "prediction": int(prediction)
        }

    except Exception as e:
        return {
            "error": "Invalid input. Please provide all required model features with the correct data types."
        }


@app.post("/predict_custom")
def predict_custom(payload: dict = Body(...)):
    try:
        row = build_feature_row(
            country=payload["country"],
            shipment_mode=payload["shipmentMode"],
            weight=float(payload["weight"]),
            freight_cost=float(payload["freightCost"]),
        )
        df = pd.DataFrame([row])
        prediction = model.predict(df)[0]
        return {"prediction": int(prediction)}
    except Exception as e:
        return {"error": str(e)}


@app.get("/test")
def test_prediction():
    try:
        sample = pd.read_csv("../Dataset/x_test.csv")

        # Remove square brackets from column names
        sample.columns = sample.columns.str.replace(r"[\[\]]", "", regex=True)

        sample = sample.iloc[[0]]

        prediction = model.predict(sample)[0]

        return {
            "prediction": int(prediction)
        }

    except Exception as e:
        return {
            "error": str(e)
        }
@app.get("/columns")
def columns():
    return {
        "num_features": len(model.feature_names_in_),
        "features": model.feature_names_in_.tolist()
    }
@app.get("/compare")
def compare():

    sample = pd.read_csv("../Dataset/x_test.csv")
    sample.columns = (
    sample.columns
    .str.replace("[", "", regex=False)
    .str.replace("]", "", regex=False)
)

    model_cols = set(model.feature_names_in_)
    sample_cols = set(sample.columns)

    return {
        "missing_in_sample": list(model_cols - sample_cols),
        "extra_in_sample": list(sample_cols - model_cols),
        "model_count": len(model_cols),
        "sample_count": len(sample_cols)
    }