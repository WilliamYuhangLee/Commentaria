from flask import Blueprint, render_template, url_for, redirect, flash, request
from flask import current_app
from flask_login import current_user, login_user, logout_user, login_required

from commentaria import db, bcrypt
from commentaria.models import User, Post
from commentaria.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from commentaria.users.utils import update_profile_picture, delete_profile_picture, send_password_reset_email

users = Blueprint("users", __name__)

@users.route("/registration", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Your account has been created! You are now logged in.", category="success")
        return redirect(url_for("main.home"))
    return render_template("registration.html", title="Join " + current_app.config["APP_NAME"], form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")  # check if there is pending request
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for("main.home"))
        else:
            flash("Login failed. Please check your email and password", category="danger")
    return render_template("login.html", title="Sign in to " + current_app.config["APP_NAME"], form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            delete_profile_picture(current_user.profile_picture)
            profile_picture_file = update_profile_picture(form.profile_picture.data)
            current_user.profile_picture = profile_picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account info has been updated!", category="success")
        return redirect(url_for("users.account"))  # Post-Redirect-Get pattern to avoid resubmitting forms
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_picture = url_for("static", filename="resources/profile_pictures/" + current_user.profile_picture)
    return render_template("account.html", title="Account", profile_picture=profile_picture, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=5)
    return render_template("user_posts.html", posts=posts, user=user)


@users.route("/reset_password", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_password_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", category="info")
        return redirect(url_for("users.login"))
    return render_template("reset_password_request.html", title="Reset Password", form=form)


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("The token is invalid or expired.", category="Warning")
        return redirect(url_for("users.reset_password_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated! Try log in with the new password.", category="success")
        return redirect(url_for("users.login"))
    return render_template("reset_password_token.html", title="Reset Password", form=form)
