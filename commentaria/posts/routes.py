from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask import current_app as app
from flask_login import current_user, login_required

from commentaria import db
from commentaria.models import Post
from commentaria.posts.forms import CreatePostForm, EditPostForm

posts = Blueprint("posts", __name__)


@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f"You have successfully posted to {app.config['APP_NAME']}!", category="success")
        return redirect(url_for("main.home"))
    return render_template("create_post.html", title="Post to " + app.config["APP_NAME"], form=form)


@posts.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("view_post.html", title=post.title, post=post)


@posts.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
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
        return redirect(url_for("posts.view_post", post_id=post_id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        return render_template("edit_post.html", title="Edit Post", form=form, post_id=post_id)


@posts.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been delete!", category="success")
    return redirect(url_for("main.home"))
