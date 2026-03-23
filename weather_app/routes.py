from __future__ import annotations

import csv
import io
from datetime import date

from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for

from .models import WeatherRequest, db
from .services import (
    ExternalAPIError,
    ValidationError,
    build_google_maps_url,
    fetch_place_summary,
    fetch_weather,
    geocode_location,
    parse_date_or_raise,
    validate_date_range,
)

main_bp = Blueprint("main", __name__)


def _serialize_rows(rows: list[WeatherRequest]) -> list[dict]:
    return [row.to_dict() for row in rows]


def _build_record(location_text: str, start: date, end: date) -> WeatherRequest:
    location = geocode_location(location_text)
    weather = fetch_weather(location.latitude, location.longitude, start, end)

    return WeatherRequest(
        input_location=location.input_location,
        resolved_location=location.resolved_location,
        latitude=location.latitude,
        longitude=location.longitude,
        start_date=start,
        end_date=end,
        current_temperature_c=weather.current_temperature_c,
        current_wind_speed=weather.current_wind_speed,
        temperature_min_c=weather.temperature_min_c,
        temperature_max_c=weather.temperature_max_c,
        map_url=build_google_maps_url(location.latitude, location.longitude),
        place_summary=fetch_place_summary(location.resolved_location),
    )


def _refresh_record(row: WeatherRequest, location_text: str, start: date, end: date) -> None:
    location = geocode_location(location_text)
    weather = fetch_weather(location.latitude, location.longitude, start, end)

    row.input_location = location.input_location
    row.resolved_location = location.resolved_location
    row.latitude = location.latitude
    row.longitude = location.longitude
    row.start_date = start
    row.end_date = end
    row.current_temperature_c = weather.current_temperature_c
    row.current_wind_speed = weather.current_wind_speed
    row.temperature_min_c = weather.temperature_min_c
    row.temperature_max_c = weather.temperature_max_c
    row.map_url = build_google_maps_url(location.latitude, location.longitude)
    row.place_summary = fetch_place_summary(location.resolved_location)


def _read_request_input() -> tuple[str, date, date]:
    source = request.get_json(silent=True) if request.is_json else request.form

    location_text = (source.get("location") or "").strip()
    start_date_raw = (source.get("start_date") or "").strip()
    end_date_raw = (source.get("end_date") or "").strip()

    start = parse_date_or_raise(start_date_raw, "start_date")
    end = parse_date_or_raise(end_date_raw, "end_date")
    validate_date_range(start, end)

    return location_text, start, end


def _json_error(message: str, status: int) -> tuple[Response, int]:
    return jsonify({"error": message}), status


@main_bp.get("/")
def home() -> str:
    rows = WeatherRequest.query.order_by(WeatherRequest.created_at.desc()).all()
    message = request.args.get("message")
    error = request.args.get("error")
    return render_template("index.html", rows=rows, message=message, error=error)


@main_bp.post("/ui/create")
def create_ui() -> Response:
    try:
        location_text, start, end = _read_request_input()
        row = _build_record(location_text, start, end)
        db.session.add(row)
        db.session.commit()
        return redirect(url_for("main.home", message="Record created successfully."))
    except (ValidationError, ExternalAPIError) as exc:
        return redirect(url_for("main.home", error=str(exc)))


@main_bp.post("/ui/<int:row_id>/update")
def update_ui(row_id: int) -> Response:
    row = WeatherRequest.query.get_or_404(row_id)
    try:
        location_text, start, end = _read_request_input()
        _refresh_record(row, location_text, start, end)
        db.session.commit()
        return redirect(url_for("main.home", message=f"Record {row_id} updated."))
    except (ValidationError, ExternalAPIError) as exc:
        return redirect(url_for("main.home", error=str(exc)))


@main_bp.post("/ui/<int:row_id>/delete")
def delete_ui(row_id: int) -> Response:
    row = WeatherRequest.query.get_or_404(row_id)
    db.session.delete(row)
    db.session.commit()
    return redirect(url_for("main.home", message=f"Record {row_id} removed."))


@main_bp.post("/api/weather-records")
def create_record() -> tuple[Response, int]:
    try:
        location_text, start, end = _read_request_input()
        row = _build_record(location_text, start, end)
        db.session.add(row)
        db.session.commit()
        return jsonify(row.to_dict()), 201
    except ValidationError as exc:
        return _json_error(str(exc), 400)
    except ExternalAPIError as exc:
        return _json_error(str(exc), 502)


@main_bp.get("/api/weather-records")
def list_records() -> Response:
    rows = WeatherRequest.query.order_by(WeatherRequest.created_at.desc()).all()
    return jsonify(_serialize_rows(rows))


@main_bp.get("/api/weather-records/<int:row_id>")
def get_record(row_id: int) -> Response:
    row = WeatherRequest.query.get_or_404(row_id)
    return jsonify(row.to_dict())


@main_bp.put("/api/weather-records/<int:row_id>")
def update_record(row_id: int) -> Response:
    row = WeatherRequest.query.get_or_404(row_id)
    try:
        location_text, start, end = _read_request_input()
        _refresh_record(row, location_text, start, end)
        db.session.commit()
        return jsonify(row.to_dict())
    except ValidationError as exc:
        return _json_error(str(exc), 400)
    except ExternalAPIError as exc:
        return _json_error(str(exc), 502)


@main_bp.delete("/api/weather-records/<int:row_id>")
def delete_record(row_id: int) -> tuple[Response, int]:
    row = WeatherRequest.query.get_or_404(row_id)
    db.session.delete(row)
    db.session.commit()
    return jsonify({"message": f"Record {row_id} deleted."}), 200


@main_bp.get("/api/export/<string:format_name>")
def export_data(format_name: str) -> Response:
    rows = WeatherRequest.query.order_by(WeatherRequest.created_at.desc()).all()
    payload = _serialize_rows(rows)

    if format_name == "json":
        return jsonify(payload)

    if format_name == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=payload[0].keys() if payload else ["id"])
        writer.writeheader()
        writer.writerows(payload)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=weather_export.csv"},
        )

    if format_name == "md":
        headers = [
            "id",
            "input_location",
            "resolved_location",
            "start_date",
            "end_date",
            "current_temperature_c",
            "temperature_min_c",
            "temperature_max_c",
        ]
        lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
        for row in payload:
            lines.append("| " + " | ".join(str(row.get(column, "")) for column in headers) + " |")
        return Response(
            "\n".join(lines),
            mimetype="text/markdown",
            headers={"Content-Disposition": "attachment; filename=weather_export.md"},
        )

    return Response("Unsupported format. Use json, csv, or md.", status=400)
