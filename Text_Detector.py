"""Experimental AI-text screening for NYAYACHAIN."""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_NAME = "adhwiraj/ai-content-detector-roberta-v1"

print("Loading text model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()
print("Text model loaded.")


def detect_text(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("No text was supplied for analysis.")

    inputs = tokenizer(text, truncation=True, max_length=512, return_tensors="pt")
    with torch.no_grad():
        probabilities = torch.softmax(model(**inputs).logits, dim=-1)[0]

    # The model card defines label 0 as AI and label 1 as Human.
    ai_score = float(probabilities[0].item())
    human_score = float(probabilities[1].item())
    risk = "HIGH" if ai_score >= 0.70 else "MEDIUM" if ai_score >= 0.40 else "LOW"

    return {
        "ai_score": round(ai_score, 4),
        "human_score": round(human_score, 4),
        "risk": risk,
        "assessment": "AI-generation likelihood; experimental screening signal only.",
        "recommendation": "FLAGGED FOR FURTHER FORENSIC REVIEW" if ai_score >= 0.40 else "No strong AI-generation signal detected.",
        "limitations": "AI-text detection is not conclusive and may be unreliable across models, languages, editing, and short text."
    }


if __name__ == "__main__":
    with open("test_text.txt", "r", encoding="utf-8") as file:
        result = detect_text(file.read())

    print("\nTEXT ANALYSIS")
    print("AI-generation likelihood:", f"{result['ai_score'] * 100:.2f}%")
    print("Human-writing likelihood:", f"{result['human_score'] * 100:.2f}%")
    print("Risk:", result["risk"])
    print("Recommendation:", result["recommendation"])