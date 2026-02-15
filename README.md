Python Verison should be 3.12 or less

You need save a Google service account JSON and set:
- `GOOGLE_SERVICE_ACCOUNT_FILE` (path to service account file)

Run FastAPI:

```powershell
venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn ingest_api.main:app --reload --port 8001
```

## Existing ingest endpoints
- `POST /ingest/upload`
- `POST /ingest/process`
- `GET /ingest/status/{job_id}`
- `GET /ingest/output/{job_id}`

## New job-assistant endpoints
- `POST /jobs/suggest-bullets`
  - Input: `resume_text`, `proficiencies[]`, `job_title`, `company`, `job_description`
  - Output: tailored summary, prioritized skills, and role-focused bullet suggestions.
- `POST /jobs/log-application`
  - Input: `spreadsheet_id`, `sheet_name`, `url`, `company`, `job_title`, `status`, `suggested_bullets[]`
  - Appends a row to Google Sheets.

## Browser extension (Chrome)
Files are in `browser_extension/`.

1. Open `chrome://extensions`
2. Enable `Developer mode`
3. Click `Load unpacked`
4. Select the `browser_extension` folder
5. Open extension `Settings` and fill:
   - API Base URL (e.g. `http://127.0.0.1:8001`)
   - Spreadsheet ID
   - Resume text
   - Proficiencies
6. On a job page, click `Scan Current Job` to get suggested bullets.
7. Click `Log Application` to append to Sheets.

## Publish to GitHub as private repo
I cannot authenticate to your GitHub account from here, but run:

```powershell
git init
git add .
git commit -m "Add job assistant API and browser extension"
gh repo create NLP-Automation-Application --private --source . --remote origin --push
```

If `gh` is not installed:

```powershell
git remote add origin https://github.com/<your-username>/NLP-Automation-Application.git
git branch -M main
git push -u origin main
```
