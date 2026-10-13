import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///wealthpulse.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_REGISTERABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    SECURITY_TOKEN_MAX_AGE = 60 * 60 * 24 * 7
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class ProductionConfig(Config):
    DEBUG = False


def selected_config():
    environment = os.getenv("APP_ENV", "development").lower()
    if environment == "production":
        if not os.getenv("SECRET_KEY") or not os.getenv("SECURITY_PASSWORD_SALT"):
            raise RuntimeError("Production requires SECRET_KEY and SECURITY_PASSWORD_SALT")
        return ProductionConfig
    if environment == "testing":
        return TestingConfig
    return DevelopmentConfig