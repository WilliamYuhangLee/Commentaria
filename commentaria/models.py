from datetime import datetime

from flask import current_app as app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from commentaria import db, login_manager


# Login Manager user session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Association tables
users_liked_posts = db.Table("users_liked_posts", db.metadata,
                             db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
                             db.Column("post_id", db.Integer, db.ForeignKey("posts.id")))


# Database models
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture = db.Column(db.String(40), nullable=False, default="default_profile_picture.png")
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)
    liked_posts = db.relationship("Post", secondary=users_liked_posts, back_populates="liked_users")

    def get_reset_token(self, expire_sec=1800):
        """Return a token for users to reset their passwords that will expire after the set number of seconds"""
        s = Serializer(app.config["SECRET_KEY"], expire_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.profile_picture}')"


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    liked_users = db.relationship("User", secondary=users_liked_posts, back_populates="liked_posts")

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

