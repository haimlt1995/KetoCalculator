# Keto Calculator

Full-stack keto nutrition calculator that estimates calories, macros, and weight change projections from your inputs.

## Stack
- FastAPI + Python 3.12 (uv managed)
- React + Vite
- Docker + Docker Compose
- Pytest + Ruff

## Features
- Metric and imperial inputs (normalized internally)
- BMI, BMR (Mifflin-St Jeor), and TDEE with activity multipliers
- Approximate body fat % and FFMI
- Goal-based calorie adjustment (lose ~20%, maintain, gain +20%)
- Keto macros (protein, fat, net carbs)
- Weekly weight forecast chart

## Scientific Basis (high level)
- BMI — WHO definition
- BMR — Mifflin-St Jeor equation
- TDEE — standard activity multipliers
- Weight change — ~7700 kcal per kg
- Body fat % (estimate) — BMI-based approximation
- FFMI — fat-free mass normalized by height

## Project Structure
```
KetoCalculator/
├─ backend/
│  ├─ app/
│  │  ├─ formulas/        # Calculation logic
│  │  ├─ units.py         # Metric / imperial normalization
│  │  ├─ calc.py          # Main calculation orchestrator
│  │  └─ main.py          # FastAPI entry point
│  ├─ tests/              # Pytest suite
│  ├─ Dockerfile
│  └─ pyproject.toml
├─ frontend/
│  ├─ src/                # React components
│  ├─ vite.config.js      # Dev proxy to backend
│  └─ package.json
├─ docker-compose.yml
└─ README.md
```

## Running Locally (recommended)
### Backend (FastAPI with uv)
Requirements: Python 3.12, `uv` installed.
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```
Backend available at http://localhost:8000 (Swagger UI at `/docs`).

### Frontend (Vite + React)
Requirements: Node.js (LTS), npm.
```bash
cd frontend
npm install
npm run dev -- --host
```
Frontend available at http://localhost:5173 (proxies API calls to the backend).

## Running with Docker (backend)
Build and run the API:
```bash
docker build -t keto-api ./backend
docker run --rm -p 8000:8000 keto-api
```
Or with Docker Compose (recommended):
```bash
docker compose up --build
```

## Environment Variables
Create a `.env` (not committed) for keys as needed, for example:
```
GOOGLE_API_KEY=your_key_here
```
Docker Compose automatically loads it.

## Tests & Code Quality
From `backend/`:
```bash
uv run pytest
uv run ruff format .
uv run ruff check .
```
All calculation logic is unit-tested.

## Roadmap (planned)
- LLM-generated keto meal plans
- Scientific references section
- Metric + imperial output toggle
- Mobile-responsive UI improvements
- Cloud deployment (AWS free tier)

## Disclaimer
Results are estimates for educational purposes and not medical or nutritional advice. Consult a professional for personalized guidance.
