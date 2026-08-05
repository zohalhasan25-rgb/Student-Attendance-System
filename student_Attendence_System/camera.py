import cv2
import os

student_id = input("Enter Student id: ").strip()

os.makedirs("dataset", exist_ok=True)

camera = cv2.VideoCapture(0)
count = 0

if not camera.isOpened():
    print("Camera could not open!")
    exit()

print("Camera started")
print("Press C to capture photo")
print("Press Q to quit")

while True:
    ret, frame = camera.read()

    if not ret:
        print("Could not read camera.")
        break

    # Instructions camera par dikhengi
    cv2.putText(
        frame,
        f"Press C to Capture | Photos: {count}/30 | Q to Quit",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.imshow("Capture Face", frame)

    key = cv2.waitKey(10) & 0xFF

    if key == ord('c') or key == ord('C'):
        count += 1

        filename = os.path.join(
            "dataset",
            f"user.{student_id}.{count}.jpg"
        )

        cv2.imwrite(filename, frame)

        print("PHOTO SAVED:", filename)

    elif key == ord('q') or key == ord('Q'):
        break

camera.release()
cv2.destroyAllWindows()

print("Total photos captured:", count)