import os, secrets

from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required

from commentaria import app, db, bcrypt
from commentaria.forms import RegistrationForm, LoginForm, UpdateAccountForm
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


def update_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename)
    file_name = random_hex + file_extension
    profile_picture_path = os.path.join(app.root_path, "static/resources/profile_pictures", file_name)
    form_picture.save(profile_picture_path)
    return file_name


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            profile_picture_file = update_profile_picture(form.profile_picture.data)
            current_user.profile_picture = profile_picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account info has been updated!", category="success")
        return redirect(url_for("account")) # Post-Redirect-Get pattern to avoid resubmitting forms
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_picture = url_for("static", filename="resources/profile_pictures/" + current_user.profile_picture)
    return render_template("account.html", title="Account", profile_picture=profile_picture, form=form)
