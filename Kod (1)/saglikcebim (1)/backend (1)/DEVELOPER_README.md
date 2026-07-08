# Developer Notes

## Run

From `backend (1)`:

```powershell
uvicorn app.main:app --reload
```

The live API should be reached at `http://127.0.0.1:8000`.

## Smoke Tests

```powershell
python test_e2e_detailed.py
python test_e2e_final.py
```

## Logs

Runtime traces are written to `backend_logs/`.

- `upload_trace.log` records report uploads.
- `token_trace.log` records auth token checks.

## Monitoring

- `GET /reports/monitoring` returns KPI and trend data.
- `GET /reports/trends/{test_name}` returns per-test history.
- `GET /reports/available-tests` lists known tests for the current user.

## Notes

- Use `127.0.0.1` in local smoke tests so requests hit the live uvicorn instance.
- The report and radiology flows now persist to the SQLite database used by the backend.