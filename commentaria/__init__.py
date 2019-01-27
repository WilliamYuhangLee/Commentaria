from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config.update(
    APP_NAME="Commentaria",
    SECRET_KEY="835c9d467dfb46b00af5a442c8c4a90f",
    SQLALCHEMY_DATABASE_URI="postgresql://localhost/commentaria"
)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from commentaria import routes
