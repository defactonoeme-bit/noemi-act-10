import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
''')

# A database made in Laboratory Activity 7 has no source column yet (Activity 9 adds it).
columns = [row[1] for row in cursor.execute("PRAGMA table_info(students)")]
if 'source' not in columns:
    cursor.execute("ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'")

cursor.execute("DELETE FROM students")
cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'students'")

# Different programs, year levels and sections, so every filter has something to show.
students = [
    ('2026-00101', 'Ruby Joy Molina', 'BSIT', 3, 'B', 'Local'),
    ('2026-00102', 'Seth Palec', 'BSIT', 3, 'A', 'Local'),
    ('2026-00103', 'Sharmaine Palencia', 'BSCS', 2, 'B', 'Local'),
    ('2026-00104', 'Rochelle Ann Paclibar', 'BSIT', 3, 'B', 'Local'),
    ('2026-00105', 'Francine Escultura', 'BSCS', 2, 'A', 'Local'),
]

cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section, source)
VALUES (?, ?, ?, ?, ?, ?)
''', students)

conn.commit()
conn.close()

print("Database created successfully.")
