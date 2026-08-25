import cv2
import os
from Image_Detector import detect_image

VIDEO_PATH = "test2.mp4"

video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():
    print("Could not open video")
    exit()

total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
fps = video.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    print("Could not determine FPS")
    video.release()
    exit()

duration = total_frames / fps

print("Total frames:", total_frames)
print("FPS:", fps)
print("Duration:", round(duration, 2), "seconds")

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

os.makedirs("suspicious_frames", exist_ok=True)

scores = []
frame_number = 0

# Analyze approximately 2 frames every second
frame_interval = max(1, int(fps / 2))

while True:

    ret, frame = video.read()

    if not ret:
        break

    frame_number += 1

    if frame_number % frame_interval != 0:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    if len(faces) == 0:
        print(
            "Frame", frame_number,
            ": No face detected"
        )
        continue

    # Select the largest face
    x, y, w, h = max(
        faces,
        key=lambda face: face[2] * face[3]
    )

    face = frame[y:y+h, x:x+w]

    temp_file = "temp_face.jpg"

    cv2.imwrite(temp_file, face)

    result = detect_image(temp_file)

    fake_score = result["fake_score"]

    scores.append({
        "frame": frame_number,
        "score": fake_score
    })

    print(
        "Frame", frame_number,
        "| Fake score:",
        round(fake_score, 4)
    )

    # Save suspicious face
    if fake_score >= 0.70:

        output_file = (
            "suspicious_frames/"
            f"frame_{frame_number}.jpg"
        )

        cv2.imwrite(output_file, face)

video.release()

if os.path.exists("temp_face.jpg"):
    os.remove("temp_face.jpg")


# ==============================
# FINAL RESULT
# ==============================

print("\n==============================")
print("VIDEO ANALYSIS COMPLETE")
print("==============================")

print(
    "Frames analyzed:",
    len(scores)
)

if len(scores) == 0:

    print("No usable faces were detected.")
    exit()


# Average score
average_score = sum(
    item["score"] for item in scores
) / len(scores)


# Number of suspicious frames
suspicious_frames = [
    item for item in scores
    if item["score"] >= 0.70
]

suspicious_count = len(suspicious_frames)

suspicious_percentage = (
    suspicious_count /
    len(scores)
) * 100


print(
    "Average fake score:",
    round(average_score, 4)
)

print(
    "Manipulation likelihood:",
    round(average_score * 100, 2),
    "%"
)

print(
    "Suspicious frames:",
    suspicious_count,
    "/",
    len(scores)
)

print(
    "Suspicious percentage:",
    round(suspicious_percentage, 2),
    "%"
)


# ==============================
# OVERALL RESULT
# ==============================

if suspicious_percentage >= 50:

    print("\nRESULT: DEEPFAKE LIKELY")
    print("RISK: HIGH")

elif suspicious_percentage >= 20:

    print("\nRESULT: SUSPICIOUS")
    print("RISK: MEDIUM")

else:

    print("\nRESULT: NO STRONG MANIPULATION SIGNAL")
    print("RISK: LOW")


print(
    "\nRecommendation:"
)

if suspicious_percentage >= 20:

    print(
        "FLAGGED FOR FURTHER FORENSIC REVIEW"
    )

else:

    print(
        "No strong manipulation signal detected"
    )