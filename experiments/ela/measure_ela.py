from PIL import Image
from pathlib import Path
import pandas as pd
import numpy as np

ELA_DIR = Path("experiments/ela/dataset/ela_images")
OUTPUT_FILE = Path("experiments/ela/ela_measurements.csv")

results = []

for image_path in ELA_DIR.glob("*.jpg"):
    image = Image.open(image_path).convert("L")
    pixels = np.array(image, dtype=np.float32)

    results.append({
        "filename": image_path.name,
        "label": "REAL" if image_path.name.startswith("REAL_") else "FAKE",
        "mean": pixels.mean(),
        "median": np.median(pixels),
        "p95": np.percentile(pixels, 95),
        "high_error_ratio": np.mean(pixels > 128)
    })

df = pd.DataFrame(results)

df.to_csv(OUTPUT_FILE, index=False)

print(df.groupby("label")[[
    "mean",
    "median",
    "p95",
    "high_error_ratio"
]].mean())

print(f"\nSaved measurements to: {OUTPUT_FILE}")