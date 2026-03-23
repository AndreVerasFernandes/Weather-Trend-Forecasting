# Weather App (Flask) - Tech Assessment 2

Flask application with SQLite persistence, full CRUD, external API integration, and data export.

## Implemented features

- **Flexible location input**: city, postal code, landmark, etc.
- **Location validation** via Open-Meteo geocoding.
- **Date range validation** (`YYYY-MM-DD`, end date >= start date and not in the future).
- **CREATE**: creates a request and stores current weather + min/max for the selected range.
- **READ**: lists and retrieves stored records (UI and API).
- **UPDATE**: updates location/date range with revalidation and refreshed weather data.
- **DELETE**: removes records.
- **API Integration (2.2)**:
	- Open-Meteo Geocoding API
	- Open-Meteo Forecast + Archive API
	- Wikipedia REST API (place summary)
	- Google Maps link for the resolved location
- **Export (2.3)**: JSON, CSV, and Markdown.

## Stack

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- SQLite
- Requests

## How to run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Access:

- UI: `http://127.0.0.1:5000/`
- API base: `http://127.0.0.1:5000/api`

## Estrutura

```text
.
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
└── weather_app/
		├── __init__.py
		├── models.py
		├── routes.py
		└── services.py
```

## Main endpoints

### CREATE

```http
POST /api/weather-records
Content-Type: application/json

{
	"location": "Recife",
	"start_date": "2026-03-01",
	"end_date": "2026-03-10"
}
```

### READ

- `GET /api/weather-records`
- `GET /api/weather-records/<id>`

### UPDATE

```http
PUT /api/weather-records/<id>
Content-Type: application/json

{
	"location": "Olinda",
	"start_date": "2026-03-01",
	"end_date": "2026-03-12"
}
```

### DELETE

- `DELETE /api/weather-records/<id>`

### EXPORT

- `GET /api/export/json`
- `GET /api/export/csv`
- `GET /api/export/md`

## Notes

- The SQLite database (`weather.db`) is created automatically on first run.
- Validation errors return `400`.
- External API failures return `502`.