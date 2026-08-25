import os
import pandas as pd
import requests
import time

CSV_PATH = "experiments/ela/dataset/FINAL_DATASET.csv"
OUTPUT_DIR = "experiments/ela/dataset/validation_images"

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH)
validation = df[df["dataset_split"].str.lower() == "val"]

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    )
})

for _, row in validation.iterrows():
    label = row["label"]
    image_id = row["image_id"]
    url = row["image_url"]

    filename = f"{label}_{image_id}.jpg"
    path = os.path.join(OUTPUT_DIR, filename)

    # Already downloaded successfully
    if os.path.exists(path):
        continue

    success = False

    for attempt in range(3):
        try:
            response = session.get(url, timeout=20)
            response.raise_for_status()

            with open(path, "wb") as f:
                f.write(response.content)

            print(f"Downloaded: {filename}")
            success = True
            break

        except Exception as e:
            print(
                f"Attempt {attempt + 1}/3 failed: "
                f"{filename} -> {e}"
            )
            time.sleep(1)

    if not success:
        print(f"FINAL FAILURE: {filename}")

print("Validation download retry complete.")