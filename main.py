from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
import sys

APP_NAME = "Commentaria"

app = Flask(APP_NAME)

app.config["SECRET_KEY"] = "835c9d467dfb46b00af5a442c8c4a90f"

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
