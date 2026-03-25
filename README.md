# Content Monitoring & Flagging System

A Django REST API backend that monitors content for keyword matches, scores them, and supports a human review workflow with suppression rules.

---

## Assignment Requirements Implemented

| Requirement | Status |
|---|---|
| Keyword model (name field) | ✅ |
| ContentItem model (title, source, body, last_updated) | ✅ |
| Flag model (keyword, content_item, score, status) | ✅ |
| POST /keywords/ — Create keyword | ✅ |
| POST /scan/ — Trigger scan | ✅ |
| GET /flags/ — List flags | ✅ |
| PATCH /flags/{id}/ — Update review status | ✅ |
| Scoring logic (100 / 70 / 40) | ✅ |
| Suppression logic | ✅ |
| Deduplication (unique_together) | ✅ (Bonus) |
| Mock data loading | ✅ |

---

## Tech Stack

- **Python 3.10+**
- **Django 4.2**
- **Django REST Framework 3.14**
- **SQLite** (default, no setup needed)

---

## Content Source

This project uses a **local mock JSON dataset** (Alternative Option from assignment).

Mock articles are loaded via `POST /scan/load-mock/` into the database.

The mock data includes 8 articles covering topics like Django, Python, automation, and data pipelines — which match the example keywords in the assignment.

---

## Project Structure

```
content-monitor-api/
│
├── core/                  ← Django settings and main URLs
│   ├── settings.py
│   └── urls.py
│
├── keywords/              ← Keyword model + POST /keywords/ endpoint
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── content/               ← ContentItem model
│   ├── models.py
│   ├── serializers.py
│   └── views.py
│
├── flags/                 ← Flag model + GET /flags/ + PATCH /flags/{id}/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── scanner/               ← Business logic (scoring + suppression)
│   ├── services.py        ← Core logic lives here (NOT in views)
│   ├── views.py
│   └── urls.py
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### Step 1: Clone the repo

```bash
git clone https://github.com/yourusername/content-monitor-api.git
cd content-monitor-api
```

### Step 2: Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run migrations

```bash
python manage.py migrate
```

### Step 5: Start the server

```bash
python manage.py runserver
```

Server runs at: **http://127.0.0.1:8000/**

---

## API Usage — Curl Commands

### 1. Create Keywords (POST /keywords/)

```bash
curl -X POST http://127.0.0.1:8000/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"name": "python"}'

curl -X POST http://127.0.0.1:8000/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"name": "django"}'

curl -X POST http://127.0.0.1:8000/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"name": "automation"}'

curl -X POST http://127.0.0.1:8000/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"name": "data pipeline"}'
```

**Response:**
```json
{
  "message": "Keyword created successfully",
  "keyword": {
    "id": 1,
    "name": "python",
    "created_at": "2026-03-22T10:00:00Z"
  }
}
```

---

### 2. Load Mock Data (POST /scan/load-mock/)

```bash
curl -X POST http://127.0.0.1:8000/scan/load-mock/
```

**Response:**
```json
{
  "status": "success",
  "message": "Mock data loaded into ContentItem table",
  "created": 8,
  "already_existed": 0,
  "total": 8
}
```

---

### 3. Run Scan (POST /scan/)

```bash
curl -X POST http://127.0.0.1:8000/scan/
```

**Response:**
```json
{
  "status": "success",
  "message": "Scan completed",
  "keywords_scanned": 4,
  "content_items_scanned": 8,
  "flags_created_or_updated": 10,
  "flags_suppressed": 0
}
```

---

### 4. List Flags (GET /flags/)

```bash
curl http://127.0.0.1:8000/flags/
```

**Response:**
```json
[
  {
    "id": 1,
    "keyword": 1,
    "keyword_name": "django",
    "content_item": 1,
    "content_title": "Learn Django Fast",
    "content_source": "mock",
    "score": 100,
    "status": "pending",
    "reviewed_at": null,
    "created_at": "2026-03-22T10:05:00Z",
    "updated_at": "2026-03-22T10:05:00Z"
  }
]
```

---

### 5. Update Flag Status — PATCH /flags/{id}/

#### Mark as Relevant
```bash
curl -X PATCH http://127.0.0.1:8000/flags/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "relevant"}'
```

#### Mark as Irrelevant (triggers suppression)
```bash
curl -X PATCH http://127.0.0.1:8000/flags/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "irrelevant"}'
```

#### Reset to Pending
```bash
curl -X PATCH http://127.0.0.1:8000/flags/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "pending"}'
```

---

## Scoring Logic

```
Exact keyword == full title   → Score 100
Keyword is part of title      → Score 70
Keyword found only in body    → Score 40
No match                      → Score 0 (no flag created)
```

**Example:**
- Keyword: `django`
- Title: `"Learn Django Fast"` → partial match → Score **70**
- Title: `"Django REST Framework Tutorial"` → partial match → Score **70**
- Title: `"django"` → exact match → Score **100**

---

## Suppression Logic

This is the most important business rule in the system.

**Rule:** If a flag is marked `irrelevant`, it will NOT reappear on the next scan — **unless** the content item's `last_updated` timestamp has changed.

**How it works:**

```
1. Reviewer marks flag as 'irrelevant'
   → flag.reviewed_at = now()

2. Next scan runs:
   → Check: is there an existing 'irrelevant' flag?
   → YES → Compare content_item.last_updated vs flag.reviewed_at
   → If last_updated > reviewed_at → Content changed! Reset flag to 'pending'
   → If last_updated <= reviewed_at → Content same, stay suppressed
```

**Assumption made:** `last_updated` is treated as the single source of truth for whether content has changed. We do not compare body/title content directly.

---

## Assumptions & Trade-offs

1. **Mock data used** instead of a live API (Alternative Option from assignment). The mock dataset covers the example keywords: python, django, automation, data pipeline.

2. **Case-insensitive matching**: All matching is done in lowercase to avoid missing `Django` vs `django`.

3. **Deduplication via unique_together**: One flag per (keyword, content_item) pair. This is a bonus requirement from the PDF.

4. **Score is recalculated on each scan** but only updated if the flag is not suppressed.

5. **SQLite** is used for simplicity as recommended in the assignment.

6. **No authentication** is implemented — this is a simplified backend per the assignment scope.

---

## Bonus Features Implemented

- ✅ **Deduplication** — `unique_together` on Flag model prevents duplicate flags
- ✅ **Service layer** — All business logic is in `scanner/services.py`, not in views
- ✅ **Mock data loader** — Separate endpoint `POST /scan/load-mock/`
