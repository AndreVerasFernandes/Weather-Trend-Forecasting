from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class WeatherRequest(db.Model):
    __tablename__ = "weather_requests"

    id = db.Column(db.Integer, primary_key=True)
    input_location = db.Column(db.String(200), nullable=False)
    resolved_location = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    current_temperature_c = db.Column(db.Float, nullable=True)
    current_wind_speed = db.Column(db.Float, nullable=True)
    temperature_min_c = db.Column(db.Float, nullable=True)
    temperature_max_c = db.Column(db.Float, nullable=True)
    map_url = db.Column(db.String(500), nullable=True)
    place_summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "input_location": self.input_location,
            "resolved_location": self.resolved_location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "current_temperature_c": self.current_temperature_c,
            "current_wind_speed": self.current_wind_speed,
            "temperature_min_c": self.temperature_min_c,
            "temperature_max_c": self.temperature_max_c,
            "map_url": self.map_url,
            "place_summary": self.place_summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
