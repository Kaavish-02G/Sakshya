from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageEnhance


# Calibration range from our current ELA experiment.
ELA_MIN = 2.2942684
ELA_MAX = 28.091797


def normalize_ela(mean_ela: float) -> float:
    """Convert mean ELA intensity to a 0–1 operational score."""
    score = (mean_ela - ELA_MIN) / (ELA_MAX - ELA_MIN)
    return max(0.0, min(1.0, score))


def analyze_ela(
    image_path: str,
    output_dir: str = "ela_outputs",
    quality: int = 90,
) -> dict:
    """
    Perform Error Level Analysis on an image.

    Returns:
        {
            "ela_score": float,
            "mean_ela": float,
            "heatmap_path": str
        }
    """

    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    original = Image.open(image_path).convert("RGB")

    # Recompress the image.
    temp_path = output_dir / "_ela_temp.jpg"
    original.save(temp_path, "JPEG", quality=quality)

    recompressed = Image.open(temp_path).convert("RGB")

    # Calculate pixel-level differences.
    difference = ImageChops.difference(original, recompressed)

    # Amplify differences for visualization.
    extrema = difference.getextrema()
    max_difference = max(
        channel_max
        for channel_min, channel_max in extrema
    )

    scale = 255 / max_difference if max_difference != 0 else 1

    ela_image = ImageEnhance.Brightness(
        difference
    ).enhance(scale)

    # Calculate mean ELA intensity.
    grayscale = np.array(
        ela_image.convert("L"),
        dtype=np.float32
    )

    mean_ela = float(grayscale.mean())

    # Convert to operational 0–1 score.
    ela_score = normalize_ela(mean_ela)

    # Save visualization.
    heatmap_path = output_dir / f"{image_path.stem}_ela.jpg"
    ela_image.save(heatmap_path)

    # Remove temporary recompressed image.
    if temp_path.exists():
        temp_path.unlink()

    return {
        "ela_score": ela_score,
        "mean_ela": mean_ela,
        "heatmap_path": str(heatmap_path),
    }