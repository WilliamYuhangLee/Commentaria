from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

app.config.from_object("config.app_config")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"  # which function to login
login_manager.login_message_category = "info"  # set login message style (Bootstrap)
mail = Mail(app)

from commentaria import routes
