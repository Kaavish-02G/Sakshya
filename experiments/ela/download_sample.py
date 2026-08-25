import os
import pandas as pd
import requests

CSV_PATH = "experiments/ela/dataset/FINAL_DATASET.csv"
OUTPUT_DIR = "experiments/ela/dataset/images"

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH)

# Take 50 real + 50 fake images
real = df[df["label"] == "REAL"].head(50)
fake = df[df["label"] == "FAKE"].head(50)

sample = pd.concat([real, fake]).reset_index(drop=True)

for i, row in sample.iterrows():
    label = row["label"]
    image_id = row["image_id"]
    url = row["image_url"]

    filename = f"{label}_{image_id}.jpg"
    path = os.path.join(OUTPUT_DIR, filename)

    print(f"[{i + 1}/100] Downloading {filename}")

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        with open(path, "wb") as f:
            f.write(response.content)

    except Exception as e:
        print(f"  FAILED: {e}")

print("Done.")