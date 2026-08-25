from PIL import Image, ImageChops, ImageEnhance
from pathlib import Path

INPUT_DIR = Path("experiments/ela/dataset/images")
OUTPUT_DIR = Path("experiments/ela/dataset/ela_images")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_ela(image_path, output_path, quality=90):
    original = Image.open(image_path).convert("RGB")

    # Recompress the image
    temp_path = OUTPUT_DIR / "_temp.jpg"
    original.save(temp_path, "JPEG", quality=quality)

    recompressed = Image.open(temp_path).convert("RGB")

    # Calculate pixel-level differences
    difference = ImageChops.difference(original, recompressed)

    # Make the differences visible
    extrema = difference.getextrema()
    max_difference = max(
        channel_max
        for channel_min, channel_max in extrema
    )

    scale = 255 / max_difference if max_difference != 0 else 1
    ela_image = ImageEnhance.Brightness(difference).enhance(scale)

    ela_image.save(output_path)


images = list(INPUT_DIR.glob("*.jpg"))

print(f"Found {len(images)} images.")

for i, image_path in enumerate(images, start=1):
    output_path = OUTPUT_DIR / image_path.name

    try:
        generate_ela(image_path, output_path)
        print(f"[{i}/{len(images)}] {image_path.name}")

    except Exception as e:
        print(f"[ERROR] {image_path.name}: {e}")

temp_path = OUTPUT_DIR / "_temp.jpg"
if temp_path.exists():
    temp_path.unlink()

print("\nELA generation complete.")