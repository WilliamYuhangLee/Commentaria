from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_migrate import Migrate
import cloudinary

from commentaria import configs

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"  # which function to login
login_manager.login_message_category = "info"  # set login message style (Bootstrap)
mail = Mail()
moment = Moment()
migrate = Migrate()


# Application Factory
def create_app(config="Config"):
    app = Flask(__name__)
    app.config.from_object(configs.__name__ + "." + config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    migrate.init_app(app, db)

    cloudinary.config(cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
                      api_key=app.config["CLOUDINARY_API_KEY"],
                      api_secret=app.config["CLOUDINARY_SECRET"])

    from commentaria.users.routes import users
    from commentaria.posts.routes import posts
    from commentaria.main.routes import main
    from commentaria.errors.handler import errors

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    from commentaria.context_processor import import_context_processor
    import_context_processor(app)

    return app
