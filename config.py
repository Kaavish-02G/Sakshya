from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "evidence"
UPLOADS_DIR = BASE_DIR / "uploads"
REGISTRY_PATH = DATA_DIR / "evidence_registry.json"

IMAGE_MODEL = "dima806/deepfake_vs_real_image_detection"
AUDIO_MODEL = "garystafford/wav2vec2-deepfake-voice-detector"
TEXT_MODEL = "adhwiraj/ai-content-detector-roberta-v1"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}
TEXT_EXTENSIONS = {".txt"}
