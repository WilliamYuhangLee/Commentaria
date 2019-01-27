import os


class Config(object):
    APP_NAME = "Commentaria"
    SECRET_KEY = "835c9d467dfb46b00af5a442c8c4a90f"
    DATABASE_URL = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", DATABASE_URL)


app_config = Config()
