import os


class Config(object):
    APP_NAME = os.getenv("APP_NAME", "Commentaria")
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", DATABASE_URL)
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
    if MAIL_USE_TLS.lower() in ("", "0", "f", "false"):
        MAIL_USE_TLS = False
    else:
        MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    DEV_MAIL = os.getenv("DEV_MAIL")
