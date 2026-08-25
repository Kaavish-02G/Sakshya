from functools import lru_cache
from pathlib import Path

from config import IMAGE_MODEL
from forensic.risk import recommendation_for, risk_from_score


@lru_cache(maxsize=1)
def _classifier():
    from transformers import pipeline
    return pipeline("image-classification", model=IMAGE_MODEL)


def detect_image(image_path: str | Path) -> dict:
    results = _classifier()(str(image_path))
    scores = {str(item["label"]).lower(): float(item["score"]) for item in results}
    fake_score = next((score for label, score in scores.items() if "fake" in label), 0.0)
    real_score = next((score for label, score in scores.items() if "real" in label), 0.0)
    return {"fake_score": round(fake_score, 4), "real_score": round(real_score, 4), "risk": risk_from_score(fake_score),
            "assessment": "Image manipulation likelihood; screening signal only.", "recommendation": recommendation_for(fake_score),
            "limitations": "This image model may be affected by concept drift and is not forensic proof."}
