from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

APP_NAME = "Commentaria"

app = Flask(APP_NAME)

app.config["SECRET_KEY"] = "835c9d467dfb46b00af5a442c8c4a90f"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/commentaria"

db = SQLAlchemy(app)


# Data models
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship("posts", backref="author", lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.profile_picture}')"


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


posts = [
    {
        "author": "William Lee",
        "title": "First Post",
        "content": "First post!",
        "date_posted": "Jan 1, 2018"
    },
    {
        "author": "William Lee",
        "title": "Second Post",
        "content": "Second post!",
        "date_posted": "Jan 2, 2018"
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/registration", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", category="success")
        return redirect(url_for("home"))
    return render_template("registration.html", title="Join "+APP_NAME, app_name=APP_NAME, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Simulate successful login
        if form.email.data == "admin@gmail.com" and form.password.data == "admin":
            flash("You have been logged in!", category="success")
            return redirect(url_for("home"))
        else:
            flash("Login failed. Please check your username and password", category="danger")
    return render_template("login.html", title="Sign in to "+APP_NAME, app_name=APP_NAME, form=form)


if __name__ == "__main__":
    app.run()
