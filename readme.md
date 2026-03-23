# Weather Trend Forecasting

Monorepo with two weather applications developed during the technical assessment:

- **Tech Assessment 1 (`weather-vue`)**: Vue 3 + Vite frontend for real-time weather and 5-day forecast.
- **Tech Assessment 2 (`weather_app`)**: Flask + SQLite backend with CRUD, external API integration, and export endpoints.

## Repository structure

```text
.
├── readme.md
├── templates/
│   └── index.html
├── weather_app/
│   ├── __init__.py
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   ├── services.py
│   ├── requirements.txt
│   └── README.md
└── weather-vue/
	├── src/
	├── public/
	├── package.json
	└── README.md
```

## Prerequisites

- **Python** 3.11+
- **Node.js** 18+ (recommended: latest LTS)
- **npm** 9+

## Running each project

### 1) Backend (Flask + SQLite)

```bash
cd weather_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Available at:

- UI: `http://127.0.0.1:5000/`
- API base: `http://127.0.0.1:5000/api`

Notes:

- The SQLite database (`weather.db`) is created automatically on first run.
- Main APIs used by backend services: Open-Meteo (geocoding + forecast/archive) and Wikipedia REST.

### 2) Frontend (Vue 3 + Vite)

```bash
cd weather-vue
npm install
npm run dev
```

Available at:

- Vite dev server (typically): `http://127.0.0.1:5173/`

Production build:

```bash
npm run build
npm run preview
```

Notes:

- This frontend fetches weather data directly from Open-Meteo APIs.
- It does **not** require the Flask backend to run.

## Feature summary

### `weather-vue` (Assessment 1)

- Search by city/postal code/landmark.
- Weather from current browser location.
- Current weather card with key metrics.
- 5-day forecast (min/max, rain probability, UV, sunrise/sunset).
- Responsive layout (desktop/tablet/mobile).
- Friendly handling for invalid input and API/geolocation failures.

### `weather_app` (Assessment 2)

- Input and date-range validation.
- Full CRUD for weather records.
- Persisted records in SQLite.
- Place summary and Google Maps URL generation.
- Export endpoints in JSON, CSV, and Markdown.

## Main backend endpoints

- `POST /api/weather-records`
- `GET /api/weather-records`
- `GET /api/weather-records/<id>`
- `PUT /api/weather-records/<id>`
- `DELETE /api/weather-records/<id>`
- `GET /api/export/json`
- `GET /api/export/csv`
- `GET /api/export/md`

## Quick validation checklist

- Backend starts and serves `http://127.0.0.1:5000/`.
- Frontend starts with `npm run dev` and returns weather data.
- Backend CRUD routes return expected status codes (`201`, `200`, `400`, `502` depending on scenario).
