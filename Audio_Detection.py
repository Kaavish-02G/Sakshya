import torch
import librosa

from transformers import (
    AutoModelForAudioClassification,
    AutoFeatureExtractor
)

MODEL_NAME = "garystafford/wav2vec2-deepfake-voice-detector"

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading audio model...")

model = AutoModelForAudioClassification.from_pretrained(MODEL_NAME)

feature_extractor = AutoFeatureExtractor.from_pretrained(
    MODEL_NAME
)

model.to(device)
model.eval()

print("Audio model loaded.")


def detect_audio(audio_path: str) -> dict:

    audio, sr = librosa.load(
        audio_path,
        sr=16000,
        mono=True
    )

    chunk_duration = 5
    chunk_size = 16000 * chunk_duration

    scores = []

    for start in range(0, len(audio), chunk_size):

        chunk = audio[start:start + chunk_size]

        start_time = start / 16000
        end_time = (start + len(chunk)) / 16000

        inputs = feature_extractor(
            chunk,
            sampling_rate=16000,
            return_tensors="pt",
            padding=True
        )

        inputs = {
            key: value.to(device)
            for key, value in inputs.items()
        }

        with torch.no_grad():

            outputs = model(**inputs)

            probabilities = torch.softmax(
                outputs.logits,
                dim=-1
            )

        real_score = probabilities[0][0].item()
        fake_score = probabilities[0][1].item()

        scores.append(fake_score)

        print("\n------------------------------")
        print(
            "Chunk:",
            round(start_time, 2),
            "-",
            round(end_time, 2),
            "seconds"
        )

        print(
            "Fake score:",
            round(fake_score, 4)
        )

        print(
            "Real score:",
            round(real_score, 4)
        )

        if fake_score >= 0.70:
            print("Result: FAKE LIKELY")

        elif fake_score >= 0.40:
            print("Result: SUSPICIOUS")

        else:
            print("Result: REAL LIKELY")

    return {
        "chunks": len(scores),
        "scores": scores
    }


if __name__ == "__main__":

    result = detect_audio("audio_test_real.wav")

    print("\n==============================")
    print("AUDIO ANALYSIS COMPLETE")
    print("==============================")

    print(
        "Chunks analyzed:",
        result["chunks"]
    )