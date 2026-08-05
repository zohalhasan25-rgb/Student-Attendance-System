import cv2
import sqlite3
from datetime import datetime

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def mark_attendance(student_id, name):
    if name == "Unknown":
        return

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Get student's latest attendance
    cursor.execute("""
        SELECT date, time
        FROM attendance
        WHERE student_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (student_id,))

    last = cursor.fetchone()

    allow_attendance = True

    if last:
        last_datetime = datetime.strptime(
            last[0] + " " + last[1],
            "%Y-%m-%d %H:%M:%S"
        )

        difference = now - last_datetime

        # Don't mark again until 50 minutes have passed
        if difference.total_seconds() < 50 * 60:
            allow_attendance = False
            print("Attendance already marked within last 50 minutes.")

    if allow_attendance:
        cursor.execute("""
            INSERT INTO attendance
            (student_id, name, date, time)
            VALUES (?, ?, ?, ?)
        """, (student_id, name, date, time))

        conn.commit()
        print(f"NEW ATTENDANCE MARKED: {name} at {time}")

    conn.close()

    
def get_student_name(student_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM students WHERE id=?",
        (student_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]

    return "Unknown"

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("Camera started.")
print("Press Q to close the camera.")

while True:
    ret, frame = camera.read()

    if not ret:
        print("Could not read camera.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100, 100)
    )

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]

        student_id, confidence = recognizer.predict(face)

        if confidence < 80:
            name = get_student_name(student_id)

            if name != "Unknown":
                mark_attendance(student_id, name)
        else:
            name = "Unknown"

        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            (0, 255, 0),
            2
        )

        if name != "Unknown":
            text = f"{name} | ID: {student_id}"
        else:
            text = "Unknown"

        cv2.putText(
            frame,
            text,
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    cv2.imshow("Face Recognition Attendance", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()