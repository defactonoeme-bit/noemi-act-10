# noemi-act-9 — Laboratory Activities 7, 8 and 9

Flask + SQLite student app with a Kanban-board interface.

- **Lab 7:** `init_db.py` creates `students.db`; `/students`, `/students/<id>`, `/students/filter?program=|year=|section=`; try them in the Explorer panel.
- **Lab 8:** CRUD cards, search, details, and classmate records shown in their own column.
- **Lab 9:** `/partner-records`, `/import-student`, `/send-record`, `source` labels; "Save →" moves a partner card into Imported.

## Run locally
    pip install -r requirements.txt
    python init_db.py
    python app.py

## Render
Build: `pip install -r requirements.txt`   Start: `gunicorn app:app`

Testing two apps on one PC: set `ALLOW_LOCAL_PARTNER=1` (leave it unset on Render).

Use fictional data only.

## Laboratory Activity 10 (AWS Lightsail)
See `LAB10_AWS_GUIDE.md` and the `deploy/` folder. The partner box now accepts an AWS Static IP or domain ending in `/api/students`.
