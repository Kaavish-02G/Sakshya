import pandas as pd

INPUT_FILE = "experiments/ela/ela_measurements.csv"

ELA_MIN = 2.2942684
ELA_MAX = 28.091797


def normalize_ela(mean_ela):
    score = (mean_ela - ELA_MIN) / (ELA_MAX - ELA_MIN)
    return max(0.0, min(1.0, score))


df = pd.read_csv(INPUT_FILE)

df["ela_score"] = df["mean"].apply(normalize_ela)

print(df.groupby("label")["ela_score"].agg([
    "mean",
    "min",
    "max"
]))

df.to_csv(
    "experiments/ela/ela_scored.csv",
    index=False
)

print("\nSaved to: experiments/ela/ela_scored.csv")