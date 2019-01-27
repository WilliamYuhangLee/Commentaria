from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required

from commentaria import app, db, bcrypt
from commentaria.forms import RegistrationForm, LoginForm
from commentaria.models import User, Post

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

# Local parameters for use
APP_NAME = app.config["APP_NAME"]


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/registration", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Your account has been created! You are now logged in.", category="success")
        return redirect(url_for("home"))
    return render_template("registration.html", title="Join "+APP_NAME, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next") # check if there is pending request
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for("home"))
        else:
            flash("Login failed. Please check your email and password", category="danger")
    return render_template("login.html", title="Sign in to "+APP_NAME, form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account")
