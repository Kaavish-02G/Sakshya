from functools import lru_cache
from pathlib import Path

from config import AUDIO_MODEL
from forensic.risk import recommendation_for, risk_from_score


@lru_cache(maxsize=1)
def _audio_components():
    import torch
    from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
    model = AutoModelForAudioClassification.from_pretrained(AUDIO_MODEL)
    extractor = AutoFeatureExtractor.from_pretrained(AUDIO_MODEL)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device).eval()
    return model, extractor, device


def detect_audio(audio_path: str | Path, chunk_seconds: int = 5) -> dict:
    import librosa
    import torch
    audio, _ = librosa.load(str(audio_path), sr=16000, mono=True)
    if len(audio) == 0:
        raise ValueError("The audio file contains no readable samples.")
    model, extractor, device = _audio_components()
    labels = {int(key): str(value).lower() for key, value in model.config.id2label.items()}
    fake_index = next((index for index, label in labels.items() if "fake" in label or "spoof" in label), 1)
    scores = []
    for start in range(0, len(audio), 16000 * chunk_seconds):
        inputs = extractor(audio[start:start + 16000 * chunk_seconds], sampling_rate=16000, return_tensors="pt", padding=True)
        inputs = {key: value.to(device) for key, value in inputs.items()}
        with torch.no_grad():
            probabilities = torch.softmax(model(**inputs).logits, dim=-1)[0]
        scores.append(float(probabilities[fake_index].item()))
    fake_score = sum(scores) / len(scores)
    return {"fake_score": round(fake_score, 4), "real_score": round(1 - fake_score, 4), "risk": risk_from_score(fake_score),
            "chunks_analyzed": len(scores), "assessment": "Synthetic-voice likelihood from screened audio chunks.",
            "recommendation": recommendation_for(fake_score),
            "limitations": "Experimental screening only; results may not generalize to all generators or recording conditions."}
