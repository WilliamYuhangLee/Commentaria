import os, secrets

from PIL import Image

from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required

from commentaria import app, db, bcrypt
from commentaria.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreatePostForm, EditPostForm
from commentaria.models import User, Post


# Local parameters for use
APP_NAME = app.config["APP_NAME"]


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get("page", default=1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
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
    return render_template("registration.html", title="Join " + APP_NAME, form=form)


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
    return render_template("login.html", title="Sign in to " + APP_NAME, form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


def update_profile_picture(form_picture):

    random_hex = secrets.token_hex(8)  # Randomize picture filename
    _, file_extension = os.path.splitext(form_picture.filename)  # Extract picture file type
    filename = random_hex + file_extension  # Join filename with file type
    file_path = os.path.join(app.root_path, "static/resources/profile_pictures", filename)  # Get path

    output_size = (360, 360)  # Compress target size
    i = Image.open(form_picture)
    i.thumbnail(output_size)  # Compress to target size

    i.save(file_path)  # Save to target path
    return filename  # Return saved full filename


def delete_profile_picture(filename):
    if filename != "default_profile_picture.png":
        file_path = os.path.join(app.root_path, "static/resources/profile_pictures", filename)
        os.remove(file_path)


@app.route("/account", methods=["GET", "POST"])
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
        return redirect(url_for("account")) # Post-Redirect-Get pattern to avoid resubmitting forms
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_picture = url_for("static", filename="resources/profile_pictures/" + current_user.profile_picture)
    return render_template("account.html", title="Account", profile_picture=profile_picture, form=form)


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f"You have successfully posted to {APP_NAME}!", category="success")
        return redirect(url_for("home"))
    return render_template("create_post.html", title="Post to " + APP_NAME, form=form)


@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("view_post.html", title=post.title, post=post)


@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your edit has been saved!", category="success")
        return redirect(url_for("view_post", post_id=post_id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        return render_template("edit_post.html", title="Edit Post", form=form, post_id=post_id)


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been delete!", category="success")
    return redirect(url_for("home"))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template("user_posts.html", posts=posts, user=user)
