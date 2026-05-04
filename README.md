# Unicode Font Browser

Local-first Unicode and font coverage browser built with React, FastAPI, SQLite, and fontTools.

## Run Locally

Backend:

```sh
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```sh
cd frontend
npm install
npm run dev
```

Docker:

```sh
docker compose -f dockercompose.yml up --build
```

The API starts on `http://localhost:8000` and the web app starts on `http://localhost:5173`.

## Notes

On startup, the backend initializes SQLite and seeds a practical starter set of Unicode blocks when no Unicode data has been imported yet. To use official Unicode files, place `Blocks.txt` and `UnicodeData.txt` in `backend/data/unicode/` and run:

```sh
cd backend
python -m app.scripts.import_unicode_data
```

