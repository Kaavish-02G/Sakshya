from transformers import pipeline

classifier = pipeline(
    "image-classification",
    model="dima806/deepfake_vs_real_image_detection"
)

def detect_image(image_path):
    results = classifier(image_path)

    fake_score = 0
    real_score = 0

    for result in results:
        label = result["label"].lower()
        score = result["score"]

        if "fake" in label:
            fake_score = score

        elif "real" in label:
            real_score = score

    if fake_score >= 0.7:
        risk = "HIGH"
    elif fake_score >= 0.4:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "fake_score": fake_score,
        "real_score": real_score,
        "risk": risk
    }

print(detect_image("0224.png.jpg"))