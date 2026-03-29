import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "phish-detect-secret-key")
    MODEL_PATH = os.path.join(BASE_DIR, "models", "phishing_model.pkl")
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    MODEL_PATH = os.path.join(BASE_DIR, "models", "phishing_model.pkl")
