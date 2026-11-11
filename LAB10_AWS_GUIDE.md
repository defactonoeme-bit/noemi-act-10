# Laboratory Activity 10 — AWS Lightsail deployment: noemi

Folder: `noemi-act-10`  ·  Partner for the AWS-to-AWS task: **Rochelle Ann** (hardcoded in app.py as http://3.0.106.1/api/students) (same pairing as Lab 9; change it if your teacher assigned someone else)

> **Nothing here has been committed or pushed.** This folder is a ready copy of the Lab 9 app plus the Lab 10 files.
> When you decide to publish, make the repo `noemi-act-10` (or reuse your existing repo) and push it yourself.

## What is in this folder

| File | Lab step | Purpose |
|---|---|---|
| `app.py`, `templates/`, `init_db.py`, `requirements.txt` | 1 | The Flask app. `requirements.txt` already has Flask, gunicorn and requests. |
| `deploy/setup_server.sh` | 4–11 | Does the server setup in one go (optional shortcut for the manual steps below). |
| `deploy/flaskapp.service` | 10 | The systemd unit for Gunicorn (reference copy, user `ubuntu`). |
| `deploy/nginx-flaskapp.conf` | 11 | The Nginx reverse-proxy site (reference copy). |
| `deploy/update_from_github.sh` | 16 | `git pull`, install requirements, restart the service. |
| `deploy/troubleshoot.sh` | 17 | The troubleshooting commands. |

## The code change for the Additional Task

In Lab 9 the partner address was a Render URL. Lab 10 needs your partner's **AWS Static IP**.
The partner address is written in `app.py` (`PARTNER_URL`), as in Lab 9, and now points to `http://3.0.106.1/api/students` (Rochelle Ann's server).
Change that one line if your partner changes, push, and run `deploy/update_from_github.sh` on the server.

## Step by step (matches the lab)

**Before AWS (Step 1)** — on your PC, in this folder, when you are ready:
```
git add .
git commit -m "Prepare application for AWS deployment"
git push
```

**Steps 2–3** — Lightsail: Create instance → Linux/Unix → OS only → Ubuntu → name it `flask-lab10-noemi` → wait for *Running* → open the browser SSH.
```
uname -a
pwd
```

**Steps 4–11 — option A, one script** (after cloning, or paste the script):
```
cd ~
git clone https://github.com/defactonoeme-bit/noemi-act-10.git
cd noemi-act-10
bash deploy/setup_server.sh https://github.com/defactonoeme-bit/noemi-act-10.git
```

**Steps 4–11 — option B, manually** (what the lab shows):
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx
cd ~ && git clone https://github.com/defactonoeme-bit/noemi-act-10.git && cd noemi-act-10
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
python init_db.py            # only if students.db is missing
gunicorn --bind 127.0.0.1:8000 app:app      # Ctrl+C to stop; test with: curl http://127.0.0.1:8000
sudo nano /etc/systemd/system/flaskapp.service    # paste deploy/flaskapp.service
sudo systemctl daemon-reload && sudo systemctl start flaskapp && sudo systemctl enable flaskapp
sudo nano /etc/nginx/sites-available/flaskapp     # paste deploy/nginx-flaskapp.conf
sudo ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled/flaskapp
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx && sudo systemctl enable nginx
```

**Step 12** — Lightsail → Networking: allow **TCP 80** (HTTP) and keep SSH. Do **not** open port 8000.

**Step 13** — open `http://YOUR-PUBLIC-IP/`, `/api/students`, `/students`.

**Step 14** — Networking → *Create static IP* → same region → attach to your instance → reopen the site with the static IP.

**Step 15–16** — send your partner only `http://YOUR-STATIC-IP/api/students`. To update after a push: `bash ~/noemi-act-10/deploy/update_from_github.sh`.

**Additional Task** — press **Retrieve Classmate's Records** (the partner `http://3.0.106.1/api/students` is already set in `app.py`; your partner is **Rochelle Ann**), retrieve, view a record, save one,
then reload and confirm the saved record is still there.

## Screenshots to submit (take them yourself, from your own AWS account)

1. Running Lightsail instance (status *Running*).
2. SSH terminal showing the project files: `ls` inside `~/noemi-act-10`.
3. `sudo systemctl status flaskapp` showing **active (running)**.
4. `sudo nginx -t` ("syntax is ok" / "test is successful") or `sudo systemctl status nginx`.
5. The Static IP (Lightsail → Networking) and the app opened at `http://YOUR-STATIC-IP/`.
6. An API endpoint through AWS, e.g. `http://YOUR-STATIC-IP/api/students`.
7. Your partner's AWS API output retrieved by your app.
8. One partner record saved, then retrieved later from your own AWS-hosted app.
9. A GitHub update pulled and redeployed (`git pull` + `systemctl restart`, then the change visible on the site).
10. *(Optional)* custom domain and HTTPS.

Also submit: the GitHub repository URL and the AWS Static IP.

## Security and cleanup

- Never put AWS keys, SSH private keys (`*.pem`), GitHub tokens or passwords in the code or the repo. `.gitignore` already skips `*.pem` and `.env`.
- Use fictional data only. Don't give classmates access to your AWS account.
- When grading is done, **stop or delete** the instance **and release the static IP** to avoid charges.
- A Lightsail disk is persistent, so unlike Render the SQLite records survive restarts. Don't re-run `init_db.py` on data you want to keep; it resets the table.
