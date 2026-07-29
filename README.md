# SupplyPrescript

An AI-powered Supply Chain Decision Support System that predicts shipment delays, recommends optimal business actions using Machine Learning and Optimization, and enables closed-loop analytics with FastAPI, React, PostgreSQL, and XGBoost.

## Project Status
Currently on **Day 13** of a 25-day project development plan. The ML pipeline (data → model → evaluation) is built and validated; API/frontend/database layers are upcoming.

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
| Feature Importance        | `11_Feature_Importance.ipynb`        | Compared untuned vs. tuned feature importances,`Results/`|

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

Here's a draft for every day completed so far (1–13), each verified against your actual notebook code/outputs rather than assumed:

Day 1 — Data Understanding

Loaded the raw SCMS Delivery History Dataset (10,324 rows, 33 columns). Initial checks (.info(), .isnull().sum(), .dtypes) showed most columns are complete, with three exceptions: Shipment Mode (360 missing), Dosage (1,736 missing), and Line Item Insurance (USD) (287 missing). Weight (Kilograms) and Freight Cost (USD) are stored as text (object) rather than numeric, due to non-numeric placeholder values in some rows (e.g. "Weight Captured Separately"). These will need cleaning before they're usable numerically.

Day 2 — Data Cleaning

Removed duplicate rows (0 found — dataset had none). Converted the three delivery-related date columns (Scheduled Delivery Date, Delivered to Client Date, Delivery Recorded Date) to proper datetime type. Missing values in Shipment Mode, Dosage, and Line Item Insurance (USD) were identified but deliberately left unfilled at this stage — imputation happens later, during feature engineering. Saved as cleaned_dataset.csv.

Day 3 — Start EDA

Began exploratory analysis on the cleaned dataset: separated columns into numeric vs. categorical, checked value counts for every categorical column, and confirmed dataset shape and structure going into deeper analysis.

Day 4 — EDA Visualizations

Added histograms and boxplots for every numeric column to inspect distributions and outliers, plus bar charts of the top categories for key categorical columns (e.g. Country, Fulfill Via). Also computed a full numeric correlation matrix to check for relationships between features ahead of modeling.

Day 5 — EDA Insights

Consolidated the visual analysis into insights: identified skewed distributions in cost/weight-related columns and notable class imbalance in categorical fields tied to country and vendor concentration. These observations directly informed the high-cardinality handling and imbalance-aware evaluation approach used in later days.

(Note: Days 3–5 all live in one shared notebook, 03_Exploratory_Data_Analysis.ipynb, so consider splitting these into separate cells/sections if your reviewer expects day-by-day separation.)

Day 6 — Feature Engineering

Converted Weight (Kilograms) and Freight Cost (USD) to numeric (coercing invalid entries to NaN). Created the modeling target: Delay Days (days late) and Is Delayed (binary flag, Delay Days > 0). Class distribution: 9,138 on-time vs. 1,186 delayed (~11.5% delay rate) — confirming the class imbalance flagged in EDA. Extracted Scheduled Month, Scheduled Year, and Scheduled Weekday from the scheduling date. Filled remaining missing values (Unknown/Not Specified for categoricals, median for numerics). Final shape: (10,324, 38).

Day 7 — Data Preprocessing

Dropped ID columns (no predictive value) and leakage columns — Delivered to Client Date, Delivery Recorded Date, Delay Days — keeping only Is Delayed as the target, since these columns wouldn't be known at prediction time. Simplified 7 high-cardinality categorical columns (e.g. Country, Vendor) to their top 15 categories plus "Other" to keep dimensionality manageable. One-hot encoded all categorical columns. Final shape: (10,324, 158).

Day 8 — Train/Test Split

Split into 80/20 train/test (X_train: 8,259 rows, X_test: 2,065 rows, 157 features) using stratify=y to preserve the delay rate in both sets (11.49% train vs. 11.48% test — confirming the split didn't introduce imbalance skew). Used random_state=42 for reproducibility.

Day 9 — Baseline Model

Trained a Logistic Regression baseline. Result: 88.52% accuracy, but 0.0 precision/recall/F1 — the model never predicted a single "delayed" case, defaulting to the majority class every time. This is a direct consequence of class imbalance and is the key motivating insight for using precision/recall/F1/ROC-AUC in later evaluation rather than accuracy alone.

Day 10 — XGBoost Model

Trained an untuned XGBoost classifier. Result: 89.49% accuracy, 0.579 precision, 0.308 recall, 0.402 F1 — a substantial improvement over the baseline in actually detecting delayed shipments. Extracted feature importances; top drivers were Fulfill Via_From RDC, Country_South Africa, and Country_Nigeria. Model saved to ../Models/xgboost_model.pkl.

Day 11 — Hyperparameter Tuning

Ran RandomizedSearchCV (20 iterations, 5-fold CV) over n_estimators, max_depth, learning_rate, subsample, and colsample_bytree, optimizing for F1 score (scoring="f1") rather than accuracy, since F1 better reflects performance on the minority "delayed" class. Best params: max_depth=7, n_estimators=300, learning_rate=0.2, subsample=0.8, colsample_bytree=1.0 (best CV F1: 0.396). Test-set result: 89.59% accuracy, 0.579 precision, 0.342 recall, 0.430 F1 — a modest F1 improvement over the untuned model. Saved to ../Models/xgboost_best_model.pkl.

Day 12 — Model Evaluation

Compared all three models on ROC-AUC and plotted ROC curves. Untuned XGBoost had the best ROC-AUC (0.903), edging out the tuned model (0.882) despite the tuned model's better F1 — because tuning optimized for F1 (a threshold-specific metric), not for ranking quality across all thresholds. Baseline's ROC-AUC (0.658) confirms its probability scores carried weak signal despite its useless classification decisions. Takeaway: the tuning objective directly shapes which metric improves, and should be chosen based on the actual business trade-off that matters.

Day 13 — Feature Importance

(as finalized above) Compared untuned vs. tuned feature importances. Core drivers (Fulfill Via_From RDC, Country_South Africa, Country_Nigeria, Vendor INCO Term_DDP, Scheduled Year) are stable across both models, indicating real signal. The deeper tuned model (max_depth=7) spreads importance more thinly and surfaces additional vendor/product-specific features, suggesting some delay risk is tied to specific supplier logistics.