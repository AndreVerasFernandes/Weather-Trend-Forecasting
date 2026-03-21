# Tech Assessment 1 - Weather App (Vue)

Frontend app built with Vue 3 + Vite to fetch real-time weather data and display a 5-day forecast.

## How to run

```bash
cd weather-vue
npm install
npm run dev
```

Production build:

```bash
npm run build
```

## Delivered features

- Text-based location search (city, postal code, neighborhood, landmark).
- Weather based on the user's current location via browser geolocation.
- Current weather display with relevant metrics:
	- Temperature
	- Feels-like temperature
	- Humidity
	- Precipitation
	- Wind speed
- 5-day forecast including:
	- Daily minimum and maximum
	- Rain probability
	- UV index
	- Sunrise and sunset
- Weather icons (emoji mapped from WMO weather codes) for better readability.
- "What to consider beyond temperature" section with contextual tips (high UV, wind, rain, etc.).

## APIs used

- Open-Meteo Geocoding API (text search):
	- `https://geocoding-api.open-meteo.com/v1/search`
- Open-Meteo Reverse Geocoding API (coordinates -> place):
	- `https://geocoding-api.open-meteo.com/v1/reverse`
- Open-Meteo Forecast API (current weather + 5-day forecast):
	- `https://api.open-meteo.com/v1/forecast`

## Responsiveness (desktop, tablet, mobile)

Applied techniques:

- CSS Grid layout with progressive breakpoints.
- Forecast cards with adaptive columns:
	- Desktop: 5 columns
	- Tablet: 3 columns
	- Mobile: 2 columns, then 1 column on smaller screens
- Search form buttons stack vertically on mobile.
- Fluid widths using `min()`, `clamp()`, and relative units.

## Error handling (1.2)

Implemented examples:

- Location not found.
- API request failure.
- Empty location input.
- Geolocation permission denied or unavailable.

Messages are shown to users gracefully without breaking the app.
