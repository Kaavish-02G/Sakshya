from transformers import pipeline

classifier = pipeline(
    "image-classification",
    model="dima806/deepfake_vs_real_image_detection"
)

result = classifier("0224.png.jpg")

print(result)