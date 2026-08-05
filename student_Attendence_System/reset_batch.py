import sqlite3
import os

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM attendance")
cursor.execute("DELETE FROM students")

try:
    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name IN ('students', 'attendance')"
    )
except sqlite3.OperationalError:
    pass

conn.commit()
conn.close()

dataset_folder = "dataset"

if os.path.exists(dataset_folder):
    for filename in os.listdir(dataset_folder):
        file_path = os.path.join(dataset_folder, filename)

        if os.path.isfile(file_path):
            os.remove(file_path)

if os.path.exists("trainer.yml"):
    os.remove("trainer.yml")

print("New batch reset completed!")
print("Old students deleted.")
print("Old attendance deleted.")
print("Old face photos deleted.")
print("Old trained model deleted.")
print("You can now register new students.")