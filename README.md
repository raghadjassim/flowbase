# 🟢 Flowbase — Team Operating System

Flowbase is a **Django-powered team workspace platform** — a dark-themed (light mode available) hub for tasks, sticky-note brainstorming, calendars, and team collaboration. Built as a full clone of a Flowbase-style product design, re-implemented from scratch as a real, persistent, multi-user web application.

> 🇮🇶 مبني خصيصاً ليكون مناسباً للشركات التقنية والفرق التي تعمل سوية: كل مستخدم له مساحة عمل خاصة، تقدر تسوي فرق (Teams) وتسند مهام، وكل شي محفوظ بقاعدة بيانات حقيقية.

![theme](https://img.shields.io/badge/theme-dark%20%2F%20light-5be59a)
![django](https://img.shields.io/badge/Django-5.1-0c4b33)
![status](https://img.shields.io/badge/status-MVP-brightgreen)

---

## ✨ Features

- **🔐 Real authentication** — sign up / log in / log out, each new user automatically gets their own personal **Workspace**.
- **🏢 Multi-workspace support** — every user can belong to multiple workspaces (personal + team spaces), switch between them from the sidebar, and invite teammates by email.
- **👥 Teams** — group members into teams inside a workspace and quick-assign a whole team to a task.
- **✅ Kanban task boards** — create projects, drag & drop tasks between *To do / In progress / Completed* columns, set priority, due dates, and assign one or more teammates. Everything is saved via AJAX, no page reload needed to move a card.
- **📌 Focus Wall (Sticky Notes)** — the original sticky-note board experience (drag, recolor, delete, auto-rotate) rebuilt to persist every note's position, color and text to the database per workspace.
- **📅 Calendar** — a real month-view calendar tied to a workspace; create events, invite attendees, and see upcoming events on the dashboard. Invited teammates get a notification.
- **🔔 Notifications** — task assignments, event invites and workspace additions push notifications to the bell icon dropdown and the notifications page, plus a lightweight in-app reminder check for today's events.
- **🌗 Dark / Light theme** — dark by default (matches the product's brand), toggle instantly from the top bar or Settings page; preference is saved per user.
- **🗂 Real multi-page navigation** — every sidebar tab (Overview, My tasks, Projects, Focus wall, Calendar, Teams, Activity) is a distinct Django URL/page — not a single-page scroll.
- **⚙️ Settings page** — edit profile, job title, bio, notification preferences, and theme.

---

## 🧱 Tech stack

| Layer | Choice |
|---|---|
| Backend | Django 5.1 (Python) |
| Database | SQLite (default, dev) — trivially swappable to PostgreSQL for production |
| Frontend | Django templates + vanilla JS + jQuery / jQuery UI (drag & drop) |
| Styling | Hand-written CSS using CSS custom properties for instant dark/light theming |
| Auth | Django's built-in auth system with a custom `User` model |

---

## 📁 Project structure

```
flowbase_django/
├── flowbase/          # project settings, root urls
├── accounts/          # custom User model, login/signup/settings, theme toggle
├── workspaces/        # Workspace, Membership, Team, Invite + dashboard
├── boards/             # Project, Column, Task, Comment — Kanban logic
├── stickywall/         # Note model — the Focus Wall
├── events/             # Event model — the Calendar
├── notifications/      # Notification model + bell dropdown
├── templates/           # all HTML templates (base.html + one folder per app)
├── static/               # theme.css, board.css, calendar.css, stickywall.css
├── requirements.txt
└── manage.py
```

---

## 🚀 Getting started (local)

```bash
# 1. Clone
git clone https://github.com/<your-username>/flowbase.git
cd flowbase

# 2. Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. (Optional) seed demo data — creates user "test" / password "test1234"
#    with a sample workspace, project, tasks, notes and an event
python manage.py seed_demo

# 6. Create an admin account
python manage.py createsuperuser

# 7. Run the dev server
python manage.py runserver
```

Visit **http://127.0.0.1:8000** and sign up, or log in with the seeded `test` / `test1234` account.

---

## 🌐 Deploying (making it live)

Flowbase ships with `gunicorn`, `whitenoise`, and `dj-database-url` in `requirements.txt`, plus a ready-to-use `render.yaml` blueprint, so it deploys to **Render** in a few clicks.

### Option A — Render, one-click blueprint (recommended)

1. Push the repo to GitHub (see below).
2. Go to **render.com** → **New** → **Blueprint** → connect your GitHub repo.
3. Render reads `render.yaml` automatically and provisions:
   - a **free Postgres database** (`flowbase-db`)
   - a **free web service** running `gunicorn flowbase.wsgi`, with `SECRET_KEY` auto-generated and `DATABASE_URL` wired to the database automatically
4. Click **Apply** — first deploy takes a couple of minutes (it runs `collectstatic` + `migrate` automatically via the build command).
5. Once live, open a shell for the service (Render dashboard → Shell) and run:
   ```bash
   python manage.py createsuperuser
   python manage.py seed_demo   # optional demo data
   ```
6. Your app is live at `https://flowbase-xxxx.onrender.com` 🎉

### Option B — Manual setup on Render / Railway / Fly.io

1. Push the repo to GitHub.
2. Create a new **Web Service** pointing at your repo.
3. **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
4. **Start Command**: `gunicorn flowbase.wsgi`
5. Environment variables:
   - `SECRET_KEY` — a long random string
   - `DEBUG` — `False`
   - `ALLOWED_HOSTS` — your service's domain, e.g. `.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` — `https://your-domain.onrender.com`
   - `DATABASE_URL` — from a managed Postgres add-on (falls back to SQLite if not set — fine for a demo, but SQLite resets on redeploy, so Postgres is recommended for anything you'll keep live)
6. After the first deploy, open a shell and run `python manage.py createsuperuser`.

> ⚠️ Without a `DATABASE_URL`, the app uses SQLite. That's fine for local development, but most hosts (Render included) wipe the filesystem on every redeploy, which would erase your data — so for a workspace you plan to keep live, attach a Postgres database.

---

## 📤 Pushing to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Flowbase Django app"
git branch -M main
git remote add origin https://github.com/<your-username>/flowbase.git
git push -u origin main
```

The included `.gitignore` already excludes `venv/`, `db.sqlite3`, `__pycache__/`, and other local artifacts, so your repo stays clean.

---

## 🗺 Roadmap ideas

- Real-time updates via WebSockets (Django Channels) for live kanban/notes collaboration
- Email delivery for invites and reminders (currently in-app only)
- File attachments on tasks
- Public REST API (Django REST Framework) for a future mobile app

---

## 📄 License

MIT — free to use, modify, and ship in your portfolio.
