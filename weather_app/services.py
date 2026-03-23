from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from urllib.parse import quote

import requests

REQUEST_TIMEOUT = 10


class ValidationError(Exception):
    pass


class ExternalAPIError(Exception):
    pass


@dataclass
class LocationData:
    input_location: str
    resolved_location: str
    latitude: float
    longitude: float


@dataclass
class WeatherData:
    current_temperature_c: float | None
    current_wind_speed: float | None
    temperature_min_c: float | None
    temperature_max_c: float | None


def parse_date_or_raise(raw_date: str, field_name: str) -> date:
    try:
        return datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValidationError(f"{field_name} must be in YYYY-MM-DD format.") from exc


def validate_date_range(start_date: date, end_date: date) -> None:
    if end_date < start_date:
        raise ValidationError("end_date cannot be earlier than start_date.")
    if end_date > date.today():
        raise ValidationError("For historical date ranges, end_date must be today or earlier.")


def geocode_location(query: str) -> LocationData:
    if not query or not query.strip():
        raise ValidationError("location is required.")

    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": query.strip(), "count": 1, "language": "en", "format": "json"},
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code != 200:
        raise ExternalAPIError("Failed to query the geolocation service.")

    payload = response.json()
    results = payload.get("results") or []

    if not results:
        raise ValidationError("Location not found. Try a more specific query.")

    result = results[0]
    location_parts = [
        result.get("name"),
        result.get("admin1"),
        result.get("country"),
    ]
    resolved = ", ".join([part for part in location_parts if part])

    return LocationData(
        input_location=query.strip(),
        resolved_location=resolved,
        latitude=float(result["latitude"]),
        longitude=float(result["longitude"]),
    )


def fetch_weather(latitude: float, longitude: float, start_date: date, end_date: date) -> WeatherData:
    current_response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m",
            "timezone": "auto",
        },
        timeout=REQUEST_TIMEOUT,
    )

    if current_response.status_code != 200:
        raise ExternalAPIError("Failed to fetch current weather.")

    archive_response = requests.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": "auto",
        },
        timeout=REQUEST_TIMEOUT,
    )

    if archive_response.status_code != 200:
        raise ExternalAPIError("Failed to fetch temperature data for the selected date range.")

    current_payload = current_response.json().get("current", {})
    archive_payload = archive_response.json().get("daily", {})

    max_list = archive_payload.get("temperature_2m_max") or []
    min_list = archive_payload.get("temperature_2m_min") or []

    temperature_max = max(max_list) if max_list else None
    temperature_min = min(min_list) if min_list else None

    return WeatherData(
        current_temperature_c=current_payload.get("temperature_2m"),
        current_wind_speed=current_payload.get("wind_speed_10m"),
        temperature_min_c=temperature_min,
        temperature_max_c=temperature_max,
    )


def fetch_place_summary(place_name: str) -> str | None:
    if not place_name:
        return None

    title = quote(place_name.split(",")[0].strip())
    response = requests.get(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}",
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code != 200:
        return None

    payload: dict[str, Any] = response.json()
    return payload.get("extract")


def build_google_maps_url(latitude: float, longitude: float) -> str:
    return f"https://www.google.com/maps?q={latitude},{longitude}"
