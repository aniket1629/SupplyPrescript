from fastapi import FastAPI
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