# Career Guidance API (FastAPI)

A FastAPI backend that:
- Predicts top career recommendations from user inputs using a simple ML pipeline (TF-IDF + RandomForest).
- Provides a conversational chatbot powered by Google Gemini (google-generativeai), with graceful fallback when the provider is unavailable or rate-limited.

This project is designed to be easy to run locally on Windows. It also includes smoke tests to verify the core endpoints.

---

## Features

- Endpoints
  - GET /health – service liveness
  - POST /predict – returns top 3 career recommendations
  - POST /chatbot – conversational guidance, optionally conditioned on /predict results
- ML pipeline
  - Trains on a small curated dataset; persists model to `model.pkl` on first run
  - Pipeline: TfidfVectorizer + RandomForestClassifier
- Chatbot integration
  - Uses google-generativeai (Gemini)
  - Dynamically selects an available model at runtime
  - Gracefully returns a friendly message during provider outages/quota errors (no 500)
- CORS
  - Configurable via `ALLOWED_ORIGINS`
  - If wildcard `*` is used, credentials are disabled to avoid invalid combinations
- Smoke tests
  - Validates /health, /predict, /chatbot
  - Includes negative test for empty /predict payload

---

## Project Structure

```text
minor project/
├─ api.py                # FastAPI app, ML pipeline, chatbot integration, CORS
├─ requirements.txt      # Locked dependencies
├─ smoke_test.py         # Automated smoke tests for endpoints
├─ .env.example          # Safe template for environment variables
├─ .gitignore            # Ensures .env, venv, etc. are not committed
└─ model.pkl             # (generated) trained model artifact
```

---

## Prerequisites

- Python 3.11 (recommended; wheels in requirements are for cp311)
- Windows PowerShell (commands below use pwsh)

---

## Setup (Windows, PowerShell)

1) Create and activate a virtual environment

```powershell
# Create venv
py -3.11 -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Upgrade pip (recommended)
python -m pip install --upgrade pip
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

3) Configure environment variables

- Copy `.env.example` to `.env` and set your values:

```powershell
Copy-Item .env.example .env
# then edit .env to set:
# GEMINI_API_KEY="{{GEMINI_API_KEY}}"
# ALLOWED_ORIGINS="http://localhost:3000"  # or * for development
```

Notes:
- `.gitignore` excludes `.env` so you don’t accidentally commit secrets.
- If the API key has ever been committed, rotate it in the provider console.

---

## Run the Development Server

Use python -m uvicorn to avoid PATH issues with uvicorn on Windows:

```powershell
python -m uvicorn api:app --reload
```

- App will start at: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/docs

---

## Example Requests (PowerShell)

- Health
```powershell
(Invoke-WebRequest -Uri http://127.0.0.1:8000/health).Content
```

- Predict
```powershell
$body = @{ p1='I like to build websites'; s1=@('javascript','react','css'); i2='frontend development' } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/predict -Body $body -ContentType 'application/json'
```

- Chatbot (basic)
```powershell
$body = @{ message='Hi! Can you help me explore careers?'; sessionId='demo-session' } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/chatbot -Body $body -ContentType 'application/json'
```

- Chatbot with recommendations
```powershell
$predictBody = @{ p1='I enjoy data and ML'; s1=@('python','pandas','sklearn'); i2='machine learning' } | ConvertTo-Json -Depth 5
$pred = Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/predict -Body $predictBody -ContentType 'application/json'
$chatBody = @{ message='Given these recommendations, what should I learn next?'; sessionId='demo-session-2'; recommendations=$pred.recommendations } | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/chatbot -Body $chatBody -ContentType 'application/json'
```

---

## Automated Smoke Tests

Run the bundled smoke tests without starting a server (they use TestClient):

```powershell
& "$PWD\minor project\venv\Scripts\python.exe" "$PWD\minor project\smoke_test.py"
```

Expected output includes:
- health: ok
- predict: returns 3 recommendations
- predict_empty: ok (400 on empty)
- chatbot: ok (live or friendly fallback)

---

## Implementation Notes

- ML Model
  - Trains on first startup if `model.pkl` does not exist.
  - Pipeline: `TfidfVectorizer(ngram_range=(1,2))` + `RandomForestClassifier(n_estimators=200, random_state=42)`.
  - Predictions: top-3 classes by probability, merged with `CAREER_DETAILS` (now curated for all labels) with safe defaults as fallback.

- Chatbot
  - Uses `google.generativeai` with runtime model selection from `list_models()` (filters for `generateContent`).
  - If provider returns errors (quota/network), endpoint responds with a friendly message instead of 500.

- CORS
  - `ALLOWED_ORIGINS` controls origins (comma-separated).
  - If `*`, `allow_credentials` is disabled to avoid invalid wildcard+credentials combo.

- Security
  - `.env` is ignored by git.
  - A `.env.example` template is provided.
  - Rotate keys if they were ever committed or shared.

---

## Troubleshooting

- "uvicorn is not recognized"
  - Use: `python -m uvicorn api:app --reload`

- `ModuleNotFoundError: google.generativeai`
  - Ensure you’re in the venv and run: `pip install -r requirements.txt`

- `/chatbot` 500 errors
  - Missing `GEMINI_API_KEY` -> endpoint will respond with a clear message.
  - Quota/Network/provider 4xx/5xx -> endpoint returns friendly fallback; check Gemini quota or try later.

- `/predict` 500 errors
  - Addressed by ensuring all recommendation fields exist; also fixed `classes_` lookup from the final estimator in the pipeline.

- Dependency issues
  - Run: `python -m pip check` (should say: No broken requirements found.)

---

## Exact Commands (Copy/Paste)

- Create venv, activate, install
```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- Set up environment
```powershell
Copy-Item .env.example .env
# Edit .env:
# GEMINI_API_KEY="<your key>"
# ALLOWED_ORIGINS="*"  # or your frontend origin
```

- Run the server
```powershell
python -m uvicorn api:app --reload
```

- Run smoke tests
```powershell
& "$PWD\minor project\venv\Scripts\python.exe" "$PWD\minor project\smoke_test.py"
```

---

## License

This project is provided as-is for educational purposes.
