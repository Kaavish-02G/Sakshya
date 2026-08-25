import pandas as pd
from sklearn.metrics import roc_auc_score

INPUT_FILE = "experiments/ela/validation_ela_measurements.csv"

df = pd.read_csv(INPUT_FILE)

# REAL = 0, FAKE = 1
y_true = (df["label"] == "FAKE").astype(int)

features = [
    "mean",
    "median",
    "p95",
    "high_error_ratio"
]

print("\nELA ROC-AUC Results")
print("-" * 30)

for feature in features:
    auc = roc_auc_score(y_true, df[feature])
    print(f"{feature:20s}: {auc:.4f}")