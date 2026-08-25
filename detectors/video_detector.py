import os
import tempfile
from pathlib import Path

from detectors.image_detector import detect_image
from forensic.risk import recommendation_for, risk_from_score


def detect_video(video_path: str | Path, samples_per_second: int = 2) -> dict:
    import cv2
    video = cv2.VideoCapture(str(video_path))
    if not video.isOpened():
        raise ValueError("Could not open the video file.")
    fps = video.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        video.release()
        raise ValueError("Could not determine the video frame rate.")
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    interval, frame_number, scores, suspicious = max(1, int(fps / samples_per_second)), 0, [], []
    try:
        while True:
            ok, frame = video.read()
            if not ok:
                break
            frame_number += 1
            if frame_number % interval:
                continue
            faces = cascade.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 1.1, 5, minSize=(80, 80))
            if len(faces) == 0:
                continue
            x, y, w, h = max(faces, key=lambda face: face[2] * face[3])
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
                temp_path = temp.name
            try:
                cv2.imwrite(temp_path, frame[y:y + h, x:x + w])
                score = detect_image(temp_path)["fake_score"]
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            scores.append(score)
            if score >= 0.70:
                suspicious.append(frame_number)
    finally:
        video.release()
    if not scores:
        return {"fake_score": None, "real_score": None, "risk": "INCONCLUSIVE", "frames_analyzed": 0, "suspicious_frames": [],
                "assessment": "No usable faces were detected in sampled frames.", "limitations": "Only face-containing frames are analyzed."}
    fake_score = sum(scores) / len(scores)
    return {"fake_score": round(fake_score, 4), "real_score": round(1 - fake_score, 4), "risk": risk_from_score(fake_score),
            "frames_analyzed": len(scores), "suspicious_frames": suspicious,
            "assessment": "Video manipulation likelihood based on analyzed face frames.", "recommendation": recommendation_for(fake_score),
            "limitations": "Frame-based image screening cannot establish temporal video authenticity."}
