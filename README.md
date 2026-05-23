# README.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# CaseTrack — Django Backend

Django REST Framework API for task management. CaseTrack is a task management API built for the HMCTS Developer Challenge.
This version uses function-based views for clarity and simplicity.

## Features

- Create, read, update, and delete tasks
- Filter tasks by status (`todo`, `in_progress`, `done`, `overdue`)
- Stats endpoint returning live counts per category including overdue
- Overdue logic computed server-side (`due_date < now AND status != "done"`)
- Partial updates via PATCH
- Automated tests (7 cases covering CRUD, filtering, stats, and overdue logic)

## Quick Start

```bash
source env/bin/activate          # Python 3.10.5
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver       # → http://127.0.0.1:8000
```

---

## Testing

```bash
python manage.py test tasks                                      # all tests
python manage.py test tasks.tests.TaskTests.test_filter_overdue  # single test
```

After model changes:

```bash
python manage.py makemigrations && python manage.py migrate
```

---

## Project Structure

```
casetrack-backend/
├── casetrack/
│   ├── settings.py   # CORS, DB, installed apps
│   └── urls.py       # Root router — mounts tasks/ at /tasks/
└── tasks/
    ├── models.py      # Task model
    ├── serializers.py # TaskSerializer
    ├── views.py       # tasks_stats, tasks_list, task_detail
    ├── urls.py        # URL patterns for the tasks app
    └── tests.py       # APITestCase — 7 tests
```

- **Virtual environment:** `env/`
- **Database:** SQLite (`db.sqlite3`)
- **Python version:** 3.10.5 (see `.python-version`)

---

## Data Model

| Field           | Type         | Required | Notes                                               |
| --------------- | ------------ | -------- | --------------------------------------------------- |
| `id`          | integer      | auto     | Primary key                                         |
| `title`       | string (255) | yes      |                                                     |
| `description` | text         | no       | Nullable, blank allowed                             |
| `status`      | string       | yes      | Choices:`"todo"` / `"in_progress"` / `"done"` |
| `due_date`    | datetime     | no       | Nullable; accepts ISO-8601 or `YYYY-MM-DDTHH:MM`  |
| `created_at`  | datetime     | auto     | Set on creation, read-only                          |

`"overdue"` is not a status value — it is a computed filter: `due_date < now AND status != "done"`.

---

## API Endpoints

**Base URL:** `http://127.0.0.1:8000`

All successful responses (except DELETE) use this envelope:

```json
{ "message": "...", "data": { } }
```

Validation errors:

```json
{ "message": "Validation failed", "errors": { "field": ["detail"] } }
```

---

### GET /tasks/stats/

Returns counts for each category, computed in the database.

**Response — 200 OK**

```json
{
  "message": "Stats retrieved successfully",
  "data": {
    "todo": 4,
    "in_progress": 2,
    "done": 1,
    "total": 7,
    "overdue": 3
  }
}
```

---

### GET /tasks/

List tasks ordered by `created_at` ascending. Supports optional status filter.

| Query param  | Values                                                 |
| ------------ | ------------------------------------------------------ |
| `?status=` | `todo` · `in_progress` · `done` · `overdue` |

`overdue` filters: `due_date < now AND status != "done"` — handled server-side via `django.utils.timezone`.

---

### POST /tasks/

```json
{ "title": "Fix bug", "status": "todo", "description": "...", "due_date": "2026-06-01T09:00" }
```

`title` and `status` are required. Returns **201 Created**.

---

### GET /tasks//

Returns single task or **404**.

---

### PATCH /tasks//

Partial update — send only the fields to change. Returns **200 OK** or **400** on validation failure.

---

### DELETE /tasks//

Returns **204 No Content** or **404**.

---

## Architecture

- Views are **function-based** (`@api_view`). Class-based equivalents are commented out in `views.py` and `urls.py` for reference.
- `TaskSerializer` uses `partial=True` for PATCH, accepting any subset of fields.
- `due_date` input formats: `iso-8601` and `%Y-%m-%dT%H:%M`. Always returned as full ISO-8601 with `Z` suffix.
- Status choices are validated by DRF's `ChoiceField` automatically — no custom validator needed.
- URL order in `tasks/urls.py`: `stats/` is declared before `<int:pk>/` to prevent routing conflicts.

## CORS

Allowed origins (configured in `settings.py`):

```
http://localhost:5173  http://127.0.0.1:5173
http://localhost:5174  http://127.0.0.1:5174
```

These match Vite's default ports. Add new origins to `CORS_ALLOWED_ORIGINS` in `casetrack/settings.py` if needed.
