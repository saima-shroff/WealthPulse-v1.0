from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import event

from app.extensions import db, security as security_extension
from app.security import user_datastore
from config import selected_config


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object or selected_config())
    db.init_app(app)
    security_extension.init_app(app, user_datastore)
    CORS(app, resources={r"/api/*": {"origins": app.config.get("FRONTEND_ORIGIN", "http://localhost:5173")}})

    @security_extension.unauthn_handler
    def unauthenticated(_mechanisms, headers=None):
        response = jsonify({"error": "Authentication required."})
        response.status_code = 401
        response.headers.update(headers or {})
        return response

    from app.api import api

    app.register_blueprint(api)

    with app.app_context():
        if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
            def enable_sqlite_foreign_keys(connection, _record):
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            event.listen(db.engine, "connect", enable_sqlite_foreign_keys)
        db.create_all()

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app