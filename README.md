# Lab 7 — Ali Rida Awad

Pytest tests for the Flask/SQLite user application from Lab 5.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -v
```

To start the API: `python app.py`.

## Graded activity

`test_user_AliRida_Awad.py` covers first-run database creation and initial
users, insert_user, get_users, get_user_by_id, update_user, delete_user,
api_get_user, api_add_user, api_update_user, and api_delete_user.
It also tests the users list API, a missing ID, and repeat initialization.
Every API test checks HTTP status and the complete JSON response; mutation
tests independently read SQLite to confirm persistence. Function-scoped
fixtures use pytest's temporary directories so tests leave application data alone.

## Changes from Lab 5

- Added initialize_database() to create and seed the database on first startup.
  Lab 5's submitted database was empty and neither handout specified a seed
  list, so the John Doe example from the Lab 5 handout is used as initial data
  (including the handout's original email spelling). INITIAL_USERS in db.py
  documents this choice. Existing databases are preserved on later starts.
- Fixed the insert exception handler's conn().rollback() typo.
- Closed database connections after reads.
- Kept the Lab 5 endpoint paths, response JSON, and HTTP 200 behavior.

## Validation evidence

`pytest-results.txt` is captured output from a real successful pytest run.
`pytest-results.png` renders that same captured output as an image for the
requested snapshot. It is an output image, not a desktop screenshot.

The provided Lab 5 and course project environments supplied the installed
packages for local validation because downloading packages was unavailable.
The commands above work in a normal environment with package installation.
