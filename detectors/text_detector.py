from functools import lru_cache

from config import TEXT_MODEL
from forensic.risk import recommendation_for, risk_from_score


@lru_cache(maxsize=1)
def _text_components():
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    return AutoTokenizer.from_pretrained(TEXT_MODEL), AutoModelForSequenceClassification.from_pretrained(TEXT_MODEL)


def detect_text(text: str) -> dict:
    """Experimental screen. This model's declared label 0 is AI, label 1 is Human."""
    import torch
    if not text or not text.strip():
        raise ValueError("No text was supplied for analysis.")
    tokenizer, model = _text_components()
    inputs = tokenizer(text, truncation=True, max_length=512, return_tensors="pt")
    model.eval()
    with torch.no_grad():
        probabilities = torch.softmax(model(**inputs).logits, dim=-1)[0]
    ai_score, human_score = float(probabilities[0]), float(probabilities[1])
    return {"ai_score": round(ai_score, 4), "human_score": round(human_score, 4), "risk": risk_from_score(ai_score),
            "assessment": "AI-generation likelihood; experimental screening signal only.", "recommendation": recommendation_for(ai_score),
            "limitations": "AI-text detection is unreliable across models, languages, edits, and short text. It is not proof."}
