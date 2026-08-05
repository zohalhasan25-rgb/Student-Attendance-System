import cv2
import os
import numpy as np

dataset_path = "dataset"

faces = []
labels = []

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

for filename in os.listdir(dataset_path):

    if filename.lower().endswith((".jpg", ".jpeg", ".png")):

        try:
            parts = filename.split(".")
            student_id = int(parts[1])
        except (ValueError, IndexError):
            print("Skipping:", filename)
            continue

        image_path = os.path.join(dataset_path, filename)

        image = cv2.imread(image_path)

        if image is None:
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        detected_faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )

        for (x, y, w, h) in detected_faces:
            face = gray[y:y+h, x:x+w]

            faces.append(face)
            labels.append(student_id)

if len(faces) == 0:
    print("ERROR: No faces detected!")

else:
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer.train(
        faces,
        np.array(labels)
    )

    recognizer.save("trainer.yml")

    print("Training completed successfully!")
    print("Faces trained:", len(faces))
    print("Student IDs:", sorted(set(labels)))
    print("Model saved as trainer.yml")