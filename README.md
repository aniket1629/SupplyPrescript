# SupplyPrescript

An AI-powered Supply Chain Decision Support System that predicts shipment delays, recommends optimal business actions using Machine Learning and Optimization, and enables closed-loop analytics with FastAPI, React, PostgreSQL, and XGBoost.

## Project Status
Currently on **Day 12** of a 25-day internship development plan. The ML pipeline (data → model → evaluation) is built and validated; API/frontend/database layers are upcoming.

## Dataset
[SCMS Delivery History Dataset](.) — ~10,324 historical HIV/ARV medical supply shipment records to countries across Africa and Asia, including shipment mode, vendor, product, cost, weight, and delivery dates.

## Problem
Predict whether a shipment will be delivered late (`Is Delayed`), based on features known at or before the point of scheduling — vendor, shipment mode, product type, cost, weight, and scheduling date features.

## Pipeline
| Stage                     | Notebook                             | Output                                                   |
|---------------------------|--------------------------------------|----------------------------------------------------------|
| Data Understanding        | `01_Data_Understanding.ipynb`        | initial profiling                                        |
| Data Cleaning             | `02_Data_Cleaning.ipynb`             | `cleaned_dataset.csv`                                    |
| EDA                       | `03_Exploratory_Data_Analysis.ipynb` | —                                                        |
| Feature Engineering       | `04_Feature_Engineering.ipynb`       | `feature_engineered_dataset.csv`                         |
| Preprocessing (encoding)  | `05_Data_Preprocessing.ipynb`        | `preprocessed_dataset.csv`                               |
| Train/Test Split          | `06_Train_test_split.ipynb`          | `x_train.csv`, `x_test.csv`, `y_train.csv`, `y_test.csv` |
| Baseline Model            | `07_Baseline_Model.ipynb`            | Logistic Regression                                      |
| XGBoost Model             | `08_XGBoost_Model.ipynb`             | `xgboost_model.pkl`                                      |
| Hyperparameter Tuning     | `09_Hyperparameter_Tuning.ipynb`     | `xgboost_best_model.pkl`                                 |
| Model Evaluation          | `10_Model_Evaluation.ipynb`          | ROC-AUC comparison, `Results/`                           |

## Results (Test Set)
| Model                          | Accuracy | Precision | Recall | F1        | ROC-AUC   |
|--------------------------------|----------|-----------|--------|-----------|-----------|
| Baseline (Logistic Regression) | 0.885    | 0.000     | 0.000  | 0.000     | 0.658     |
| XGBoost (Untuned)              | 0.895    | 0.579     | 0.308  | 0.402     | **0.903** |
| XGBoost (Tuned, `scoring="f1"`)| 0.896    | 0.579     | 0.342  | **0.430** | 0.882     |

**Key finding:** raw accuracy is misleading on this dataset due to class imbalance (~88.5% on-time shipments) — the baseline model never once predicted a delay despite its high accuracy. XGBoost substantially improves detection of actual delays. Tuning for F1 improved F1 slightly but reduced ranking quality (ROC-AUC), showing the tuning objective directly trades off against other metrics.

## Tech Stack
- **ML:** Python, pandas, scikit-learn, XGBoost
- **API:** FastAPI *(planned)*
- **Frontend:** React *(planned)*
- **Database:** PostgreSQL *(planned)*

## Requirements
See `Requirements.txt`.

## Project Structure
```
SupplyPrescript/
├── Dataset/
├── Models/
├── Results/
├── Notebooks/
└── README.md
```