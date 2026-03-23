from flask import Flask

from .models import db
from .routes import main_bp


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///weather.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(main_bp)
    return app
