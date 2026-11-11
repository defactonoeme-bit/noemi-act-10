import os
import sqlite3
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


# ==============================
# PARTNER API (HARDCODED)
# ==============================
# Laboratory Activities 8 and 9 use ONE classmate's deployed API. The address is written
# here in the code (not typed on the web page). Change this one line if your partner changes.
# PARTNER_API_URL is only for testing on one PC; leave it unset on Render.

PARTNER_URL = os.environ.get(
    "PARTNER_API_URL",
    "http://3.0.106.1/api/students"
)


# ==============================
# DATABASE CONNECTION
# ==============================

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# A database created in Laboratory Activity 7 has no "source" column. Add it once (Activity 9).
def ensure_source_column():
    conn = get_db_connection()

    columns = [c['name'] for c in conn.execute('PRAGMA table_info(students)')]

    if columns and 'source' not in columns:
        conn.execute("ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'")
        conn.execute("UPDATE students SET source = 'Local' WHERE source IS NULL")
        conn.commit()

    conn.close()


ensure_source_column()


# Check a student sent from the web page or from a partner system.
def clean_student(data):
    if not isinstance(data, dict):
        return None, 'Send the student information as JSON.'

    for field in ['student_id', 'name', 'program', 'year', 'section']:
        if str(data.get(field, '')).strip() == '':
            return None, field + ' is required.'

    try:
        year = int(data['year'])
    except (TypeError, ValueError):
        return None, 'Year must be a number.'

    if year < 1:
        return None, 'Year must be 1 or more.'

    return {
        'student_id': str(data['student_id']).strip(),
        'name': str(data['name']).strip(),
        'program': str(data['program']).strip(),
        'year': year,
        'section': str(data['section']).strip()
    }, None


# ==============================
# HOME PAGE
# ==============================

@app.route('/')
def home():
    return render_template(
        'index.html',
        partner_host=urlparse(PARTNER_URL).hostname
    )


# ==============================
# EXISTING STUDENT API
# ==============================

@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00102",
        "name": "Noeme Defacto",
        "program": "BSIT",
        "year": 3,
        "section": "Dijsktra"
    })


# ==============================
# GREETING API
# ==============================

@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')

    return jsonify({
        "message": f"Hello, {name}!"
    })


# ==============================
# CUSTOM COURSE API
# ==============================

@app.route('/course')
def get_course():
    return jsonify({
        "course_code": "IT 3120",
        "course_title": "System Integration",
        "instructor": "Dr. Rene Arduo"
    })


# ==============================
# DATABASE API
# GET ALL STUDENTS
# ==============================

@app.route('/students')
def get_students():
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students'
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# ==============================
# DATABASE API
# GET ONE STUDENT BY ID
# ==============================

@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify(dict(student))


# ==============================
# ADDITIONAL DATABASE API
# GET STUDENTS BY PROGRAM
# ==============================

@app.route('/students/program/<program>')
def get_students_by_program(program):
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students WHERE program = ?',
        (program,)
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# ==============================
# LABORATORY ACTIVITY 8
# CRUD API (CREATE, READ, UPDATE, DELETE)
# ==============================

# CREATE: a record sent without a source is labelled "External API" (Activity 9, Step 8).
# The web page always sends "Local" for records you add yourself.

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json(silent=True)

    student, error = clean_student(data)

    if error:
        return jsonify({"error": error}), 400

    source = str(data.get('source') or 'External API').strip()

    conn = get_db_connection()

    cursor = conn.execute(
        """INSERT INTO students
        (student_id, name, program, year, section, source)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (student['student_id'], student['name'], student['program'],
         student['year'], student['section'], source)
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Student added", "id": new_id}), 201


# READ: all practice records (this is the read-only endpoint your classmate uses)

@app.route('/api/students', methods=['GET'])
def api_students():
    conn = get_db_connection()

    rows = conn.execute('SELECT * FROM students').fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


# READ: one record

@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# UPDATE (the source label is not changed)

@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    student, error = clean_student(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    cursor = conn.execute(
        """UPDATE students SET student_id=?, name=?, program=?,
        year=?, section=? WHERE id=?""",
        (student['student_id'], student['name'], student['program'],
         student['year'], student['section'], id)
    )

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student updated"})


# DELETE

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()

    cursor = conn.execute('DELETE FROM students WHERE id = ?', (id,))

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted"})


# ==============================
# LABORATORY ACTIVITY 9
# SYSTEM-TO-SYSTEM INTEGRATION
# (the partner address is the hardcoded PARTNER_URL at the top of this file)
# ==============================

# VIEW: retrieve the partner's records through this server (avoids browser CORS limits)

@app.route('/partner-records')
def partner_records():
    try:
        response = requests.get(PARTNER_URL, timeout=15, allow_redirects=False)
        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError):
        return jsonify({"error": "Unable to retrieve partner data"}), 502

    if not isinstance(data, list):
        return jsonify({"error": "Unable to retrieve partner data"}), 502

    return jsonify(data)


# SAVE: store one selected partner record in my own database

@app.route('/import-student', methods=['POST'])
def import_student():
    student, error = clean_student(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    conn.execute(
        """INSERT INTO students
        (student_id, name, program, year, section, source)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (student['student_id'], student['name'], student['program'],
         student['year'], student['section'], 'Classmate API')
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Remote record saved"}), 201


# SEND: post one practice record to the partner's POST /api/students endpoint

@app.route('/send-record', methods=['POST'])
def send_record():
    body = request.get_json(silent=True) or {}

    student, error = clean_student(body.get('record'))

    if error:
        return jsonify({"error": error}), 400

    student['source'] = 'Partner API'

    try:
        response = requests.post(
            PARTNER_URL, json=student, timeout=15, allow_redirects=False
        )

    except requests.RequestException:
        return jsonify({"error": "Unable to reach the partner API"}), 502

    result = {
        "partner_status": response.status_code,
        "partner_response": response.text,
        "sent": student
    }

    if response.status_code >= 400:
        result["error"] = ("Partner replied " + str(response.status_code) +
                           ": " + response.text[:200])
        return jsonify(result), response.status_code

    return jsonify(result)


# ==============================
# RUN APPLICATION
# ==============================

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )