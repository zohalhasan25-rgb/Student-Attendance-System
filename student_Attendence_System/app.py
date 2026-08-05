from flask import Flask, render_template, request
import sqlite3
import database
import subprocess
import os
import sys
import cv2
import numpy as np
import base64
from datetime import datetime
from flask import jsonify
from flask import redirect,url_for


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        branch = request.form["branch"]
        year = request.form["year"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO students(name, roll, branch) VALUES(?,?,?)",
            (name, roll, branch)
        )

        conn.commit()
        conn.close()

        return "<h2>Student Registered Successfully!</h2><a href='/'>Home</a>"

    return render_template("register.html")
@app.route("/students")
def students():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    data = cur.fetchall()

    conn.close()

    return render_template("students.html", students=data)

@app.route("/attendance")
def attendance():
    return render_template("attendance.html")

@app.route("/recognize-face", methods=["POST"])
def recognize_face():
    try:
        data = request.get_json()
        image_data = data["image"].split(",")[1]

        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )

        if len(faces) == 0:
            return jsonify({
                "success": False,
                "message": "No face detected"
            })

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("trainer.yml")

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]

            student_id, confidence = recognizer.predict(face)

            if confidence < 80:
                conn = sqlite3.connect("database.db")
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT name FROM students WHERE id=?",
                    (student_id,)
                )

                student = cursor.fetchone()

                if student:
                    name = student[0]

                    now = datetime.now()
                    date = now.strftime("%Y-%m-%d")
                    time = now.strftime("%H:%M:%S")

                    cursor.execute("""
                        SELECT date, time
                        FROM attendance
                        WHERE student_id=?
                        ORDER BY id DESC
                        LIMIT 1
                    """, (student_id,))

                    last = cursor.fetchone()

                    if last:
                        last_datetime = datetime.strptime(
                            last[0] + " " + last[1],
                            "%Y-%m-%d %H:%M:%S"
                        )

                        difference = now - last_datetime

                        if difference.total_seconds() < 50 * 60:
                            conn.close()
                            return jsonify({
                                "success": False,
                                "message": f"Recogized:{name} | ID: {student_id} | Attendance already marked within last 50 minutes"
                            })

                    cursor.execute("""
                        INSERT INTO attendance
                        (student_id, name, date, time)
                        VALUES (?, ?, ?, ?)
                    """, (student_id, name, date, time))

                    conn.commit()
                    conn.close()

                    return jsonify({
                        "success": True,
                        "message": f"Attendance marked for {name} | ID: {student_id}"
                    })

        return jsonify({
            "success": False,
            "message": "Face not recognized"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        })

@app.route("/report")
def report():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance")
    records = cursor.fetchall()

    conn.close()

    return render_template("attendance_report.html", records=records)

if __name__ == "__main__":
    app.run(debug=True)
    